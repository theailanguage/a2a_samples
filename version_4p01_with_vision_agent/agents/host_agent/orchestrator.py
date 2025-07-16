# =============================================================================
# agents/host_agent/orchestrator.py
# =============================================================================
# 🎯 Purpose:
# Defines the OrchestratorAgent, which:
#   1) Discovers and calls other A2A agents (via DiscoveryClient & AgentConnector)
#   2) Discovers and loads MCP tools (via MCPConnector)
#   3) Exposes each A2A action and each MCP tool as its own callable tool
# Also defines OrchestratorTaskManager to serve this agent over JSON-RPC.
# =============================================================================

import uuid                            # For generating unique session identifiers
import logging                         # For writing log messages to console or file
import asyncio                         # For running asynchronous tasks from synchronous code
from dotenv import load_dotenv         # To load environment variables from a .env file

# Load environment variables from .env (e.g., GOOGLE_API_KEY)
load_dotenv()

# -----------------------------------------------------------------------------
# Google ADK / Gemini imports: classes and functions to build and run LLM agents
# -----------------------------------------------------------------------------
from google.adk.agents.llm_agent import LlmAgent                # Main LLM agent class
from google.adk.sessions import InMemorySessionService          # Simple in-memory session storage
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService  # In-memory memory storage
from google.adk.artifacts import InMemoryArtifactService        # In-memory artifact storage (files, binaries)
from google.adk.runners import Runner                           # Coordinates LLM, sessions, memory, and tools
from google.adk.agents.readonly_context import ReadonlyContext  # Provides read-only context to system prompts
from google.adk.tools.tool_context import ToolContext           # Carries state between tool invocations
from google.adk.tools.function_tool import FunctionTool         # Wraps a Python function as a callable LLM tool
from google.genai import types                                 # For wrapping user messages into LLM-friendly format

# -----------------------------------------------------------------------------
# A2A infrastructure imports: task manager and message models for JSON-RPC
# -----------------------------------------------------------------------------
from server.task_manager import InMemoryTaskManager               # Base class for task storage and locking
from models.request import SendTaskRequest, SendTaskResponse      # JSON-RPC request/response models
from models.task import Message, TaskStatus, TaskState, TextPart   # Task, message, and status data models

# -----------------------------------------------------------------------------
# A2A discovery & connector imports: to find and call remote A2A agents
# -----------------------------------------------------------------------------
from utilities.a2a.agent_discovery import DiscoveryClient        # Finds agent URLs from registry file
from utilities.a2a.agent_connect import AgentConnector          # Sends tasks to remote A2A agents

# -----------------------------------------------------------------------------
# MCP connector import: to discover and call MCP servers/tools
# -----------------------------------------------------------------------------
from utilities.mcp.mcp_connect import MCPConnector              # Connects to MCP servers and lists tools

# Import AgentCard model for typing
from models.agent import AgentCard                              # Metadata structure describing an agent

# -----------------------------------------------------------------------------
# Logging setup: configure root logger to show INFO and above
# -----------------------------------------------------------------------------
logger = logging.getLogger(__name__)                           # Create a logger for this module
logging.basicConfig(level=logging.INFO)                        # Show INFO-level logs in the console


class OrchestratorAgent:
    """
    🤖 OrchestratorAgent:
      - Discovers A2A agents via DiscoveryClient → list of AgentCards
      - Connects to each A2A agent with AgentConnector
      - Discovers MCP servers via MCPConnector and loads MCP tools
      - Exposes each A2A action and each MCP tool as its own callable tool
      - Routes user queries by picking and invoking the correct tool
    """
    
    # Specify supported MIME types for input/output (we only handle plain text)
    SUPPORTED_CONTENT_TYPES = ["text", "text/plain"]

    def __init__(self, agent_cards: list[AgentCard]):
        """
        Initialize the orchestrator with discovered A2A agents and MCP tools.

        Args:
            agent_cards (list[AgentCard]): Metadata for each A2A child agent.
        """
        # 1) Build connectors for each A2A agent
        self.connectors = {}
        self.agent_cards = agent_cards                                  # Dict mapping agent name → AgentConnector
        for card in agent_cards:
            # Create a connector to send tasks to this agent's URL
            self.connectors[card.name] = AgentConnector(card.name, card.url)
            logger.info(f"Registered A2A connector for: {card.name}")

        # 2) Load all MCP tools once at startup
        self.mcp = MCPConnector()                              # Reads mcp_config.json internally
        mcp_tools = self.mcp.get_tools()                       # Retrieve list of MCPTool instances
        logger.info(f"Loaded {len(mcp_tools)} MCP tools")

        # 3) Wrap each MCPTool.run into a simple async function for ADK
        self._mcp_wrappers = []                                # List of FunctionTool instances
        
        def make_wrapper(tool):                                # Factory creates a wrapper for a given MCPTool
            # Define an async function that accepts a single dict of args
            async def wrapper(args: dict) -> str:
                # Call the tool's run() to execute MCP command
                return await tool.run(args)
            # Name the wrapper so ADK can refer to it by the tool's name
            wrapper.__name__ = tool.name
            # updated (13/Jun/25) also add the tool description so the agent can read it
            wrapper.__doc__ = tool.description or f"Tool wrapper for MCP tool: {tool.name}"
            return wrapper

        # Create and register a FunctionTool for each MCP tool
        for tool in mcp_tools:
            fn = make_wrapper(tool)                            # Build the async stub
            self._mcp_wrappers.append(FunctionTool(fn))        # Wrap stub as an ADK tool
            logger.info(f"Wrapped MCP tool for LLM: {tool.name}")

        # 4) Build the Gemini LLM agent and its Runner
        self._agent = self._build_agent()                      # Assemble LlmAgent with tools
        self._user_id = "orchestrator_user"                   # Fixed user ID for session tracking
        self._runner = Runner(
            app_name=self._agent.name,                         # Name of this agent
            agent=self._agent,                                 # LLM agent object
            artifact_service=InMemoryArtifactService(),        # In-memory artifact handler
            session_service=InMemorySessionService(),          # In-memory session storage
            memory_service=InMemoryMemoryService(),            # In-memory conversation memory
        )

    def _build_agent(self) -> LlmAgent:
        """
        Construct the Gemini LLM agent with all available tools.

        Returns:
            LlmAgent: Configured ADK agent ready to run.
        """
        # Gather A2A and MCP tools into one list
        tools = [
            self._list_agents,    # Function listing child A2A agents
            self._delegate_task,  # Async function for routing to A2A agents
            *self._mcp_wrappers    # Unpack all MCP tool wrappers
        ]
        # Create and return the LlmAgent
        return LlmAgent(
            # model="gemini-1.5-flash-latest",                 # Gemini model variant
            model="gemini-2.5-flash",
            name="orchestrator_agent",                        # Unique name for this agent
            description="Routes requests to A2A agents or MCP tools.",
            instruction=self._root_instruction,                  # System prompt callback
            tools=tools,                                        # List of tool functions
        )

    def _root_instruction(self, context: ReadonlyContext) -> str:
        """
        System prompt generator: instructs the LLM how to use available tools.

        Args:
            context (ReadonlyContext): Read-only context (unused here).
        """
        return (
            "You are an orchestrator with two tool categories:\n"
            "1) A2A agent tools: list_agents(), delegate_task(agent_name, message)\n"
            "2) MCP tools: one FunctionTool per tool name\n"
            "Pick exactly the right tool by its name and call it with correct args. Do NOT hallucinate."
        )

    def _list_agents(self) -> list[str]:
        """
        A2A tool: returns a detailed list of registered agents with their skills.

        Format per agent:
        "<Agent Name>: <Agent Description> | Skill 1: <Skill Description> | Skill 2: <Skill Description> ..."
        
        Returns:
            list[str]: Agent summaries.
        """
        summaries = []
        for card in self.connectors.keys():
            # Find the matching AgentCard
            connector = self.connectors[card]
            agent_card = next((c for c in self.agent_cards if c.name == card), None)
            if not agent_card:
                continue

            parts = [f"{agent_card.name}: {agent_card.description.strip()}"]
            for skill in agent_card.skills:
                skill_summary = f"{skill.name}: {skill.description.strip() if skill.description else 'No description'}"
                parts.append(skill_summary)
            
            summaries.append(" | ".join(parts))
        
        return summaries

    async def _delegate_task(
        self,
        agent_name: str,
        message: str,
        tool_context: ToolContext
    ) -> str:
        """
        A2A tool: forwards a message to a child agent and returns its reply.

        Args:
            agent_name (str): Name of the target agent.
            message (str): The user message to send.
            tool_context (ToolContext): Holds state across invocations (e.g., session ID).

        Returns:
            str: The text of the agent's reply, or empty string on failure.
        """
        # Ensure the agent exists
        if agent_name not in self.connectors:
            raise ValueError(f"Unknown agent: {agent_name}")
        # Persist or create a session_id between calls
        state = tool_context.state
        if "session_id" not in state:
            state["session_id"] = str(uuid.uuid4())
        session_id = state["session_id"]
        # Send the task and await its completion
        task = await self.connectors[agent_name].send_task(message, session_id)
        # Extract the last history entry if present
        if task.history and len(task.history) > 1:
            return task.history[-1].parts[0].text
        return ""

    async def invoke(self, query: str, session_id: str) -> str:
        """
        Primary entrypoint: handles a user query.

        Steps:
          1) Create or retrieve a session
          2) Wrap query into LLM Content format
          3) Run the Runner (may invoke tools)
          4) Return the final text output
        Note - function updated 28 May 2025
        Summary of changes:
        1. Agent's invoke method is made async
        2. All async calls (get_session, create_session, run_async) 
            are awaited inside invoke method
        3. task manager's on_send_task updated to await the invoke call

        Reason - get_session and create_session are async in the 
        "Current" Google ADK version and were synchronous earlier 
        when this lecture was recorded. This is due to a recent change 
        in the Google ADK code 
        https://github.com/google/adk-python/commit/1804ca39a678433293158ec066d44c30eeb8e23b

        """
        # 1) Get or create a session for this user and session_id
        session = await self._runner.session_service.get_session(
            app_name=self._agent.name,
            user_id=self._user_id,
            session_id=session_id
        )
        if session is None:
            session = await self._runner.session_service.create_session(
                app_name=self._agent.name,
                user_id=self._user_id,
                session_id=session_id,
                state={}
            )
        # 2) Wrap user text into Content object for Gemini
        content = types.Content(
            role="user",
            parts=[types.Part.from_text(text=query)]
        )
        # 🚀 Run the agent using the Runner and collect the last event
        last_event = None
        async for event in self._runner.run_async(
            user_id=self._user_id,
            session_id=session.id,
            new_message=content
        ):
            last_event = event

        # 🧹 Fallback: return empty string if something went wrong
        if not last_event or not last_event.content or not last_event.content.parts:
            return ""

        # 📤 Extract and join all text responses into one string
        return "\n".join([p.text for p in last_event.content.parts if p.text])


class OrchestratorTaskManager(InMemoryTaskManager):
    """
    TaskManager wrapper: exposes OrchestratorAgent.invoke()
    over the `tasks/send` JSON-RPC endpoint.
    """
    def __init__(self, agent: OrchestratorAgent):
        super().__init__()             # Initialize in-memory store and lock
        self.agent = agent             # Store reference to orchestrator logic

    def _get_user_text(self, request: SendTaskRequest) -> str:
        """
        Helper: extract raw user text from JSON-RPC request.

        Args:
            request (SendTaskRequest): Incoming RPC request.

        Returns:
            str: The text from the request payload.
        """
        return request.params.message.parts[0].text

    async def on_send_task(self, request: SendTaskRequest) -> SendTaskResponse:
        """
        Handle `tasks/send` calls:
          1) Store incoming message in memory
          2) Invoke the orchestrator to get a reply
          3) Append the reply, mark task COMPLETED
          4) Return the full Task in the response
        """
        logger.info(f"OrchestratorTaskManager received task {request.params.id}")
        # Store or update the task record
        task = await self.upsert_task(request.params)
        # Extract the text and invoke orchestration logic
        user_text = self._get_user_text(request)
        reply_text = await self.agent.invoke(user_text, request.params.sessionId)
        # Wrap reply in a Message object
        msg = Message(role="agent", parts=[TextPart(text=reply_text)])
        # Safely append reply and update status under lock
        async with self.lock:
            task.status = TaskStatus(state=TaskState.COMPLETED)
            task.history.append(msg)
        # Return the RPC response including the updated task
        return SendTaskResponse(id=request.id, result=task)

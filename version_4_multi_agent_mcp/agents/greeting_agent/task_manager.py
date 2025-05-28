# agents/greeting_agent/task_manager.py
# =============================================================================
# 🎯 Purpose:
# Connects the GreetingAgent class to the Agent-to-Agent (A2A) protocol by
# handling incoming JSON-RPC "tasks/send" requests. It:
# 1. Receives a SendTaskRequest model
# 2. Stores the user message in memory
# 3. Calls GreetingAgent.invoke() to asynchronously generate a greeting
# 4. Updates the task status and appends the greeting to task history
# 5. Returns a SendTaskResponse containing the completed Task
# =============================================================================

# -----------------------------------------------------------------------------
# 📦 Imports
# -----------------------------------------------------------------------------
import logging                            # Python's built-in logging module

# InMemoryTaskManager provides an in-memory store and locking for tasks
from server.task_manager import InMemoryTaskManager

# Data models for handling A2A JSON-RPC requests/responses and task structures
from models.request import SendTaskRequest, SendTaskResponse
from models.task import Message, TaskStatus, TaskState, TextPart

# The core business logic: GreetingAgent with an async invoke() method
from agents.greeting_agent.agent import GreetingAgent

# -----------------------------------------------------------------------------
# 🪵 Logger setup
# -----------------------------------------------------------------------------
# Create a logger specific to this module using its __name__
logger = logging.getLogger(__name__)


class GreetingTaskManager(InMemoryTaskManager):
    """
    🧩 TaskManager for GreetingAgent:

    - Inherits storage, upsert_task, and locking from InMemoryTaskManager
    - Overrides on_send_task() to:
      * save the incoming message
      * call the GreetingAgent.invoke() to craft a greeting
      * update the task status and history
      * wrap and return the result as SendTaskResponse

    Note:
    - GreetingAgent.invoke() is asynchronous, but on_send_task()
      itself is also defined as async, so we await internal calls.
    """
    def __init__(self, agent: GreetingAgent):
        """
        Initialize the TaskManager with a GreetingAgent instance.

        Args:
            agent (GreetingAgent): The core logic handler that knows how to
                                   produce a greeting.
        """
        # Call the parent constructor to set up self.tasks and self.lock
        super().__init__()
        # Store a reference to our GreetingAgent for later use
        self.agent = agent

    def _get_user_text(self, request: SendTaskRequest) -> str:
        """
        Extract the raw user text from the incoming SendTaskRequest.

        Args:
            request (SendTaskRequest): The incoming JSON-RPC request
                                       containing a TaskSendParams object.

        Returns:
            str: The text content the user sent (first TextPart).
        """
        # The request.params.message.parts is a list of TextPart objects.
        # We take the first element's .text attribute.
        return request.params.message.parts[0].text

    async def on_send_task(self, request: SendTaskRequest) -> SendTaskResponse:
        """
        Handle a new greeting task:

        1. Store the incoming user message in memory (or update existing task)
        2. Extract the user's text for processing
        3. Call GreetingAgent.invoke() to generate the greeting
        4. Wrap that greeting string in a Message/TextPart
        5. Update the Task status to COMPLETED and append the reply
        6. Return a SendTaskResponse containing the updated Task

        Args:
            request (SendTaskRequest): The JSON-RPC request with TaskSendParams

        Returns:
            SendTaskResponse: A JSON-RPC response with the completed Task
        """
        # Log receipt of a new task along with its ID
        logger.info(f"GreetingTaskManager received task {request.params.id}")

        # Step 1: Save or update the task in memory.
        # upsert_task() will create a new Task if it doesn't exist,
        # or append the incoming user message to existing history.
        task = await self.upsert_task(request.params)

        # Step 2: Extract the actual text the user sent
        user_text = self._get_user_text(request)

        # Step 3: Call the GreetingAgent to generate a greeting text.
        # Since GreetingAgent.invoke() might be an async function,
        # await it to get the returned string.
        greeting_text = await self.agent.invoke(
            user_text,
            request.params.sessionId
        )

        # Step 4: Wrap the greeting string in a TextPart, then in a Message
        reply_message = Message(
            role="agent",               # Mark this as an "agent" response
            parts=[TextPart(text=greeting_text)]  # The agent's reply text
        )

        # Step 5: Update the task status to COMPLETED and append our reply
        # Use the lock to avoid race conditions with other coroutines.
        async with self.lock:
            # Mark the task as done
            task.status = TaskStatus(state=TaskState.COMPLETED)
            # Add the agent's reply to the task's history
            task.history.append(reply_message)

        # Step 6: Return a SendTaskResponse, containing the JSON-RPC id
        # (mirroring the request.id) and the updated Task model.
        return SendTaskResponse(id=request.id, result=task)

# =============================================================================
# agents/greeting_agent/__main__.py
# =============================================================================
# 🎯 Purpose:
# Starts the GreetingAgent as an Agent-to-Agent (A2A) server.
# - Defines the agent’s metadata (AgentCard)
# - Wraps the GreetingAgent logic in a GreetingTaskManager
# - Listens for incoming tasks on a configurable host and port
# =============================================================================

import logging                        # Standard Python module for logging
import click                          # Library for building command-line interfaces

from server.server import A2AServer    # Our generic A2A server implementation
from models.agent import (
    AgentCard,                        # Pydantic model for describing an agent
    AgentCapabilities,                # Describes streaming & other features
    AgentSkill                       # Describes a specific skill the agent offers
)
from agents.greeting_agent.task_manager import GreetingTaskManager
                                      # TaskManager that adapts GreetingAgent to A2A
from agents.greeting_agent.agent import GreetingAgent
                                      # Our custom orchestration agent logic

# -----------------------------------------------------------------------------
# ⚙️ Logging setup
# -----------------------------------------------------------------------------
# Configure the root logger to print INFO-level messages to the console.
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# __name__ resolves to "agents.greeting_agent.__main__",
# so this logger’s output will be prefixed accordingly.

# -----------------------------------------------------------------------------
# ✨ CLI Entrypoint
# -----------------------------------------------------------------------------
@click.command()                     # Decorator: makes `main` a CLI command
@click.option(
    "--host",                        # CLI flag name
    default="localhost",             # Default value if flag not provided
    help="Host to bind GreetingAgent server to"  # Help text for `--help`
)
@click.option(
    "--port",
    default=10001,
    help="Port for GreetingAgent server"
)
def main(host: str, port: int):
    """
    Launches the GreetingAgent A2A server.

    Args:
        host (str): Hostname or IP to bind to (default: localhost)
        port (int): TCP port to listen on (default: 10001)
    """
    # Print a friendly banner so the user knows the server is starting
    print(f"\n🚀 Starting GreetingAgent on http://{host}:{port}/\n")

    # -------------------------------------------------------------------------
    # 1) Define the agent’s capabilities
    # -------------------------------------------------------------------------
    # Here we specify that this agent does NOT support streaming responses.
    # It will always send a single, complete reply.
    capabilities = AgentCapabilities(streaming=False)

    # -------------------------------------------------------------------------
    # 2) Define the agent’s skill metadata
    # -------------------------------------------------------------------------
    # An AgentSkill describes:
    # - id: unique identifier for the skill
    # - name: human-readable name
    # - description: what this skill does
    # - tags: keywords for discovery or categorization
    # - examples: sample user inputs to illustrate the skill
    skill = AgentSkill(
        id="greet",                                        # Unique skill ID
        name="Greeting Tool",                              # Friendly name
        description="Returns a greeting based on the current time of day",
        tags=["greeting", "time", "hello"],                # Searchable tags
        examples=["Greet me", "Say hello based on time"]   # Example prompts
    )

    # -------------------------------------------------------------------------
    # 3) Compose the AgentCard for discovery
    # -------------------------------------------------------------------------
    # AgentCard is the JSON metadata that other clients/agents fetch
    # from "/.well-known/agent.json". It describes:
    # - name, description, URL, version
    # - supported input/output modes
    # - capabilities and skills
    agent_card = AgentCard(
        name="GreetingAgent",                              # Agent identifier
        description="Agent that greets you based on the current time",
        url=f"http://{host}:{port}/",                      # Base URL for discovery
        version="1.0.0",                                   # Semantic version
        defaultInputModes=["text"],                        # Accepts plain text
        defaultOutputModes=["text"],                       # Produces plain text
        capabilities=capabilities,                         # Streaming disabled
        skills=[skill]                                     # List of skills
    )

    # -------------------------------------------------------------------------
    # 4) Instantiate the core logic and its TaskManager
    # -------------------------------------------------------------------------
    # GreetingAgent contains the orchestration logic (LLM + tools).
    greeting_agent = GreetingAgent()
    # GreetingTaskManager adapts that logic to the A2A JSON-RPC protocol.
    task_manager = GreetingTaskManager(agent=greeting_agent)

    # -------------------------------------------------------------------------
    # 5) Create and start the A2A server
    # -------------------------------------------------------------------------
    # A2AServer wires up:
    # - HTTP routes (POST "/" for tasks, GET "/.well-known/agent.json" for discovery)
    # - our AgentCard metadata
    # - the TaskManager that handles incoming requests
    server = A2AServer(
        host=host,
        port=port,
        agent_card=agent_card,
        task_manager=task_manager
    )
    server.start()  # Blocks here, serving requests until the process is killed


# -----------------------------------------------------------------------------
# Entrypoint guard
# -----------------------------------------------------------------------------
# Ensures `main()` only runs when this script is executed directly,
# not when it’s imported as a module.
if __name__ == "__main__":
    main()
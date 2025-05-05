# =============================================================================
# agents/host_agent/entry.py
# =============================================================================
# 🎯 Purpose:
# Boots up the OrchestratorAgent as an A2A server.
# Uses the shared registry file to discover all child agents,
# then delegates routing to the OrchestratorAgent via A2A JSON-RPC.
# =============================================================================

import asyncio                              # Built-in for running async coroutines
import logging                              # Standard Python logging module
import click                                # Library for building CLI interfaces

# Utility for discovering remote A2A agents from a local registry
from utilities.discovery import DiscoveryClient
# Shared A2A server implementation (Starlette + JSON-RPC)
from server.server import A2AServer
# Pydantic models for defining agent metadata (AgentCard, etc.)
from models.agent import AgentCard, AgentCapabilities, AgentSkill
# Orchestrator implementation and its task manager
from agents.host_agent.orchestrator import (
    OrchestratorAgent,
    OrchestratorTaskManager
)

# Configure root logger to show INFO-level messages
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@click.command()
@click.option(
    "--host", default="localhost",
    help="Host to bind the OrchestratorAgent server to"
)
@click.option(
    "--port", default=10002,
    help="Port for the OrchestratorAgent server"
)
@click.option(
    "--registry",
    default=None,
    help=(
        "Path to JSON file listing child-agent URLs. "
        "Defaults to utilities/agent_registry.json"
    )
)
def main(host: str, port: int, registry: str):
    """
    Entry point to start the OrchestratorAgent A2A server.

    Steps performed:
    1. Load child-agent URLs from the registry JSON file.
    2. Fetch each agent's metadata via `/.well-known/agent.json`.
    3. Instantiate an OrchestratorAgent with discovered AgentCards.
    4. Wrap it in an OrchestratorTaskManager for JSON-RPC handling.
    5. Launch the A2AServer to listen for incoming tasks.
    """
    # 1) Discover all registered child agents from the registry file
    discovery = DiscoveryClient(registry_file=registry)
    # Run the async discovery synchronously at startup
    agent_cards = asyncio.run(discovery.list_agent_cards())

    # Warn if no agents are found in the registry
    if not agent_cards:
        logger.warning(
            "No agents found in registry – the orchestrator will have nothing to call"
        )

    # 2) Define the OrchestratorAgent's own metadata for discovery
    capabilities = AgentCapabilities(streaming=False)
    skill = AgentSkill(
        id="orchestrate",                          # Unique skill identifier
        name="Orchestrate Tasks",                  # Human-friendly name
        description=(
            "Routes user requests to the appropriate child agent, "
            "based on intent (time, greeting, etc.)"
        ),
        tags=["routing", "orchestration"],       # Keywords to aid discovery
        examples=[                                  # Sample user queries
            "What is the time?",
            "Greet me",
            "Say hello based on time"
        ]
    )
    orchestrator_card = AgentCard(
        name="OrchestratorAgent",
        description="Delegates tasks to discovered child agents",
        url=f"http://{host}:{port}/",             # Public endpoint
        version="1.0.0",
        defaultInputModes=["text"],                # Supported input modes
        defaultOutputModes=["text"],               # Supported output modes
        capabilities=capabilities,
        skills=[skill]
    )

    # 3) Instantiate the OrchestratorAgent and its TaskManager
    orchestrator = OrchestratorAgent(agent_cards=agent_cards)
    task_manager = OrchestratorTaskManager(agent=orchestrator)

    # 4) Create and start the A2A server
    server = A2AServer(
        host=host,
        port=port,
        agent_card=orchestrator_card,
        task_manager=task_manager
    )
    server.start()


if __name__ == "__main__":
    main()

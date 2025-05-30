# =============================================================================
# agents/host_agent/entry.py
# =============================================================================
# 🎯 Purpose:
#   Boots up the OrchestratorAgent as an A2A server.
#   Uses DiscoveryClient to load child A2A agent cards,
#   then delegates routing (and MCP tools) to the OrchestratorAgent.
# =============================================================================

import asyncio                              # Provides tools for working with asynchronous code
import logging                              # Standard Python module for logging messages (info, warning, errors)
import click                                # Third-party library for building command-line interfaces (CLI)

# UPDATED: import the renamed discovery class
from utilities.a2a.agent_discovery import DiscoveryClient  # Utility to discover other A2A agents via a JSON registry
from server.server import A2AServer           # The core A2A server implementation (Starlette + JSON-RPC)
from models.agent import AgentCard, AgentCapabilities, AgentSkill  # Pydantic models describing agent metadata
from agents.host_agent.orchestrator import (
    OrchestratorAgent,                        # The in-process orchestrator logic (routes tasks)
    OrchestratorTaskManager                   # Exposes the orchestrator over JSON-RPC
)

# Configure the root logger to display INFO-level and above messages
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)          # Create a logger instance specific to this module


@click.command()                              # Declare this function as a CLI command entrypoint
@click.option(
    "--host", default="localhost",
    help="Bind address for host agent"    # Description for the --host CLI flag
)
@click.option(
    "--port", default=10000,
    help="Port for host agent"            # Description for the --port CLI flag
)
@click.option(
    "--registry", default=None,
    help=(
        "Path to A2A registry JSON. "        
        "Defaults to utilities/a2a/agent_registry.json"
    )
)
def main(host: str, port: int, registry: str):
    """
    Starts the OrchestratorAgent A2A server.

    Steps:
    1) Load child A2A AgentCards via DiscoveryClient
    2) Instantiate OrchestratorAgent (with A2A connectors & MCP tools)
    3) Wrap it in OrchestratorTaskManager
    4) Launch the JSON-RPC server
    """
    # 1) Discover child A2A agents from the registry file or default location
    discovery = DiscoveryClient(registry_file=registry)
    # list_agent_cards() is async, so we run it via asyncio.run to get the result synchronously
    agent_cards = asyncio.run(discovery.list_agent_cards())

    # If no agents are found, warn the user (the orchestrator will have no downstream targets)
    if not agent_cards:
        logger.warning(
            "No A2A agents found – the orchestrator will have nothing to call"
        )

    # 2) Define this host agent’s own metadata for discovery by other clients
    capabilities = AgentCapabilities(streaming=False)  # Indicates this agent does not support streaming
    skill = AgentSkill(
        id="orchestrate",                          # Unique internal identifier for the skill
        name="Orchestrate Tasks",                  # Human-friendly name shown in UIs
        description=(
            "Routes user requests to child A2A agents or MCP tools based on intent."
        ),
        tags=["routing", "orchestration"],        # Keywords to help clients discover this skill
        examples=[                                  # Sample queries to illustrate usage
            "What is the time?",
            "Greet me",
            "Search the latest funding news for Acme Corp",
        ]
    )
    # Build the AgentCard, which is served at /.well-known/agent.json
    orchestrator_card = AgentCard(
        name="OrchestratorAgent",                # Unique agent name
        description="Delegates to TellTimeAgent, GreetingAgent, and MCP tools",
        url=f"http://{host}:{port}/",            # Public endpoint where this agent listens
        version="1.0.0",                         # Semantic version of this agent
        defaultInputModes=["text"],              # Supported input modes
        defaultOutputModes=["text"],             # Supported output modes
        capabilities=capabilities,                 # Streaming capabilities
        skills=[skill]                             # Which skills this agent provides
    )

    # 3) Instantiate the orchestrator logic and its JSON-RPC task manager
    orchestrator = OrchestratorAgent(agent_cards=agent_cards)
    task_manager = OrchestratorTaskManager(agent=orchestrator)

    # 4) Construct and launch the A2A server
    server = A2AServer(
        host=host,
        port=port,
        agent_card=orchestrator_card,
        task_manager=task_manager
    )
    server.start()                              # This call blocks, running the server until interrupted


# Standard Python idiom: if this script is run directly, invoke main()
if __name__ == "__main__":
    main()

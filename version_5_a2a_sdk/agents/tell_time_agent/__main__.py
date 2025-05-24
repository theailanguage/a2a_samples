# =============================================================================
# agents/tell_time_agent/main.py
# =============================================================================
# Purpose:
# This file starts the A2A-compatible agent server.
# It sets up environment, configures the task execution handler, agent card,
# and launches a Starlette-based web server for incoming agent tasks.
# =============================================================================

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
import os                      # Provides access to environment variables
import sys                     # Used for exiting if setup is incomplete

import click                   # Helps define command-line interface for running the server
import httpx                   # HTTP client used for async push notifications
from dotenv import load_dotenv  # Loads .env file for environment variables

# Import the agent logic and its executor
from .agent import TellTimeAgent                # Defines the actual agent logic
from .agent_executor import TellTimeAgentExecutor  # Bridges the agent with A2A server

# Import A2A SDK components to create a working agent server
from a2a.server.apps import A2AStarletteApplication  # Main application class based on Starlette
from a2a.server.request_handlers import DefaultRequestHandler  # Default logic for handling tasks
from a2a.server.tasks import InMemoryPushNotifier, InMemoryTaskStore  # In-memory task manager and notifier
from a2a.types import AgentCard, AgentSkill, AgentCapabilities  # Agent metadata definitions

# -----------------------------------------------------------------------------
# Load environment variables from .env file if present
# -----------------------------------------------------------------------------
load_dotenv()

# -----------------------------------------------------------------------------
# Main entry point to launch the agent server
# -----------------------------------------------------------------------------
@click.command()
@click.option('--host', 'host', default='localhost')     # Host where the agent will listen (default: localhost)
@click.option('--port', 'port', default=10000)            # Port where the agent will listen (default: 10000)
def main(host: str, port: int):
    # Check if the required API key is set in environment
    if not os.getenv('GOOGLE_API_KEY'):
        print("GOOGLE_API_KEY environment variable not set.")
        sys.exit(1)  # Exit the program if API key is missing

    # Create HTTP client (used for push notifications)
    client = httpx.AsyncClient()

    # Set up the request handler for processing incoming tasks
    handler = DefaultRequestHandler(
        agent_executor=TellTimeAgentExecutor(),  # Hook in our custom agent
        task_store=InMemoryTaskStore(),          # Use in-memory store to manage task state
        push_notifier=InMemoryPushNotifier(client),  # Enable server push updates (e.g., via webhook)
    )

    # Set up the A2A server application using agent card and handler
    server = A2AStarletteApplication(
        agent_card=build_agent_card(host, port),  # Provide agent capabilities and skills
        http_handler=handler,                     # Attach the request handler
    )

    # Start the server using uvicorn async server
    import uvicorn
    uvicorn.run(server.build(), host=host, port=port)

# -----------------------------------------------------------------------------
# Defines the metadata card for this agent
# -----------------------------------------------------------------------------
def build_agent_card(host: str, port: int) -> AgentCard:
    return AgentCard(
        name="TellTime Agent",                                      # Human-readable name of the agent
        description="Tells the current system time.",               # Short description
        url=f"http://{host}:{port}/",                               # Full URL where the agent is reachable
        version="1.0.0",                                            # Version of the agent
        capabilities=AgentCapabilities(streaming=True, pushNotifications=True),  # Supported features
        defaultInputModes=TellTimeAgent.SUPPORTED_CONTENT_TYPES,    # Accepted input content types
        defaultOutputModes=TellTimeAgent.SUPPORTED_CONTENT_TYPES,   # Returned output content types
        skills=[                                                     # Skills this agent supports (currently one)
            AgentSkill(
                id="tell_time",                                     # Unique ID for the skill
                name="Get Current Time",                           # Display name
                description="Tells the current system time in HH:MM:SS format.",
                tags=["time", "clock"],                             # Useful tags for search/filtering
                examples=["What time is it?", "Tell me the current time."],  # Example user prompts
            )
        ],
    )

# -----------------------------------------------------------------------------
# This ensures the server starts when you run `python -m agents.tell_time_agent.main`
# -----------------------------------------------------------------------------
if __name__ == '__main__':
    main()

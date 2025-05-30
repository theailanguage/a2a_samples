# =============================================================================
# agents/google_adk/__main__.py
# =============================================================================
# Purpose:
# This script launches a Gemini Vision agent as an A2A-compatible server.
# When run, it sets up the agent, defines its metadata, starts the server,
# and listens for tasks (like image-based queries from other agents or users).
# =============================================================================

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

import click  # Used to create command-line interfaces (CLI) easily
import logging  # Python's built-in module to show logs like "INFO", "ERROR", etc.

# Import the A2A server class from your backend framework
# This handles HTTP server setup and routing
from server.server import A2AServer

# Import the data model that describes the agent to the outside world
# - AgentCard: metadata like name, description, capabilities
# - AgentCapabilities: flags like "supports streaming"
# - AgentSkill: describes what the agent can do (e.g., "describe images")
from models.agent import AgentCard, AgentCapabilities, AgentSkill

# Import your custom Gemini Vision agent implementation
from agents.vision_agent.agent import GeminiVisionAgent

# Import the task manager which connects tasks to your agent logic
from agents.vision_agent.task_manager import AgentTaskManager

# -----------------------------------------------------------------------------
# Logging Setup
# -----------------------------------------------------------------------------

# Configure logging so that important events are printed to the console
logging.basicConfig(level=logging.INFO)  # Set log level to show INFO and above
logger = logging.getLogger(__name__)  # Create a logger for this module

# -----------------------------------------------------------------------------
# CLI Entry Point
# -----------------------------------------------------------------------------

# Define command-line options using Click
@click.command()  # Marks this function as a CLI command
@click.option("--host", default="localhost", help="Host to bind the server to")
# --host specifies where the server should run (localhost = only this machine)

@click.option("--port", default=10003, help="Port number for the server")
# --port specifies what port to listen on (10003 is the default)
def main(host, port):
    """
    Starts the Gemini Vision A2A agent server.
    """

    # -----------------------------------------------------------------------------
    # Define what this agent can do
    # -----------------------------------------------------------------------------

    # Create a capabilities object — here, we say streaming responses are not supported
    capabilities = AgentCapabilities(streaming=False)

    # Define a skill offered by this agent (this shows up in the directory or when discovered by other agents)
    skill = AgentSkill(
        id="vision_query",  # Unique identifier for the skill
        name="Image Query Tool",  # Human-readable name
        description=(
            "Answer questions about the content of an image. Input must be provided "
            "as a single string in the format:\n"
            "<your question> || <image path or URL>\n"
            "Example: What is shown in this picture? || https://example.com/car.jpg"
        ),
        tags=["image", "vision", "gemini"],  # Searchable tags
        examples=[
            "What is in this image? || https://example.com/dog.jpg",
            "Describe this picture || ./images/photo1.png"
        ]
    )

    # Create the agent card that describes this agent to other agents/systems
    agent_card = AgentCard(
        name="GeminiVisionAgent",  # The name of the agent
        description=(
            "This agent answers questions about images using Gemini Vision.\n\n"
            "Input Format:\n"
            "Provide a single string input in the following format:\n"
            "<your question> || <image path or URL>\n\n"
            "Image Path Support:\n"
            "- For URLs: Provide a direct image link such as:\n"
            "  https://example.com/image.jpg\n"
            "- For Local Files: Provide an absolute or relative file path such as:\n"
            "  ./images/sample.jpg or /home/user/image.png\n\n"
            "Example Input:\n"
            "What is in this image? || https://example.com/cat.jpg\n\n"
            "The agent will load the image from the provided path or URL and answer the query accordingly."
        ),
        url=f"http://{host}:{port}/",  # The public URL of this agent
        version="1.0.0",  # Version of the agent (you can bump this when updating)
        defaultInputModes=GeminiVisionAgent.SUPPORTED_CONTENT_TYPES,
        # Types of inputs supported — from the agent class

        defaultOutputModes=GeminiVisionAgent.SUPPORTED_CONTENT_TYPES,
        # Types of outputs supported — same as input for this agent

        capabilities=capabilities,  # Pass the capability object from above
        skills=[skill]  # List of skills this agent can handle
    )

    # -----------------------------------------------------------------------------
    # Start the Server
    # -----------------------------------------------------------------------------

    # Create the actual A2A server instance
    # Pass in:
    # - host: where the server listens (e.g., "localhost" or "0.0.0.0")
    # - port: port number to use
    # - agent_card: metadata that describes the agent
    # - task_manager: logic for how to process incoming tasks
    server = A2AServer(
        host=host,
        port=port,
        agent_card=agent_card,
        task_manager=AgentTaskManager(agent=GeminiVisionAgent())
    )

    # Start the server — it will now listen for incoming A2A tasks
    server.start()

# -----------------------------------------------------------------------------
# Run the main() function if this file is executed directly
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    main()  # This runs the server with the provided host/port
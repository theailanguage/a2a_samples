# =============================================================================
# utilities/a2a/agent_connect.py
# =============================================================================
# 🎯 Purpose:
# Provides a simple wrapper (`AgentConnector`) around the A2AClient to send tasks
# to any remote agent identified by a base URL. This decouples the Orchestrator
# from low-level HTTP details and HTTP client setup.
# =============================================================================

import uuid                           # Standard library for generating unique IDs
import logging                        # Standard library for configurable logging

# Import our custom A2AClient which handles JSON-RPC task requests
from client.client import A2AClient
# Import Task model to represent the full task response
from models.task import Task

# Create a logger for this module using its namespace
logger = logging.getLogger(__name__)


class AgentConnector:
    """
    🔗 Connects to a remote A2A agent and provides a uniform method to delegate tasks.

    Attributes:
        name (str): Human-readable identifier of the remote agent.
        client (A2AClient): HTTP client pointing at the agent's URL.
    """

    def __init__(self, name: str, base_url: str):
        """
        Initialize the connector for a specific remote agent.

        Args:
            name (str): Identifier for the agent (e.g., "TellTimeAgent").
            base_url (str): The HTTP endpoint (e.g., "http://localhost:10000").
        """
        # Store the agent’s name for logging and reference
        self.name = name
        # Instantiate an A2AClient bound to the agent’s base URL
        self.client = A2AClient(url=base_url)
        # Log that the connector is ready for use
        logger.info(f"AgentConnector: initialized for {self.name} at {base_url}")

    async def send_task(self, message: str, session_id: str) -> Task:
        """
        Send a text task to the remote agent and return its completed Task.

        Args:
            message (str): What you want the agent to do (e.g., "What time is it?").
            session_id (str): Session identifier to group related calls.

        Returns:
            Task: The full Task object (including history) from the remote agent.
        """
        # Generate a unique ID for this task using uuid4, hex form
        task_id = uuid.uuid4().hex
        # Build the JSON-RPC payload matching TaskSendParams schema
        payload = {
            "id": task_id,
            "sessionId": session_id,
            "message": {
                "role": "user",                # Indicates this message is from the user
                "parts": [                       # Wrap the text in a list of parts
                    {"type": "text", "text": message}
                ]
            }
        }

        # Use the A2AClient to send the task asynchronously and await the response
        task_result = await self.client.send_task(payload)
        # Log receipt of the completed task for debugging/tracing
        logger.info(f"AgentConnector: received response from {self.name} for task {task_id}")
        # Return the Task Pydantic model for further processing by the orchestrator
        return task_result

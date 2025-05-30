# =============================================================================
# agents/vision_agent/task_manager.py
# =============================================================================
# 🎯 Purpose:
# Connects the Gemini Vision Agent to the A2A task-handling system.
# Receives a query + file path, invokes the agent, and returns the response.
# =============================================================================

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

import logging  # Python’s built-in module for printing messages to the console

# Import the in-memory task manager from the server module.
# This is the parent class that stores and tracks tasks in RAM.
from server.task_manager import InMemoryTaskManager

# Import the agent class that will handle vision queries.
from agents.vision_agent.agent import GeminiVisionAgent

# Import the request and response types for sending and receiving tasks
from models.request import SendTaskRequest, SendTaskResponse

# Import models used to structure the conversation task:
# - Message: a message sent/received by the agent
# - TaskStatus: status of the task (e.g., completed, in progress)
# - TaskState: enum-like object representing the state itself (e.g., COMPLETED)
# - TextPart: holds the actual text portion of a message
from models.task import Message, TaskStatus, TaskState, TextPart

# Create a logger for this module (good for printing debug info)
logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# AgentTaskManager Class
# -----------------------------------------------------------------------------

class AgentTaskManager(InMemoryTaskManager):
    """
    Connects the Gemini Vision agent to A2A by:
    - Receiving a task
    - Extracting the query and file path
    - Passing to GeminiVisionAgent for processing
    - Returning the structured result
    """

    def __init__(self, agent: GeminiVisionAgent):
        # Call the constructor of the parent (InMemoryTaskManager)
        super().__init__()

        # Save the agent instance so we can call its invoke method later
        self.agent = agent

    def _get_user_query(self, request: SendTaskRequest) -> str:
        """
        Extract the text query input from the request.
        This is where we read what the user typed.

        Args:
            request (SendTaskRequest): The request object coming from another agent

        Returns:
            str: A string like "Describe this || ./path/to/image.jpg"
        """
        # Access the text content inside the request object
        # We assume the message has at least one "part", and it's a text part.
        return request.params.message.parts[0].text

    async def on_send_task(self, request: SendTaskRequest) -> SendTaskResponse:
        """
        The main handler that processes incoming tasks.

        Steps:
        1. Save the task in memory (upsert = update or insert)
        2. Extract the user's query from the request
        3. Call the Gemini agent to process the image and get a response
        4. Wrap the response in a message object
        5. Mark the task as complete and add the message to its history
        6. Return the updated task wrapped in a response object
        """

        # Log that we are processing a new task (for visibility in logs)
        logger.info(f"Processing new task: {request.params.id}")

        # Step 1: Save the task in memory (insert if new, update if exists)
        task = await self.upsert_task(request.params)

        # Step 2: Extract the actual text query from the request
        query = self._get_user_query(request)

        # Step 3: Ask the agent to process the query and image
        # This returns a string like "This is a photo of a dog"
        result_text = await self.agent.invoke(query, request.params.sessionId)

        # Step 4: Format the result into a structured Message object
        agent_message = Message(
            role="agent",  # Who is sending this message? The agent
            parts=[TextPart(text=result_text)]  # The reply content
        )

        # Step 5: Mark the task as completed and append the message to history
        async with self.lock:  # Locking to avoid race conditions
            task.status = TaskStatus(state=TaskState.COMPLETED)  # Mark as done
            task.history.append(agent_message)  # Add the agent's reply

        # Step 6: Wrap and return the final updated task inside a SendTaskResponse
        return SendTaskResponse(id=request.id, result=task)
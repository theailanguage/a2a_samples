# =============================================================================
# agents/google_adk/task_manager.py
# =============================================================================
# 🎯 Purpose:
# This file connects your Gemini-powered agent (TellTimeAgent) to the task-handling system.
# It inherits from InMemoryTaskManager to:
# - Receive a task from the user
# - Extract the question (like "What time is it?")
# - Ask the agent to respond
# - Save and return the agent’s answer
# =============================================================================


# -----------------------------------------------------------------------------
# 📚 Imports
# -----------------------------------------------------------------------------

import logging  # Standard Python module for logging debug/info messages

# 🔁 Import the shared in-memory task manager from the server
from server.task_manager import InMemoryTaskManager

# 🤖 Import the actual agent we're using (Gemini-powered TellTimeAgent)
from agents.tell_time_agent.agent import TellTimeAgent

# 📦 Import data models used to structure and return tasks
from models.request import SendTaskRequest, SendTaskResponse
from models.task import Message, Task, TextPart, TaskStatus, TaskState


# -----------------------------------------------------------------------------
# 🪵 Logger setup
# -----------------------------------------------------------------------------
# This allows us to print nice logs like:
# INFO:agents.google_adk.task_manager:Processing new task: 12345
logger = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# AgentTaskManager
# -----------------------------------------------------------------------------

class AgentTaskManager(InMemoryTaskManager):
    """
    🧠 This class connects the Gemini agent to the task system.

    - It "inherits" all the logic from InMemoryTaskManager
    - It overrides the part where we handle a new task (on_send_task)
    - It uses the Gemini agent to generate a response
    """

    def __init__(self, agent: TellTimeAgent):
        super().__init__()     # Call parent class constructor
        self.agent = agent     # Store the Gemini-based agent as a property

    # -------------------------------------------------------------------------
    # 🔍 Extract the user's query from the incoming task
    # -------------------------------------------------------------------------
    def _get_user_query(self, request: SendTaskRequest) -> str:
        """
        Get the user’s text input from the request object.

        Example: If the user says "what time is it?", we pull that string out.

        Args:
            request: A SendTaskRequest object

        Returns:
            str: The actual text the user asked
        """
        return request.params.message.parts[0].text

    # -------------------------------------------------------------------------
    # 🧠 Main logic to handle and complete a task
    # -------------------------------------------------------------------------
    async def on_send_task(self, request: SendTaskRequest) -> SendTaskResponse:
        """
        This is the heart of the task manager.

        It does the following:
        1. Save the task into memory (or update it)
        2. Ask the Gemini agent for a reply
        3. Format that reply as a message
        4. Save the agent’s reply into the task history
        5. Return the updated task to the caller
        """

        logger.info(f"Processing new task: {request.params.id}")

        # Step 1: Save the task using the base class helper
        task = await self.upsert_task(request.params)

        # Step 2: Get what the user asked
        query = self._get_user_query(request)

        # Step 3: Ask the Gemini agent to respond (synchronous call here)
        result_text = await self.agent.invoke(query, request.params.sessionId)

        # Step 4: Turn the agent's response into a Message object
        agent_message = Message(
            role="agent",                       # The role is "agent" not "user"
            parts=[TextPart(text=result_text)]  # The reply text is stored inside a TextPart
        )

        # Step 5: Update the task state and add the message to history
        async with self.lock:                   # Lock access to avoid concurrent writes
            task.status = TaskStatus(state=TaskState.COMPLETED)  # Mark task as done
            task.history.append(agent_message)  # Append the agent's message to the task history

        # Step 6: Return a structured response back to the A2A client
        return SendTaskResponse(id=request.id, result=task)


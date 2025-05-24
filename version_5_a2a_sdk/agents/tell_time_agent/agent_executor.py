# =============================================================================
# agents/tell_time_agent/agent_executor.py
# =============================================================================
# Purpose:
# This file defines the "executor" that acts as a bridge between the A2A server
# and the underlying TellTime agent. It listens to tasks and dispatches them to
# the agent, then sends back task updates and results through the event queue.
# =============================================================================

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

from .agent import TellTimeAgent  # Imports the TellTimeAgent class from the same directory

# Importing base classes from the A2A SDK to define agent behavior
from a2a.server.agent_execution import AgentExecutor  # Base class for defining agent task executor logic
from a2a.server.agent_execution import RequestContext  # Holds information about the incoming user query and context

# EventQueue is used to push updates back to the A2A server (e.g., task status, results)
from a2a.server.events.event_queue import EventQueue

# Importing event and status types for responding to client
from a2a.types import (
    TaskArtifactUpdateEvent,  # Event for sending result artifacts back to the client
    TaskStatusUpdateEvent,   # Event for sending status updates (e.g., working, completed)
    TaskStatus,              # Object that holds the current status of the task
    TaskState,               # Enum that defines states: working, completed, input_required, etc.
)

# Utility functions to create standardized message and artifact formats
from a2a.utils import (
    new_agent_text_message,  # Creates a message object from agent to client
    new_task,                # Creates a new task object from the initial message
    new_text_artifact        # Creates a textual result artifact
)

# -----------------------------------------------------------------------------
# TellTimeAgentExecutor: Connects the agent logic to A2A server infrastructure
# -----------------------------------------------------------------------------

class TellTimeAgentExecutor(AgentExecutor):  # Define a new executor by extending A2A's AgentExecutor
    """
    This class connects the TellTimeAgent to the A2A server runtime. It implements
    the `execute` function to run tasks and push updates to the event queue.
    """

    def __init__(self):  # Constructor for the executor class
        self.agent = TellTimeAgent()  # Creates an instance of the TellTimeAgent for handling queries

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        # This method is called when a new task is received

        query = context.get_user_input()  # Extracts the actual text of the user's message
        task = context.current_task      # Gets the task object if it already exists

        if not context.message:          # Ensure the message is not missing
            raise Exception('No message provided')  # Raise an error if something's wrong

        if not task:                     # If no existing task, this is a new interaction
            task = new_task(context.message)       # Create a new task based on the message
            event_queue.enqueue_event(task)        # Enqueue the new task to notify the A2A server

        # Use the agent to handle the query via async stream
        async for event in self.agent.stream(query, task.contextId):

            if event['is_task_complete']:  # If the task has been successfully completed
                # Send the result artifact to the A2A server
                event_queue.enqueue_event(
                    TaskArtifactUpdateEvent(
                        taskId=task.id,                 # ID of the task
                        contextId=task.contextId,       # ID of the context (conversation thread)
                        artifact=new_text_artifact(     # The result artifact
                            name='current_result',      # Name of the artifact
                            description='Result of request to agent.',  # Description
                            text=event['content'],      # The actual result text
                        ),
                        append=False,                   # Not appending to previous result
                        lastChunk=True,                 # This is the final chunk of the result
                    )
                )
                # Send final status update: task is completed
                event_queue.enqueue_event(
                    TaskStatusUpdateEvent(
                        taskId=task.id,                 # ID of the task
                        contextId=task.contextId,       # Context ID
                        status=TaskStatus(state=TaskState.completed),  # Mark task as completed
                        final=True,                     # This is the last status update
                    )
                )

            elif event['require_user_input']:  # If the agent needs more information from user
                # Enqueue an input_required status with a message
                event_queue.enqueue_event(
                    TaskStatusUpdateEvent(
                        taskId=task.id,                 # ID of the task
                        contextId=task.contextId,       # Context ID
                        status=TaskStatus(
                            state=TaskState.input_required,  # Set state as input_required
                            message=new_agent_text_message(  # Provide a message asking for input
                                event['content'],             # Message content
                                task.contextId,               # Context ID
                                task.id                       # Task ID
                            ),
                        ),
                        final=True,                     # Input_required is a final state until user responds
                    )
                )

            else:  # The task is still being processed (working)
                # Enqueue a status update showing ongoing work
                event_queue.enqueue_event(
                    TaskStatusUpdateEvent(
                        taskId=task.id,                 # Task ID
                        contextId=task.contextId,       # Context ID
                        status=TaskStatus(
                            state=TaskState.working,    # Mark as still working
                            message=new_agent_text_message(
                                event['content'],       # Current progress or log
                                task.contextId,         # Context ID
                                task.id                  # Task ID
                            ),
                        ),
                        final=False,                    # More updates may follow
                    )
                )

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        # Optional method to cancel long-running tasks (not supported here)
        raise Exception('Cancel not supported')  # Raise error since this agent doesn’t support canceling

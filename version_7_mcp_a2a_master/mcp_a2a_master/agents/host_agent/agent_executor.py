from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import TaskUpdater

from agents.host_agent.agent import HostAgent
from a2a.utils import (
    new_task,
    new_agent_text_message
)

from a2a.utils.errors import ServerError

from a2a.types import (
    Task,
    TaskState,
    UnsupportedOperationError
)

import asyncio

class HostAgentExecutor(AgentExecutor):
    """
    Implements the AgentExecutor interface to integrate the 
    website builder simple agent with the A2A framework.
    """

    def __init__(self):
        self.agent = HostAgent()

    async def create(self):
        """
        Factory method to create and asynchronously initialize the HostAgentExecutor.
        """
        await self.agent.create()

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        """
        Executes the agent with the provided context and event queue.
        """
        query = context.get_user_input()
        task = context.current_task
        if not task:
            task = new_task(context.message)
            await event_queue.enqueue_event(task)

        updater = TaskUpdater(event_queue, task.id, task.contextId)
        
        try:
            async for item in self.agent.invoke(query, task.contextId):
                is_task_complete = item.get("is_task_complete", False)

                if not is_task_complete:
                    message = item.get('updates','The Agent is still working on your request.')
                    await updater.update_status(
                        TaskState.working,
                        new_agent_text_message(message, task.contextId, task.id)
                    )
                else:
                    final_result = item.get('content','no result received')
                    await updater.update_status(
                        TaskState.completed,
                        new_agent_text_message(final_result, task.contextId, task.id)
                    )

                    await asyncio.sleep(0.1)  # Allow time for the message to be processed

                    break
        except Exception as e:
            error_message = f"An error occurred: {str(e)}"
            await updater.update_status(
                TaskState.failed,
                new_agent_text_message(error_message, task.contextId, task.id)
            )
            raise

    async def cancel(self, request: RequestContext, event_queue: EventQueue) -> Task | None:
        raise ServerError(error=UnsupportedOperationError())
from typing import Any
from uuid import uuid4
from a2a.types import (
    AgentCard, 
    Task,
    SendMessageRequest,
    MessageSendParams
)
import httpx
from a2a.client import A2AClient

class AgentConnector:
    """
    Connects to a remote A2A agent and provides a uniform method to delegate tasks
    """

    def __init__(self, agent_card: AgentCard):
        self.agent_card = agent_card

    async def send_task(self, message: str, session_id: str) -> str:
        """
        Send a task to the agent and return the Task object
        
        Args:
            message (str): The message to send to the agent
            session_id (str): The session ID for tracking the task

        Returns:
            Task: The Task object containing the response from the agent
        """

        async with httpx.AsyncClient(timeout = 300.0) as httpx_client:
            a2a_client = A2AClient(
                httpx_client=httpx_client,
                agent_card=self.agent_card,
            )

            send_message_payload: dict[str, Any] = {
                'message': {
                    'role': 'user',
                    'messageId': str(uuid4()),
                    'parts': [
                        {
                            'text': message,
                            'kind': 'text'
                        }
                    ]
                }
            }

            request = SendMessageRequest(
                id = str(uuid4()),
                params=MessageSendParams(
                    **send_message_payload
                )
            )

            response = await a2a_client.send_message(
                request=request
            )

            response_data = response.model_dump(mode='json', exclude_none=True)

            try:
                agent_response = response_data['result']['status']['message']['parts'][0]['text']
            except (KeyError, IndexError):
                agent_response = "No response from agent"

            return agent_response

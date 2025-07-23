import asyncio
from uuid import uuid4
from a2a.client import A2ACardResolver
from a2a.types import (
    AgentCard,
)
import asyncclick as click
import httpx

from utilities.a2a.agent_connect import AgentConnector


@click.command()
@click.option("--agent", default="http://127.0.0.1:10001", help="Base URL of the A2A agent server")
@click.option("--session", default=0, help="Session ID (use 0 to generate a new one)")
async def cli(agent: str, session: str):
    """
    CLI to send user messages to an A2A agent using an A2A client
    and display the responses
    """

    session_id = uuid4().hex if str(session) == "0" else session

    while True:
        prompt = click.prompt("\nWhat do you want to send to the agent. Type ':q' or 'quit' to exit")

        if prompt.strip().lower() in ["quit", ":q"]:
            break

        card: AgentCard = None

        async with httpx.AsyncClient(timeout=300.0) as httpx_client:
            resolver = A2ACardResolver(
                    base_url=agent.rstrip('/'),
                    httpx_client=httpx_client
            )

            card = await resolver.get_agent_card()
        
        

        connector = AgentConnector(card)

        response = await connector.send_task(message=prompt, session_id=session_id)
        print("\nAgent says:", response)

if __name__ == "__main__":
    asyncio.run(cli())
    
import asyncio
import uvicorn

from a2a.types import AgentSkill, AgentCard, AgentCapabilities
import asyncclick as click
from a2a.server.request_handlers import DefaultRequestHandler

from agents.host_agent.agent_executor import HostAgentExecutor
from a2a.server.tasks import InMemoryTaskStore
from a2a.server.apps import A2AStarletteApplication

@click.command()
@click.option('--host', default='localhost', help='Host for the agent server')
@click.option('--port', default=10001, help='Port for the agent server')
async def main(host: str, port: int):
    """
    Main function to create and run the website builder agent.
    """
    skill = AgentSkill(
        id="host_agent_skill",
        name="host_agent_skill",
        description="A simple orchestrator for orchestrating tasks" \
        "with A2A agents and MCP Tools",
        tags=["host", "orchestrator"],
        examples=[
            """Create a simple webpage with a header and a footer 
            using other agents/tools.""",
        ]
    )

    agent_card = AgentCard(
        name ="host_agent",
        description="A simple orchestrator for orchestrating tasks",
        url=f"http://{host}:{port}/",
        version="1.0.0",
        defaultInputModes=["text"],
        defaultOutputModes=["text"],
        skills=[skill],
        capabilities=AgentCapabilities(streaming=True),
    )

    # Create agent executor
    agent_executor = HostAgentExecutor()
    await agent_executor.create()

       
    
    request_handler = DefaultRequestHandler(
        agent_executor=agent_executor,
        task_store=InMemoryTaskStore()
    )

    server = A2AStarletteApplication(
        agent_card=agent_card,
        http_handler=request_handler
    )

    # Fixed: Use uvicorn.Config and Server instead of uvicorn.run() to avoid
    # "asyncio.run() cannot be called from a running event loop" error
    config = uvicorn.Config(server.build(), host=host, port=port)
    server_instance = uvicorn.Server(config)
    
    await server_instance.serve()


if __name__ == "__main__":
    asyncio.run(main())
    
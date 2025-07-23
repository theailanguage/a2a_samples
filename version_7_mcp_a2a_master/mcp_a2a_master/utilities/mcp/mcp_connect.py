import asyncio
import logging
# ADDED: Import signal and sys for graceful shutdown handling
import signal
import sys
from contextlib import asynccontextmanager
from utilities.mcp.mcp_discovery import MCPDiscovery
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool import StdioConnectionParams
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPServerParams

from mcp import StdioServerParameters
from rich import print

# ADDED: Configure logging for MCP cleanup issues to reduce noise during shutdown
logging.getLogger("mcp").setLevel(logging.ERROR)
logger = logging.getLogger(__name__)

class MCPConnector:
    """
    Discovers the MCP servers from the config.
    Config will be loaded by the MCP discovery class
    Then it lists each server's tools
    and then caches them as MCPToolsets that are compatible with 
    Google's Agent Development Kit
    """

    def __init__(self, config_file: str = None):
        self.discovery = MCPDiscovery(config_file=config_file)
        self.tools: list[MCPToolset] = []
        
    async def _load_all_tools(self):
        """
        Loads all tools from the discovered MCP servers 
        and caches them as MCPToolsets.
        """
    
        tools = []

        for name, server in self.discovery.list_servers().items():
            try:
                if server.get("command") == "streamable_http":
                    conn = StreamableHTTPServerParams(url=server["args"][0])
                else:
                    conn = StdioConnectionParams(
                    server_params=StdioServerParameters(
                        command=server["command"],
                        args=server["args"]
                    ),
                    timeout=5
                    )
                
                # ADDED: Wrap toolset creation with timeout and error handling
                # This prevents hanging on unresponsive MCP servers
                toolset = await asyncio.wait_for(
                    MCPToolset(connection_params=conn).get_tools(),
                    timeout=10.0
                )
                
                if toolset:
                    # Create the actual toolset object for caching
                    mcp_toolset = MCPToolset(connection_params=conn)
                    tool_names = [tool.name for tool in toolset]
                    print(f"[bold green]Loaded tools from server [cyan]'{name}'[/cyan]:[/bold green] {', '.join(tool_names)}")
                    tools.append(mcp_toolset)
                    
            # ADDED: Specific error handling for different types of connection failures
            except asyncio.TimeoutError:
                print(f"[bold red]Timeout loading tools from server '{name}' (skipping)[/bold red]")
            except ConnectionError as e:
                print(f"[bold red]Connection error loading tools from server '{name}': {e} (skipping)[/bold red]")
            except Exception as e:
                print(f"[bold red]Error loading tools from server '{name}': {e} (skipping)[/bold red]")
    
        self.tools = tools
    
    async def get_tools(self) -> list[MCPToolset]:
        """
        Returns the cached list of MCPToolsets.
        """

        await self._load_all_tools()
        return self.tools.copy()    
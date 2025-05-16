# =============================================================================
# utilities/mcp/mcp_discovery.py
# =============================================================================
# 🎯 Purpose:
# Loads an MCP (Model Context Protocol) configuration file listing one or
# more MCP servers, and exposes a simple API to retrieve their definitions.
# =============================================================================

import os  # Provides functions for interacting with the file system
import json  # Provides functions for parsing and generating JSON data
import logging  # Provides logging capability for warnings and errors
from typing import Dict, Any  # Type annotations: Dict[K, V] and Any type

# Create a logger specific to this module
logger = logging.getLogger(__name__)


class MCPDiscovery:
    """
    🔍 Reads a JSON config file defining MCP servers and provides access
    to the server definitions under the "mcpServers" key.

    Attributes:
        config_file (str): Path to the JSON configuration file.
        config (Dict[str, Any]): Parsed JSON content, expected to contain "mcpServers".
    """

    def __init__(self, config_file: str = None):
        """
        Initialize the discovery client.

        Args:
            config_file (str, optional): Custom path to the MCP config JSON.
                                         If None, defaults to 'mcp_config.json'
                                         located in the same directory as this module.
        """
        # If the caller provided a config_file, use it; otherwise build the default path
        if config_file:
            self.config_file = config_file  # Use the custom path
        else:
            # Determine this module's directory and join with 'mcp_config.json'
            self.config_file = os.path.join(
                os.path.dirname(__file__),  # Directory containing this file
                "mcp_config.json"  # Default config filename
            )

        # Load and parse the configuration JSON file into a Python dict
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """
        Read and parse the JSON config file.

        Returns:
            Dict[str, Any]: The entire JSON object if valid;
                            otherwise, an empty dict on error.
        """
        try:
            # Attempt to open the file in read mode
            with open(self.config_file, 'r') as f:
                data = json.load(f)  # Parse JSON into Python object

            # Ensure the top-level JSON is a dictionary/object
            if not isinstance(data, dict):
                # If not, raise a ValueError to trigger the exception handler
                raise ValueError("MCP config must be a JSON object at the top level.")

            # Return the parsed JSON data
            return data

        except FileNotFoundError:
            # Log a warning if the file does not exist, then return empty config
            logger.warning(f"MCP config file not found: {self.config_file}")
            return {}

        except (json.JSONDecodeError, ValueError) as e:
            # Log an error if parsing fails or data is not a dict
            logger.error(f"Error parsing MCP config: {e}")
            return {}

    def list_servers(self) -> Dict[str, Any]:
        """
        Retrieve the mapping of server names to their configuration entries.

        The JSON should look like:

        {
            "mcpServers": {
                "server 1 name": { "command": "...", "args": [...] },
                "server 2 name":           { "command": "...", "args": [...] }
            }
        }

        Returns:
            Dict[str, Any]: The dictionary under "mcpServers", or empty dict if missing.
        """
        # Use dict.get to safely retrieve 'mcpServers'; return {} if key not found
        return self.config.get('mcpServers', {})

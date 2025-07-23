# MCP A2A Master Class

This project is a comprehensive master class on building a multi-agent system from scratch. It covers the fundamentals of creating a robust and scalable multi-agent architecture using the Mission Control Protocol (MCP) and Agent-to-Agent (A2A) communication.

## Project Overview

The project demonstrates how to build a multi-agent system with a `host_agent` that orchestrates tasks by discovering and delegating to other agents. The communication and discovery mechanisms are built on top of MCP and A2A protocols.

### Core Concepts Covered

*   **Multi-Agent System Design:** Learn how to design and structure a multi-agent system with a clear separation of concerns.
*   **Host Agent:** A central agent responsible for task orchestration, delegation, and coordination.
*   **A2A Compatible Agents:** Build agents that can communicate and interact with each other using the A2A protocol.
*   **MCP Servers:** Implement MCP servers for agent and tool discovery.
    *   **Streamable HTTP Server:** A streamable HTTP server for real-time communication.
    *   **Stdio Server:** A standard I/O server for simple, direct communication.
*   **MCP and A2A Connectors:** Connectors for establishing communication between agents and servers.
*   **Discovery Mechanisms:**
    *   **MCP Server and Tool Discovery:** Dynamically discover available MCP servers and their tools.
    *   **A2A Agent Discovery:** Discover and register A2A compatible agents.
*   **Task Delegation:** Delegate tasks from the host agent to specialized agents.

## Project Structure

```
/Users/theailanguage/mcp_a2a_master/
├───.gitignore
├───main.py
├───pyproject.toml
├───README.md
├───agents/
│   ├───host_agent/
│   └───website_builder_simple/
├───app/
│   └───cmd/
├───mcp/
│   └───servers/
└───utilities/
    ├───a2a/
    ├───common/
    └───mcp/
```

## Folder Explanations

*   [**agents/**](./agents): Contains the different agents in the system.
    *   [**host_agent/**](./agents/host_agent): The main orchestrator agent.
    *   [**website_builder_simple/**](./agents/website_builder_simple): A simple agent that can build websites.
*   [**app/cmd/**](./app/cmd): A command-line application for interacting with the system.
*   [**mcp/servers/**](./mcp/servers): Contains the MCP server implementations.
*   [**utilities/**](./utilities): Contains the utilities for A2A and MCP communication and discovery.

## Getting Started

### Prerequisites

*   Python 3.11+
*   `uv`

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/mcp-a2a-master.git
    cd mcp-a2a-master
    ```
2.  **Create and activate the virtual environment:**

    *   **macOS/Linux:**
        ```bash
        python3 -m venv .venv
        source .venv/bin/activate
        ```
    *   **Windows:**
        ```bash
        python -m venv .venv
        .venv\Scripts\activate
        ```
3.  **Install dependencies:**
    ```bash
    uv pip install -r requirements.txt
    ```

## How to Run

1.  **Streamable HTTP Server:**
    ```bash
    uv run python3 -m mcp.servers.streamable_http_server
    ```
2.  **Website Builder Simple Agent:**
    ```bash
    uv run python3 -m agents.website_builder_simple
    ```
3.  **Host Agent:**
    ```bash
    uv run python3 -m agents.host_agent
    ```
4.  **CMD App:**
    ```bash
    uv run python3 -m app.cmd.cmd
    ```

## How it Works

The `main.py` script initializes the multi-agent system. The `host_agent` starts and uses the `mcp_discovery` and `a2a_discovery` utilities to find available servers and agents. Once discovered, the `host_agent` can delegate tasks to other agents, such as the `website_builder_simple` agent, using the A2A communication protocol.

The `mcp` directory contains the server implementations, and the `utilities` directory provides the necessary tools for discovery and connection.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue.

## 📜 License

This repository is licensed under the **GNU General Public License v3.0**.
See the [LICENSE](./LICENSE) file for full details.

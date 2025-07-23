# MCP Servers

## Overview

This directory contains the implementations of the Mission Control Protocol (MCP) servers that are used in the multi-agent system. MCP servers are responsible for providing a standardized way for agents to discover and interact with tools and other resources.

## Server Implementations

### Streamable HTTP Server (`streamable_http_server.py`)

This server provides a streamable HTTP interface for real-time, asynchronous communication. It is well-suited for applications that require a continuous flow of data, such as streaming logs or real-time notifications.

**How to Run:**

```bash
uv run python3 -m mcp.servers.streamable_http_server
```

### Terminal Server (`terminal_server/terminal_server.py`)

This server provides a simple, direct communication channel using standard input/output (stdio). It is ideal for scenarios where a simple, no-frills communication mechanism is sufficient.

## Interaction with Other Components

*   **Agents:** Agents connect to these MCP servers to discover and utilize the tools and resources they provide. The servers act as a bridge between the agents and the underlying tools.
*   **MCP Utilities:** The `mcp_discovery` utility is used by agents to find and connect to these servers.
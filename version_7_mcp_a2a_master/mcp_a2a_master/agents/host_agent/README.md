# Host Agent

## Overview

The Host Agent is the central nervous system of this multi-agent system. It acts as an orchestrator, responsible for receiving tasks, breaking them down into smaller, manageable steps, and delegating those steps to the appropriate specialized agents. It maintains an awareness of the available agents and their capabilities through the A2A discovery mechanism and leverages MCP servers to discover and utilize available tools.

## Key Responsibilities

*   **Task Reception and Decomposition:** The Host Agent is the primary entry point for user requests. It analyzes incoming tasks and decomposes them into a sequence of actions that can be executed by other agents.
*   **Agent Discovery and Selection:** Using the `a2a_discovery` utility, the Host Agent dynamically discovers available agents and their functionalities. It then selects the most suitable agent for each sub-task based on their advertised capabilities.
*   **Task Delegation and Coordination:** Once an agent is selected, the Host Agent delegates the task and monitors its execution. It coordinates the flow of information between agents, ensuring that the output of one agent can be used as the input for another.
*   **Tool Discovery and Utilization:** The Host Agent interacts with MCP servers to discover and utilize available tools. This allows it to extend its own capabilities and provide more complex solutions.

## How to Run

To run the Host Agent, execute the following command from the root of the project:

```bash
uv run python3 -m agents.host_agent
```

## Interaction with Other Components

*   **A2A Agents:** The Host Agent communicates with other agents (e.g., `website_builder_simple`) using the A2A protocol. This enables it to delegate tasks and receive results.
*   **MCP Servers:** The Host Agent connects to MCP servers to discover and utilize tools. This allows it to access a wider range of functionalities.
*   **CMD App:** The CMD App provides a user interface for interacting with the Host Agent, allowing users to submit tasks and monitor their execution.
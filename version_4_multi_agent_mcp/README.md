# version_4_multi_agent_mcp

🎯 **Purpose**  
This repository demonstrates a distributed multi-agent system that combines Google’s Agent-to-Agent (A2A) protocol with Anthropic’s Model Context Protocol (MCP). You’ll see how a front-end client, a central “Host” OrchestratorAgent, multiple child A2A agents, and external MCP servers all interoperate seamlessly.

---

## 🚀 Features

- **A2A Protocol** – Agents discover each other via JSON-RPC and call one another’s skills.
- **MCP Integration** – Dynamically discover and load third-party MCP servers and expose each MCP tool as a callable function.
- **Orchestrator Agent** – A central LLM-powered agent that routes user requests to the right child A2A agent **or** MCP tool.
- **Modular & Extensible** – Drop in new A2A agents or MCP servers simply by updating a registry or config file.

---

## 📦 Project Structure

```bash
version_4_multi_agent_mcp/
├── .env                             # YOUR GOOGLE_API_KEY, etc. (gitignored)
├── pyproject.toml                   # Project metadata & dependencies
├── README.md                        # This file
├── utilities/
│   ├── a2a/
│   │   ├── agent_discovery.py       # Reads agent_registry.json
│   │   ├── agent_connect.py         # Calls remote A2A agents over JSON-RPC
│   │   └── agent_registry.json      # List of child-agent endpoints
│   └── mcp/
│       ├── mcp_discovery.py         # Reads mcp_config.json
│       ├── mcp_connect.py           # Connects to MCP servers & lists their tools
│       └── mcp_config.json          # Defines available MCP servers & launch commands
├── agents/
│   ├── tell_time_agent/
│   │   ├── __main__.py         # Starts TellTimeAgent server
│   │   ├── agent.py            # Gemini-based time agent
│   │   └── task_manager.py     # In-memory task handler for TellTimeAgent
│   ├── greeting_agent/
│   │   ├── __main__.py         # Starts GreetingAgent server
│   │   ├── agent.py            # Orchestrator that calls TellTimeAgent + LLM greeting
│   │   └── task_manager.py     # Task handler for GreetingAgent
│   └── host_agent/
│       ├── entry.py                 # CLI: boots the OrchestratorAgent server
│       ├── orchestrator.py          # Gemini LLM routing logic + TaskManager
│       └── ... (no more agent_connect here)
├── server/
│   ├── server.py                    # A2A JSON-RPC server (Starlette)
│   └── task_manager.py              # Base & InMemoryTaskManager for A2A
├── client/
│   ├── a2a_client.py                # Async A2A client (tasks/send, tasks/get)
├── app/
│   └── cmd/
│       └── cmd.py                   # CLI app that talks to either A2A or MCP client
└── models/
    ├── agent.py              # AgentCard, AgentSkill, AgentCapabilities
    ├── json_rpc.py           # JSON-RPC request/response formats
    ├── request.py            # SendTaskRequest, A2ARequest union
    └── task.py               # Task structure, messages, status```

---

## 🛠️ Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) (optional, for streamlined venv & installs)
- A valid `GOOGLE_API_KEY` with access to Gemini via the Google ADK

---

## ⚙️ Setup & Install

1. **Clone & enter**  
   ```bash
   git clone https://github.com/theailanguage/a2a_samples.git
   cd version_4_multi_agent_mcp
   ```

2. **Create & activate virtualenv**  
   ```bash
   cd version_4p01_with_vision_agent
   uv venv
   source .venv/bin/activate
   uv sync --all-groups
   ```

3. **Configure credentials**  
   Create a `.env` in the project root containing:  
   ```bash
   touch .env
   echo "GOOGLE_API_KEY=your_gemini_api_key_here" > .env
   ```

---

## 🎬 Running the Demo

### 1. Start your child A2A agents

```bash
# TellTimeAgent (returns current time)
uv run python3 -m agents.tell_time_agent --host localhost --port 10002

# GreetingAgent (calls TellTimeAgent + LLM greeting)
uv run python3 -m agents.greeting_agent --host localhost --port 10001
```

> Each agent serves a JSON-RPC endpoint at `/` and advertises metadata at `/.well-known/agent.json`.

### 2. Start the Host OrchestratorAgent

```bash
uv run python3 -m agents.host_agent.entry --host localhost --port 10000
```

### 3. Use the CLI to talk to your Orchestrator

```bash
uv run python3 -m app.cmd.cmd --agent http://localhost:10000
```
---

## 📖 Architecture Overview

1. **Front-End Client**  
   - Web/Mobile/CLI → Issues A2A JSON-RPC calls to the Host Agent.

2. **Host OrchestratorAgent**  
   - **A2A branch:** `list_agents()` & `delegate_task(...)`.  
   - **MCP branch:** Discovers MCP servers, loads & exposes each tool.

3. **Child A2A Agents**  
   - Domain-specific handlers (time, greetings).

4. **MCP Servers**  
   - Serve tool definitions & executions over stdio.

---

## 💡 Why This Design?

- **Modularity**: Easily add/remove agents or tools.  
- **Scalability**: Central orchestrator routes high volume.  
- **Flexibility**: LLM picks between programmatic and agent skills.  
- **Simplicity**: Leverages JSON-RPC & stdio protocols.
# 🤖 TellTimeAgent & Multi-Agent Demo – A2A with Google ADK

Welcome to **TellTimeAgent** and the **Multi-Agent** demo — a minimal Agent2Agent (A2A) implementation using Google's [Agent Development Kit (ADK)](https://github.com/google/agent-development-kit).

This example demonstrates how to build, serve, and interact with three A2A agents:
1. **TellTimeAgent** – replies with the current time.
2. **GreetingAgent** – fetches the time and generates a poetic greeting.
3. **OrchestratorAgent** – routes requests to the appropriate child agent.

All of them work together seamlessly via A2A discovery and JSON-RPC.

---

## 📦 Project Structure

```bash
version_3_multi_agent/
├── .env                         # Your GOOGLE_API_KEY (not committed)
├── pyproject.toml              # Dependency config
├── README.md                   # You are reading it!
├── app/
│   └── cmd/
│       └── cmd.py              # CLI to interact with the OrchestratorAgent
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
│       ├── entry.py            # CLI to start OrchestratorAgent server
│       ├── orchestrator.py     # LLM router + TaskManager for OrchestratorAgent
│       └── agent_connect.py    # Helper to call child A2A agents
├── server/
│   ├── server.py               # A2A JSON-RPC server implementation
│   └── task_manager.py         # Base in-memory task manager interface
└── utilities/
    ├── discovery.py            # Finds agents via `agent_registry.json`
    └── agent_registry.json     # List of child-agent URLs (one per line)
```

---

## 🛠️ Setup

1. **Clone & navigate**

    ```bash
    git clone https://github.com/theailanguage/a2a_samples.git
    cd a2a_samples/version_3_multi_agent
    ```

2. **Create & activate a venv**

    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3. **Install dependencies**

    Using [`uv`](https://github.com/astral-sh/uv):

    ```bash
    uv pip install .
    ```

    Or with pip directly:

    ```bash
    pip install .
    ```

4. **Set your API key**

    Create `.env` at the project root:
    ```bash
    echo "GOOGLE_API_KEY=your_api_key_here" > .env
    ```

---

## 🎬 Demo Walkthrough

**Start the TellTimeAgent**
```bash
python3 -m agents.tell_time_agent \
  --host localhost --port 10000
```

**Start the GreetingAgent**
```bash
python3 -m agents.greeting_agent \
  --host localhost --port 10001
```

**Start the Orchestrator (Host) Agent**
```bash
python3 -m agents.host_agent.entry \
  --host localhost --port 10002
```

**Launch the CLI (cmd.py)**
```bash
python3 -m app.cmd.cmd --agent http://localhost:10002
```

**Try it out!**
```bash
> What time is it?
Agent says: The current time is: 2025-05-05 14:23:10

> Greet me
Agent says: Good afternoon, friend! The golden sun dips low...
```

---

## 🔍 How It Works

1. **Discovery**: OrchestratorAgent reads `utilities/agent_registry.json`, fetches each agent’s `/​.well-known/agent.json`.
2. **Routing**: Based on intent, the Orchestrator’s LLM calls its tools:
   - `list_agents()` → lists child-agent names
   - `delegate_task(agent_name, message)` → forwards tasks
3. **Child Agents**:
   - TellTimeAgent returns the current time.
   - GreetingAgent calls TellTimeAgent then crafts a poetic greeting.
4. **JSON-RPC**: All communication uses A2A JSON-RPC 2.0 over HTTP via Starlette & Uvicorn.

---

## 📖 Learn More

- A2A GitHub: https://github.com/google/A2A  
- Google ADK: https://github.com/google/agent-development-kit
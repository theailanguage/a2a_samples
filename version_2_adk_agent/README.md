# 🤖 TellTimeAgent - A2A Agent Using Google ADK

Welcome to **TellTimeAgent** — a minimal Agent2Agent (A2A) implementation using Google's [Agent Development Kit (ADK)](https://github.com/google/agent-development-kit).

This example demonstrates how to build, serve, and interact with a Gemini-powered agent that replies with the current time.

---

## 📦 Project Structure

```bash
a2a_samples/version_2_adk_agent/
├── .env                       # API key goes here (not committed)
├── pyproject.toml            # Dependency config (used with uv or pip)
├── README.md                 # You're reading it!
├── app/
│   └── cmd/
│       └── cmd.py            # Command-line app to talk to the agent
├── agents/
│   └── google_adk/
│       ├── __main__.py       # Starts the agent + A2A server
│       ├── agent.py          # Gemini agent definition using Google ADK
│       └── task_manager.py   # Handles task lifecycle
├── server/
│   ├── server.py             # A2A server logic (routes, JSON-RPC)
│   └── task_manager.py       # In-memory task storage + interface
└── models/
    ├── agent.py              # AgentCard, AgentSkill, AgentCapabilities
    ├── json_rpc.py           # JSON-RPC request/response formats
    ├── request.py            # SendTaskRequest, A2ARequest union
    └── task.py               # Task structure, messages, status
```

---

## 🚀 Features

✅ Gemini-powered A2A agent using Google ADK  
✅ Follows JSON-RPC 2.0 specification  
✅ Supports session handling and memory  
✅ Custom A2A server implementation (non-streaming)  
✅ CLI to interact with agent  
✅ Fully commented and beginner-friendly

---

## 💠 Setup

### 1. Clone and navigate to the repo

```bash
git clone https://github.com/your-username/a2a-adk-telltime-agent.git
cd a2a_samples/version_2_adk_agent
```

### 2. Create virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

Using [`uv`](https://github.com/astral-sh/uv):

```bash
uv pip install .
```

Or using pip (if you generated a `requirements.txt`):

```bash
pip install -r requirements.txt
```

---

## 🔑 API Key Setup

Create a `.env` file in the root directory:

```bash
touch .env
```

And add your Gemini API key:

```env
GOOGLE_API_KEY=your_api_key_here
```

---

## ▶️ Running the Agent

In one terminal window:

```bash
source .venv/bin/activate
cd a2a_samples/version_2_adk_agent
python3 -m agents.google_adk
```

You should see:

```
Uvicorn running on http://localhost:10002
```

---

## 🧑‍💻 Running the Client

Open a **second terminal window**:

```bash
source .venv/bin/activate
cd a2a_samples/version_2_adk_agent
python3 -m app.cmd.cmd --agent http://localhost:10002
```

You can now type messages like:

```bash
what time is it?
```

And get a Gemini-powered response!

---

## 🔍 Agent Workflow (A2A Lifecycle)

1. The client queries the agent using a CLI (`cmd.py`)
2. The A2A client sends a task using JSON-RPC to the A2A server
3. The server parses the request, invokes the task manager
4. The task manager calls the Gemini-powered `TellTimeAgent`
5. The agent responds with current system time
6. The server wraps the response and sends it back to the client

---

## 📸 Screenshot (Optional)

> Add a screenshot or GIF of the CLI interaction here!

---

## 📜 License

MIT — free for personal and commercial use.

---

## 🙌 Acknowledgements

- [Google ADK (Agent Development Kit)](https://github.com/google/agent-development-kit)
- [Gemini API](https://ai.google.dev/)
- [Starlette](https://www.starlette.io/)
- [Uvicorn](https://www.uvicorn.org/)

---

## 🌐 Connect with Me

- [YouTube: The AI Language](https://youtube.com/@theailanguage)
- Twitter / X: [@theailanguage](https://twitter.com/theailanguage)
- GitHub: [@theailanguage](https://github.com/theailanguage)

---
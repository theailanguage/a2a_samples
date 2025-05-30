# version_4p01_with_vision_agent

🌟 **Purpose**  
This repository builds on version 4 of our multi-agent A2A + MCP architecture by adding a **Gemini-based VisionAgent** that can analyze images via file path or URL. You’ll see how a lightweight front-end client, a central Host OrchestratorAgent, and specialized agents (like VisionAgent, TellTimeAgent, and GreetingAgent) collaborate over Google’s Agent-to-Agent (A2A) protocol and Anthropic’s Model Context Protocol (MCP).

---

## 🚀 Features

- **Gemini Vision Agent** – Accepts text+image input and answers image-based questions using `gemini-2.0-flash`
- **A2A Protocol** – Agents discover and call each other over JSON-RPC
- **MCP Integration** – Automatically discovers and invokes tools hosted via MCP
- **Orchestrator Agent** – A central Gemini-powered router that connects everything
- **Modular & Extensible** – Add agents or tools by updating JSON config

---

## 📦 Project Structure

```bash
version_4p01_with_vision_agent/
├── .env                             # Contains GOOGLE_API_KEY (gitignored)
├── pyproject.toml                   # Project metadata & dependencies
├── README.md                        # This file
├── utilities/
│   ├── a2a/
│   │   ├── agent_discovery.py       # Loads agent_registry.json
│   │   ├── agent_connect.py         # Calls agents using JSON-RPC
│   │   └── agent_registry.json      # Defines A2A agents (VisionAgent, etc.)
│   └── mcp/
│       ├── mcp_discovery.py         # Loads MCP servers
│       ├── mcp_connect.py           # Loads & calls tools via MCP
│       └── mcp_config.json          # Defines MCP servers & tools
├── agents/
│   ├── tell_time_agent/             # Returns the current time
│   ├── greeting_agent/              # Returns a poetic greeting based on time of day
│   ├── vision_agent/                # NEW: Accepts image + query
│   │   ├── __main__.py              # Starts the vision agent
│   │   ├── agent.py                 # Loads Gemini + handles image input
│   │   └── task_manager.py          # Routes incoming tasks to the agent
│   └── host_agent/                  # Central orchestrator
│       ├── entry.py
│       ├── orchestrator.py
├── server/
│   ├── server.py                    # A2A JSON-RPC server
│   └── task_manager.py              # In-memory task tracking
├── client/
│   ├── a2a_client.py                # Makes JSON-RPC task requests
├── app/
│   └── cmd/
│       └── cmd.py                   # CLI to interact with host agent
└── models/
    ├── agent.py
    ├── json_rpc.py
    ├── request.py
    └── task.py
````

---

## 🛠️ Prerequisites

* Python 3.11+
* [uv](https://github.com/astral-sh/uv)
* Valid `GOOGLE_API_KEY` with Gemini access

---

## ⚙️ Setup & Install

```bash
# Clone the repo
cd version_4p01_with_vision_agent
uv venv
source .venv/bin/activate
uv sync --all-groups

# Add your Gemini API Key
echo "GOOGLE_API_KEY=your_key_here" > .env
```

---

## 🎥 Running the Demo

### 1. Start your agents

```bash
# VisionAgent
uv run python3 -m agents.vision_agent --host localhost --port 10003

# TellTimeAgent
uv run python3 -m agents.tell_time_agent --host localhost --port 10002

# GreetingAgent
uv run python3 -m agents.greeting_agent --host localhost --port 10001
```

### 2. Start the Orchestrator Host Agent

```bash
uv run python3 -m agents.host_agent.entry --host localhost --port 10000
```

### 3. Ask your Host Agent to describe an image!

```bash
uv run python3 -m app.cmd.cmd --agent http://localhost:10000
```

---

## 📅 Architecture Overview

* **Client** → Sends query + image to HostAgent
* **HostAgent** → Detects VisionAgent via A2A registry, forwards task
* **VisionAgent** → Uses Gemini to analyze the image & reply
* **Also includes** → TellTimeAgent, GreetingAgent, and MCP Tool support

---

## 💡 What This Teaches

* How to combine Gemini LLM with vision and external query routing
* How to architect multi-agent workflows using A2A
* How to wrap visual AI into callable services

---

## ✨ More Resources

* [The AI Language Course on Udemy](https://www.udemy.com/course/modelcontextprotocol/?referralCode=6FADE0F85C5DB97203C6)
* [Subscriber-only Code Access](https://theailanguage.com/onlySubscribers?id=a2a_samples&site=github)
* [Previous Video (Multi-agent orchestration with MCP)](https://www.youtube.com/watch?v=ALN7wSJ5pGI&list=PL6tW9BrhiPTCKTXXJAwigi7QDNpA7t4Ip)
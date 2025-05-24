# 🕒 version_5_a2a_sdk

🌟 **Purpose**  
This version demonstrates a **minimal educational setup** using Google's [Agent-to-Agent (A2A)](https://github.com/google/A2A) protocol via the official **`a2a-python` SDK**.

It includes:
- A single **TellTime agent** that returns the current system time
- A single **A2A client** that sends messages and receives streaming responses
- Shared **utility code** for formatting agent responses into A2A-compatible event types

This version is ideal as a **first hands-on project** to understand A2A SDK usage.

---

## 🚀 Features

- ✅ Minimal working agent with LangChain + Gemini + time tool
- ✅ Fully async A2A client using the SDK
- ✅ Streaming responses with structured task updates
- ✅ Clean, modular file structure

---

## 📦 Project Structure

```bash
version_5_a2a_sdk/
🔺── agents/
│   🔺── tell_time_agent/
│       🔺── agent.py               # LangChain-based agent with time tool
│       🔺── agent_executor.py      # AgentExecutor that connects agent to A2A
🔺── client/
│   🔺── client.py                  # A2A SDK client that runs test scenarios
🔺── utilities/
│   🔺── a2a/
│       🔺── utilities.py           # Converts agent responses into A2A event formats
🔺── pyproject.toml
🔺── README.md
```

---

## 🛠️ Prerequisites

- Python 3.13+
- [`uv`](https://github.com/astral-sh/uv) (recommended for environment setup)
- A valid `GOOGLE_API_KEY` for Gemini (required by LangChain)

---

## ⚙️ Setup & Install

```bash
git clone https://github.com/theailanguage/a2a_samples.git
cd version_5_a2a_sdk
uv sync
source .venv/bin/activate

# Add Gemini API key
echo "GOOGLE_API_KEY=your_gemini_key_here" > .env
```

---

## 🧪 Running the Project

### 🟢 Step 1: Start the TellTime Agent Server

```bash
uv run python3 -m agents.tell_time_agent.agent_executor
```

This launches the agent server at `http://localhost:10000`.

It uses a tool to return the current system time, and supports:
- ✅ Single-turn queries
- ✅ Streaming results
- ✅ Multi-turn interactions if needed

### 🟡 Step 2: Run the Client

```bash
uv run python3 client/client.py
```

This will:
- Send a one-shot question like _"What time is it?"_
- Run a streaming task to show how real-time updates work
- Demonstrate a multi-turn flow (if the agent requests clarification)

---

## 🧐 Agent Logic (Inside `agent.py`)

The agent is a LangChain ReAct agent with one tool:

```python
from datetime import datetime

def get_time_now():
    return {"current_time": datetime.now().strftime("%H:%M:%S")}
```

The agent responds to any time-related query using this tool, and replies in a structured format (`status`, `message`) compatible with A2A.

---

## 💡 What You Learn in This Version

| Concept                  | Description                                                                 |
|--------------------------|-----------------------------------------------------------------------------|
| A2A SDK usage            | Connect to an agent, send messages, stream task updates                     |
| AgentExecutor setup      | How to bridge your agent with A2A's lifecycle using events                  |
| Streaming architecture   | How partial agent responses become events (`working`, `completed`, etc.)    |
| Response formatting      | How to turn agent output into A2A-compliant artifacts and messages          |

---

## 🔄 Coming from `version_4_multi_agent_mcp`?

This version:
- ✅ Removes MCP integration
- ✅ Removes multi-agent orchestration
- ✅ Focuses purely on **A2A SDK usage**
- ✅ Keeps just one agent and one client — ideal for beginners

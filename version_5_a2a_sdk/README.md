# 🕒 version_5_a2a_sdk

## 🌟 Purpose
This version demonstrates a **minimal educational setup** using Google's [Agent-to-Agent (A2A)](https://github.com/google/A2A) protocol via the official **`a2a-python` SDK**.

It includes:
- A single **TellTime agent** that returns the current system time
- A single **A2A client** that sends messages and receives streaming responses
- A clear example of multi-turn streaming via task updates

This version is ideal as a **first hands-on project** to understand A2A SDK usage.

---

## 🚀 Features

- ✅ Minimal working agent with LangChain + Gemini + time tool
- ✅ Fully async A2A client using the SDK
- ✅ Streaming responses with task update events
- ✅ Supports multi-turn interactions
- ✅ Clean, modular folder structure

---

## 📦 Project Structure

```bash
version_5_a2a_sdk/
→ agents/
    → tell_time_agent/
        agent.py             # LangChain-based TellTime agent logic
        agent_executor.py    # Executor that connects the agent to A2A runtime
        __main__.py          # Starts the agent server (entry point)
        __init__.py          # Required to treat this folder as a module

→ client/
    client.py               # A2A SDK client that streams messages to the agent

main.py                    # Optional runner stub
README.md                  # You're reading it!
````

---

## 🛠️ Prerequisites

* Python 3.13+
* [`uv`](https://github.com/astral-sh/uv) for clean environment setup
* A valid `GOOGLE_API_KEY` for Gemini

---

## ⚙️ Setup & Installation

```bash
git clone https://github.com/theailanguage/a2a_samples.git
cd version_5_a2a_sdk
uv init --python python3.13
uv venv
source .venv/bin/activate
uv add a2a-sdk langchain langgraph google-genai httpx python-dotenv langchain-google-genai uvicorn click rich
uv sync --all-groups
touch .env
echo "GOOGLE_API_KEY=your_key_here" > .env
```

---

## 🧪 Running the Project

### 🟢 Step 1: Start the TellTime Agent Server

```bash
uv run python3 -m agents.tell_time_agent
```

This launches the agent server at `http://localhost:10000`.

### 🟡 Step 2: Run the A2A Client

```bash
uv run python3 client/client.py
```

This lets you:

* Ask one-shot queries like *"What time is it?"*
* Watch streaming updates in real time
* Handle follow-up input for multi-turn dialogs

---

## 🤔 How the Agent Works (agent.py)

* Uses LangChain ReAct agent with Gemini (Flash model)
* Has one tool:

```python
@tool
def get_time_now():
    return {"current_time": datetime.now().strftime("%H:%M:%S")}
```

* Responds with a structured format:

```python
{"status": "completed", "message": "The current time is ..."}
```

---

## 💡 What You'll Learn

| Concept               | Description                                                    |
| --------------------- | -------------------------------------------------------------- |
| A2A SDK usage         | Connect, send, and stream tasks to an agent                    |
| AgentExecutor pattern | How the agent gets plugged into A2A's server loop              |
| Streaming flow        | Watch how `working` → `completed` messages are delivered       |
| Multi-turn handling   | Learn how agents can request clarification/input from the user |

---

Happy coding ✨
# 🧠 A2A Agent Samples – Powered by Google's Agent-to-Agent Protocol

Welcome to the `a2a_samples` repository! This project contains multiple implementations of AI agents using [Google's A2A (Agent-to-Agent)](https://github.com/google/A2A) protocol.

These implementations demonstrate how to:
- Set up and run A2A-compliant servers and clients
- Use discovery endpoints and standardized task formats
- Integrate with Google's ADK (Agent Development Kit)

We plan to continuously add more versions to illustrate various approaches and frameworks.

---

## 📁 Folder Structure

```
a2a_samples/
├── version_1_simple/      # Basic implementation using Flask
├── version_2_adk_agent/   # Advanced agent built using Google ADK + Gemini
```

---

## 📦 Version Overview

### ✅ `version_1_simple`
A beginner-friendly demo that uses Flask to create a basic A2A server agent (`TellTimeAgent`) and a client that:
- Fetches the agent card from the `/.well-known/agent.json` endpoint
- Sends a simple task to `/tasks/send`
- Receives a time-based response

➡️ [Explore the folder](./version_1_simple/)


### 🚀 `version_2_adk_agent`
A more advanced version using **Google's ADK (Agent Development Kit)** to implement a fully functional Gemini-powered A2A agent.
- Integrates memory, sessions, and artifacts
- Uses ADK runners and LLM agents
- Structured with reusable components and aligned with A2A's JSON-RPC model

➡️ [Explore the folder](./version_2_adk_agent/)


---

## 🧪 Running the Code
Each version contains its own `README.md` file with detailed instructions on:
- Setting up Python environments
- Installing dependencies
- Running the server and client

Make sure to check the respective version folder before you begin!

---

## 🛠 Future Plans
- Add streaming support via SSE and `tasks/sendSubscribe`
- Add push notification samples
- Add more ADK agent variants with different skills

Stay tuned and ⭐ star the repo if you find it useful!

---

## 📜 License
This repository is licensed under the **GNU General Public License v3.0**. 
See the [LICENSE](./LICENSE) file for full details.

---

Happy building with A2A! 🛠
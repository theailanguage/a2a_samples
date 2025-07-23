# 🧠 A2A Agent Samples – Powered by Google's Agent-to-Agent Protocol

Welcome to the `a2a_samples` repository! This project contains multiple implementations of AI agents using [Google's A2A (Agent-to-Agent)](https://github.com/google/A2A) protocol.

These implementations demonstrate how to:

* Set up and run A2A-compliant servers and clients
* Use discovery endpoints and standardized task formats
* Integrate with Google's ADK (Agent Development Kit)

We plan to continuously add more versions to illustrate various approaches and frameworks.

---

## 📁 Folder Structure

```bash
a2a_samples/
├── version_1_simple/        # Basic implementation using Flask
├── version_2_adk_agent/     # Advanced agent built using Google ADK + Gemini
├── version_3_multi_agent/   # Multi-agent orchestration example
├── version_4_multi_agent_mcp/ # Distributed multi-agent with A2A + MCP integration
├── version_4p01_with_vision_agent/ # Adds Gemini-based VisionAgent to version_4 architecture
├── version_5_a2a_sdk/       # Minimal A2A PYTHON SDK setup with streaming, LangChain + Gemini
├── version_6_docker_vision_agent/ # Dockerized Gemini Vision Agent deployable to Google Cloud
├── version_7_mcp_a2a_master/ # Production-ready masterclass project with MCP + A2A orchestration
```

---

## 𞿦 Version Overview

### ✅ `version_1_simple`

A beginner-friendly demo that uses Flask to create a basic A2A server agent (`TellTimeAgent`) and a client that:

* Fetches the agent card from the `/.well-known/agent.json` endpoint
* Sends a simple task to `/tasks/send`
* Receives a time-based response

﹖→ [Explore the folder](./version_1_simple/)

### 🚀 `version_2_adk_agent`

A more advanced version using **Google's ADK (Agent Development Kit)** to implement a fully functional Gemini-powered A2A agent.

* Integrates memory, sessions, and artifacts
* Uses ADK runners and LLM agents
* Structured with reusable components and aligned with A2A's JSON-RPC model

﹖→ [Explore the folder](./version_2_adk_agent/)

### 🌐 `version_3_multi_agent`

A multi-agent orchestration example demonstrating:

* Dynamic discovery of TellTimeAgent and GreetingAgent via a registry
* An OrchestratorAgent that routes user queries to the appropriate child agent
* A CLI (`cmd.py`) for seamless end-to-end testing

﹖→ [Explore the folder](./version_3_multi_agent/)

### 🔄 `version_4_multi_agent_mcp`

A cutting-edge integration combining Google’s A2A protocol with Anthropic’s MCP (Model Context Protocol):

* **A2A Protocol** – Agents discover each other via JSON-RPC and call one another’s skills.
* **MCP Integration** – Dynamically discover and load external MCP servers, exposing each tool as a callable function.
* **Orchestrator Agent** – A central LLM-powered router that decides whether to delegate to a child agent or invoke an MCP tool.
* **Modular & Extensible** – Simply update a registry or config to add new A2A agents or MCP servers.

﹖→ [Explore the folder](./version_4_multi_agent_mcp/)

### 💡 `version_4p01_with_vision_agent`

An enhanced version of `version_4_multi_agent_mcp` that adds support for a **Gemini-based VisionAgent**:

* Accepts image input via local file path or URL
* Uses Google ADK's multimodal capabilities
* Integrates cleanly into the existing A2A and MCP architecture

﹖→ [Explore the folder](./version_4p01_with_vision_agent/)

### 📊 `version_5_a2a_sdk`

An educational minimal setup using the official **A2A Python SDK** with LangChain + Gemini.

* One agent (`TellTimeAgent`) with time tool
* One async client
* Streaming + multi-turn + structured response support
* Ideal starting point for learning A2A SDK fundamentals

﹖→ [Explore the folder](./version_5_a2a_sdk/)

### 🚀 `version_6_docker_vision_agent`

A production-style deployment of a Gemini-based VisionAgent in a Docker container:

* Fully Dockerized architecture for isolated builds
* Local testing using `curl` to hit the vision agent endpoint
* One-line deployment to **Google Cloud Run**
* Supports volume-mounted images + container-path resolution

﹖→ [Explore the folder](./version_6_docker_vision_agent/)

### 📆 `version_7_mcp_a2a_master`

Build a production-ready multi-agent orchestration system using the Model Context Protocol (MCP) and Agent-to-Agent (A2A) communication.

This is a **coding master class**. Please refer to the videos for overview:

* **MCP Overview**: [https://www.youtube.com/watch?v=lUs2wrlazwM\&list=PL6tW9BrhiPTCDteflzehKS6Cn3a79-iCs](https://www.youtube.com/watch?v=lUs2wrlazwM&list=PL6tW9BrhiPTCDteflzehKS6Cn3a79-iCs)
* **A2A Overview**: [https://www.youtube.com/watch?v=0bgrPco8Wfw\&list=PL6tW9BrhiPTCKTXXJAwigi7QDNpA7t4Ip](https://www.youtube.com/watch?v=0bgrPco8Wfw&list=PL6tW9BrhiPTCKTXXJAwigi7QDNpA7t4Ip)

﹖→ [Explore the folder](./version_7_mcp_a2a_master/mcp_a2a_master/)

#### 📆 Project Features:

* STDIO and Streamable HTTP MCP servers
* Agent discovery and registration
* Task orchestration with A2A-compatible agents
* A working host agent delegating to remote agents
* Command-line interface for interacting with the system
* Clear folder structure and reusable utilities

#### 🛠️ Tech Requirements:

* Python 3.11+
* `uv` (Universal Virtualenv tool)


#### 🚀 DISCOUNTED COURSES

* [MCP & A2A Udemy Course](https://www.udemy.com/course/modelcontextprotocol/?couponCode=DISCOUNT479) – Completion certificate, practice questions, Q\&A
* [Google ADK Udemy Course](https://www.udemy.com/course/google-adk-agent-development-kit-mac-windows-ubuntu/?couponCode=DISCOUNT479) – Certificate, bite-sized lectures

---

## 🧪 Running the Code

Each version contains its own `README.md` file with detailed instructions on:

* Setting up Python environments
* Installing dependencies
* Running the server and client

Make sure to check the respective version folder before you begin!

---

## 🛠️ Future Plans

* Add streaming support via SSE and `tasks/sendSubscribe`
* Add push notification samples
* Add more ADK agent variants with different skills

Stay tuned and ⭐ star the repo if you find it useful!

---

## 📜 License

This repository is licensed under the **GNU General Public License v3.0**.
See the [LICENSE](./LICENSE) file for full details.

---

Happy building with A2A! 🛠

# version_6_docker_vision_agent

🌟 **Purpose**  
This version demonstrates how to dockerize and deploy a Gemini-based Vision Agent using Google Cloud Run. It builds on earlier multi-agent A2A + MCP architectures by showing how to wrap a vision agent into a Docker container and run it locally or remotely on GCP.

---

## 🚀 Features

- **Gemini Vision Agent** – Accepts text+image input and generates a caption using `gemini-2.0-flash`
- **Dockerized Agent** – Package and run your agent in isolated containers
- **Cloud Run Deployment** – Easily deploy to Google Cloud Run
- **Port Mapping & Volume Mounting** – Full support for image path routing
- **Modular Codebase** – Includes models, server logic, and agent logic in a clean structure

---

## 📦 Project Structure

```bash
version_6_docker_vision_agent/
├── Dockerfile
├── README.md
├── agents/
│   └── vision_agent/
│       ├── __main__.py
│       ├── agent.py
│       ├── image_samples_ai_generated/
│       │   ├── busstop.png
│       │   ├── butterfly.png
│       │   ├── computer.png
│       │   └── rainbow.png
│       └── task_manager.py
├── main.py
├── models/
│   ├── agent.py
│   ├── json_rpc.py
│   ├── request.py
│   └── task.py
├── pyproject.toml
└── server/
    ├── server.py
    └── task_manager.py
````

---

## 🛠️ Prerequisites

* Python 3.11+
* Docker installed locally
* Google Cloud account with `gcloud` CLI configured
* Valid `GOOGLE_API_KEY` for Gemini models

---

## 🧪 Local: Build, Run, Test

### 🔨 Build Docker Image Locally

```bash
docker build --platform linux/amd64 --no-cache -t vision_agent_docker .
```

### ▶️ Run the Docker Container Locally

```bash
docker run --rm -p 10003:10003 \
  -v /absolute/path/to/image_samples_ai_generated:/root/image_samples_ai_generated \
  vision_agent_docker
```

### 🔁 Send a Test Request

```bash
curl -X POST http://localhost:10003/ \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "test-1",
    "method": "tasks/send",
    "params": {
      "id": "task-123",
      "sessionId": "session-abc",
      "message": {
        "role": "user",
        "parts": [
          {
            "type": "text",
            "text": "Describe the image || /root/image_samples_ai_generated/computer.png"
          }
        ]
      },
      "historyLength": null,
      "metadata": null
    }
  }'
```

---

## ☁️ Cloud: Build, Push, Deploy, Test

### 🧱 Build Docker Image with Tag for GCP

```bash
docker build --platform linux/amd64 --no-cache -t gcr.io/YOUR_PROJECT_ID/vision-agent-docker .
```

### 📤 Push Docker Image to Google Container Registry

```bash
docker push gcr.io/YOUR_PROJECT_ID/vision-agent-docker
```

### 🚀 Deploy to Google Cloud Run

```bash
gcloud run deploy vision-agent-docker \
  --image gcr.io/YOUR_PROJECT_ID/vision-agent-docker \
  --platform managed \
  --region asia-south1 \
  --port 10003 \
  --allow-unauthenticated
```

🔒 **Note**: `--allow-unauthenticated` is used for demo access. Once tested, revoke or delete this service for security.

### 🌐 Test Deployed Vision Agent

```bash
curl -X POST https://YOUR_CLOUD_RUN_URL \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "test-1",
    "method": "tasks/send",
    "params": {
      "id": "task-123",
      "sessionId": "session-abc",
      "message": {
        "role": "user",
        "parts": [
          {
            "type": "text",
            "text": "Describe the image || /app/agents/vision_agent/image_samples_ai_generated/computer.png"
          }
        ]
      },
      "historyLength": null,
      "metadata": null
    }
  }'
```

---

## 🧹 Delete Service and Clean Up

### 🚫 Delete the Cloud Run Service

```bash
gcloud run services list --region asia-south1 
gcloud run services delete vision-agent-docker --region asia-south1
```

### 🗑️ Delete the Container Image from GCP

```bash
gcloud container images list-tags gcr.io/YOUR_PROJECT_ID/vision-agent-docker
gcloud container images delete gcr.io/YOUR_PROJECT_ID/vision-agent-docker@sha256:YOUR_DIGEST_ID --force-delete-tags
```

---

## ✨ More Resources

* [The AI Language Course on Udemy](https://www.udemy.com/course/modelcontextprotocol/?referralCode=6FADE0F85C5DB97203C6)
* [More on A2A Protocol (YouTube Playlist)](https://www.youtube.com/playlist?list=PL6tW9BrhiPTCKTXXJAwigi7QDNpA7t4Ip)

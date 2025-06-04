# -----------------------------------------------------------------------------
# 🐍 Base Image: Start from a minimal Python 3.11 image (Debian-based slim variant)
# -----------------------------------------------------------------------------
FROM python:3.11-slim

# -----------------------------------------------------------------------------
# 🐚 Use bash as the default shell so we can use `source` and other bash features
# (By default, Debian uses /bin/sh which doesn't support `source`)
# -----------------------------------------------------------------------------
SHELL ["/bin/bash", "-c"]

# -----------------------------------------------------------------------------
# 📁 Set working directory inside the container to /app
# All commands will now run from this directory
# -----------------------------------------------------------------------------
WORKDIR /app

# -----------------------------------------------------------------------------
# 🔧 Install essential system dependencies
# - `curl`: Needed to download `uv` (a modern Python package manager)
# - `--no-install-recommends`: Keeps image size smaller by skipping optional packages
# -----------------------------------------------------------------------------
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \

    # 📥 Download and install `uv` from the official Astral script
    curl -Ls https://astral.sh/uv/install.sh | bash && \

    # ✅ Debug prints to verify where `uv` was installed
    echo "✅ uv installed at: $(find /root/.local/bin -name uv)" && \
    echo "🔍 PATH before: $PATH" && \

    # ➕ Temporarily add `uv` to PATH for this RUN step
    export PATH="/root/.local/bin:$PATH" && \
    echo "🧭 PATH after: $PATH" && \

    # 🧪 Verify that `uv` is working
    /root/.local/bin/uv --version && \

    # 🧹 Clean up apt cache to reduce image size
    apt-get clean && rm -rf /var/lib/apt/lists/*

# -----------------------------------------------------------------------------
# 🛠️ Add uv to PATH permanently for all future Docker steps
# (This ensures `uv` is found even without specifying the full path)
# -----------------------------------------------------------------------------
ENV PATH="/root/.local/bin:$PATH"

# -----------------------------------------------------------------------------
# 📦 Copy all files from your local directory (where Docker build runs)
# into the container's /app directory (set earlier via WORKDIR)
# -----------------------------------------------------------------------------
COPY . /app

# -----------------------------------------------------------------------------
# 🐍 Create and activate a virtual environment inside the container
# - `uv venv`: Initializes a `.venv` folder
# - `source .venv/bin/activate`: Activates the environment
# - `uv sync --all-groups`: Installs dependencies from pyproject.toml
# - `uv sync --upgrade`: Ensures latest compatible versions are installed
# -----------------------------------------------------------------------------
RUN uv venv && \
    source .venv/bin/activate && \
    uv sync --all-groups && \
    uv sync --upgrade

# -----------------------------------------------------------------------------
# 📡 Expose port 10003 so Docker knows which port the container serves traffic on
# Note: This does not publish the port — just documents it
# -----------------------------------------------------------------------------
EXPOSE 10003

# -----------------------------------------------------------------------------
# 🚀 Default command to run the server when container starts
# - `uv run`: Executes the command inside the activated virtual environment
# - `-m agents.vision_agent`: Runs the module `agents/vision_agent.py`
# - `--host 0.0.0.0`: Binds to all network interfaces (needed for Docker/GCP)
# - `--port 10003`: Runs the service on port 10003
# -----------------------------------------------------------------------------
CMD ["uv", "run", "python3", "-m", "agents.vision_agent", "--host", "0.0.0.0", "--port", "10003"]
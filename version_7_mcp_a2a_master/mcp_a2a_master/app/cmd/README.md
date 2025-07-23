# CMD App

## Overview

The CMD App is a command-line interface (CLI) that serves as the primary user interface for interacting with the multi-agent system. It allows users to connect to the Host Agent, issue commands, and monitor the system's activity.

## Key Features

*   **Interactive Shell:** The CMD App provides an interactive shell where users can type commands and receive immediate feedback.
*   **Host Agent Communication:** The app connects to the Host Agent to send commands and receive responses. This allows users to control the behavior of the multi-agent system.
*   **System Monitoring:** The CMD App can be used to monitor the logs and status of the various agents and servers in the system, providing a real-time view of the system's operations.

## How to Run

To run the CMD App, execute the following command from the root of the project:

```bash
uv run python3 -m app.cmd.cmd
```

## Interaction with Other Components

*   **Host Agent:** The CMD App's primary interaction is with the Host Agent. It sends user commands to the Host Agent and displays the results.
# Website Builder Simple Agent

## Overview

The Website Builder Simple Agent is a specialized agent that, as its name suggests, is responsible for creating simple websites. It receives instructions from the Host Agent and uses its capabilities to generate the necessary HTML, CSS, and JavaScript files to construct a basic website.

## Key Responsibilities

*   **Website Generation:** The agent's primary function is to generate the files and content for a simple website based on the specifications provided by the Host Agent.
*   **A2A Communication:** The agent communicates with the Host Agent using the A2A protocol to receive tasks and send back the results of its work.
*   **Task Execution:** The agent executes the tasks delegated to it by the Host Agent. This may involve creating files, writing content, and structuring the website.

## How to Run

To run the Website Builder Simple Agent, execute the following command from the root of the project:

```bash
uv run python3 -m agents.website_builder_simple
```

## Interaction with Other Components

*   **Host Agent:** The Website Builder Simple Agent receives tasks from the Host Agent and reports back its progress and results. It operates under the direction of the Host Agent.
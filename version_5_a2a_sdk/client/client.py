# =============================================================================
# client/client.py
# =============================================================================
# Purpose:
# This file defines a dynamic async client built on top of the official
# A2A Python SDK. It can:
# - Detect agent capabilities (streaming or not)
# - Send queries in a loop
# - Handle single-turn or multi-turn conversations
# - Automatically pick between streaming and non-streaming flows
# =============================================================================

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
import asyncio                      # Provides support for asynchronous programming and I/O operations
import json                         # Allows encoding and decoding JSON data
import traceback                    # Prints detailed tracebacks in case of errors
from uuid import uuid4              # Generates unique message IDs
from typing import Any              # Allows function arguments and variables to accept any type

import click                        # Library to easily create command-line interfaces
import httpx                        # Async HTTP client for sending requests to agents
from rich import print as rprint    # Enhanced print function to support colors and formatting
from rich.syntax import Syntax      # Used to highlight JSON output in the terminal

# Import the official A2A SDK client and related types
from a2a.client import A2AClient
from a2a.types import (
    AgentCard,                      # Metadata about the agent
    SendMessageRequest,             # For sending regular (non-streaming) messages
    SendStreamingMessageRequest,    # For sending streaming messages
    MessageSendParams,              # Structure to hold message content
    SendMessageSuccessResponse,     # Represents a successful response from the agent
    Task,                           # Task object representing the agent's work unit
    TaskState,                      # Enum describing current task state (working, complete, etc.)
    GetTaskRequest,                 # Used to request status of a task
    TaskQueryParams,                # Parameters needed to fetch a specific task
)

# -----------------------------------------------------------------------------
# Helper: Create a message payload in expected A2A format
# -----------------------------------------------------------------------------
def build_message_payload(text: str, task_id: str | None = None, context_id: str | None = None) -> dict[str, Any]:
    # Constructs a dictionary payload that matches A2A message format
    return {
        "message": {
            "role": "user",  # The role of the message sender
            "parts": [{"kind": "text", "text": text}],  # The actual message content
            "messageId": uuid4().hex,  # Unique message ID for tracking
            **({"taskId": task_id} if task_id else {}),  # Include taskId only if it's a follow-up
            **({"contextId": context_id} if context_id else {}),  # Include contextId for continuity
        }
    }

# -----------------------------------------------------------------------------
# Helper: Pretty print JSON objects using syntax coloring
# -----------------------------------------------------------------------------
def print_json_response(response: Any, title: str) -> None:
    # Displays a formatted and color-highlighted view of the response
    print(f"\n=== {title} ===")  # Section title for clarity
    try:
        if hasattr(response, "root"):  # Check if response is wrapped by SDK
            data = response.root.model_dump(mode="json", exclude_none=True)
        else:
            data = response.model_dump(mode="json", exclude_none=True)

        json_str = json.dumps(data, indent=2, ensure_ascii=False)  # Convert dict to pretty JSON string
        syntax = Syntax(json_str, "json", theme="monokai", line_numbers=False)  # Apply syntax highlighting
        rprint(syntax)  # Print it with color
    except Exception as e:
        # Print fallback text if something fails
        rprint(f"[red bold]Error printing JSON:[/red bold] {e}")
        rprint(repr(response))

# -----------------------------------------------------------------------------
# Handles sending one non-streaming message and optionally a follow-up
# -----------------------------------------------------------------------------
async def handle_non_streaming(client: A2AClient, text: str):
    # Build and send the first message
    request = SendMessageRequest(params=MessageSendParams(**build_message_payload(text)))
    result = await client.send_message(request)  # Wait for agent reply
    print_json_response(result, "Agent Reply")  # Print the reply

    # If agent needs more input, prompt user again
    if isinstance(result.root, SendMessageSuccessResponse):
        task = result.root.result  # Extract task
        if task.status.state == TaskState.input_required:
            follow_up = input("\U0001F7E1 Agent needs more input. Your reply: ")
            follow_up_req = SendMessageRequest(
                params=MessageSendParams(**build_message_payload(follow_up, task.id, task.contextId))
            )
            follow_up_resp = await client.send_message(follow_up_req)
            print_json_response(follow_up_resp, "Follow-up Response")

# -----------------------------------------------------------------------------
# Handles streaming message and recursively continues if more input is needed
# -----------------------------------------------------------------------------
async def handle_streaming(client: A2AClient, text: str, task_id: str | None = None, context_id: str | None = None):
    # Construct streaming request payload
    request = SendStreamingMessageRequest(params=MessageSendParams(**build_message_payload(text, task_id, context_id)))

    # Track latest task/context ID to support multi-turn
    latest_task_id = None
    latest_context_id = None
    input_required = False

    # Process each streamed update
    async for update in client.send_message_streaming(request):
        print_json_response(update, "Streaming Update")  # Print each update as it comes

        # Extract context/task from current update
        if hasattr(update.root, "result"):
            result = update.root.result
            if hasattr(result, "contextId"):
                latest_context_id = result.contextId
            if hasattr(result, "status") and result.status.state == TaskState.input_required:
                latest_task_id = result.taskId
                input_required = True

    # If input was required, get response from user and continue conversation
    if input_required and latest_task_id and latest_context_id:
        follow_up = input("\U0001F7E1 Agent needs more input. Your reply: ")
        await handle_streaming(client, follow_up, latest_task_id, latest_context_id)

# -----------------------------------------------------------------------------
# Loop for querying the agent repeatedly
# -----------------------------------------------------------------------------
async def interactive_loop(client: A2AClient, supports_streaming: bool):
    print("\nEnter your query below. Type 'exit' to quit.")  # Print instructions for user
    while True:
        query = input("\n\U0001F7E2 Your query: ").strip()  # Get user input
        if query.lower() in {"exit", "quit"}:
            print("\U0001F44B Exiting...")  # Say goodbye
            break
        # Choose path based on agent's capability
        if supports_streaming:
            await handle_streaming(client, query)
        else:
            await handle_non_streaming(client, query)

# -----------------------------------------------------------------------------
# Command-line entry point
# -----------------------------------------------------------------------------
@click.command()
@click.option("--agent-url", default="http://localhost:10000", help="URL of the A2A agent to connect to")
def main(agent_url: str):
    asyncio.run(run_main(agent_url))  # Launch async event loop with provided agent URL

# -----------------------------------------------------------------------------
# Async runner: sets up client, agent card, and launches the loop
# -----------------------------------------------------------------------------
async def run_main(agent_url: str):
    print(f"Connecting to agent at {agent_url}...")  # Let user know we're starting connection
    try:
        async with httpx.AsyncClient() as session:  # Use async context to keep session open
            client = await A2AClient.get_client_from_agent_card_url(session, agent_url)  # Create A2A client
            client.httpx_client.timeout = 60  # Increase timeout for long operations

            res = await session.get(f"{agent_url}/.well-known/agent.json")  # Get agent metadata
            agent_card = AgentCard.model_validate(res.json())  # Validate the structure of the metadata
            supports_streaming = agent_card.capabilities.streaming  # Check if agent can stream

            rprint(f"[green bold]✅ Connected. Streaming supported:[/green bold] {supports_streaming}")  # Confirm success
            await interactive_loop(client, supports_streaming)  # Start conversation loop

    except Exception:
        traceback.print_exc()  # Show full error trace
        print("❌ Failed to connect or run. Ensure the agent is live and reachable.")  # Friendly error message

# -----------------------------------------------------------------------------
# Execute main only when run as script
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    main()  # Run main CLI logic

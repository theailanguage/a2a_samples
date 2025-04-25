# =============================================================================
# server.py
# =============================================================================
# 📌 Purpose:
# This file defines a very simple A2A (Agent-to-Agent) server.
# It supports:
# - Receiving task requests via POST ("/")
# - Letting clients discover the agent's details via GET ("/.well-known/agent.json")
# NOTE: It does not support streaming or push notifications in this version.
# =============================================================================


# -----------------------------------------------------------------------------
# 🧱 Required Imports
# -----------------------------------------------------------------------------

# 🌐 Starlette is a lightweight web framework for building ASGI applications
from starlette.applications import Starlette            # To create our web app
from starlette.responses import JSONResponse            # To send responses as JSON
from starlette.requests import Request                  # Represents incoming HTTP requests

# 📦 Importing our custom models and logic
from models.agent import AgentCard                      # Describes the agent's identity and skills
from models.request import A2ARequest, SendTaskRequest  # Request models for tasks
from models.json_rpc import JSONRPCResponse, InternalError  # JSON-RPC utilities for structured messaging
from agents.google_adk import task_manager              # Our actual task handling logic (Gemini agent)

# 🛠️ General utilities
import json                                              # Used for printing the request payloads (for debugging)
import logging                                           # Used to log errors and info messages
logger = logging.getLogger(__name__)                     # Setup logger for this file

# 🕒 datetime import for serialization
from datetime import datetime

# 📦 Encoder to help convert complex data like datetime into JSON
from fastapi.encoders import jsonable_encoder


# -----------------------------------------------------------------------------
# 🔧 Serializer for datetime
# -----------------------------------------------------------------------------
def json_serializer(obj):
    """
    This function can convert Python datetime objects to ISO strings.
    If you try to serialize a type it doesn't know, it will raise an error.
    """
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


# -----------------------------------------------------------------------------
# 🚀 A2AServer Class: The Core Server Logic
# -----------------------------------------------------------------------------
class A2AServer:
    def __init__(self, host="0.0.0.0", port=5000, agent_card: AgentCard = None, task_manager: task_manager = None):
        """
        🔧 Constructor for our A2AServer

        Args:
            host: IP address to bind the server to (default is all interfaces)
            port: Port number to listen on (default is 5000)
            agent_card: Metadata that describes our agent (name, skills, capabilities)
            task_manager: Logic to handle the task (using Gemini agent here)
        """
        self.host = host
        self.port = port
        self.agent_card = agent_card
        self.task_manager = task_manager

        # 🌐 Starlette app initialization
        self.app = Starlette()

        # 📥 Register a route to handle task requests (JSON-RPC POST)
        self.app.add_route("/", self._handle_request, methods=["POST"])

        # 🔎 Register a route for agent discovery (metadata as JSON)
        self.app.add_route("/.well-known/agent.json", self._get_agent_card, methods=["GET"])

    # -----------------------------------------------------------------------------
    # ▶️ start(): Launch the web server using uvicorn
    # -----------------------------------------------------------------------------
    def start(self):
        """
        Starts the A2A server using uvicorn (ASGI web server).
        This function will block and run the server forever.
        """
        if not self.agent_card or not self.task_manager:
            raise ValueError("Agent card and task manager are required")

        # Dynamically import uvicorn so it’s only loaded when needed
        import uvicorn
        uvicorn.run(self.app, host=self.host, port=self.port)

    # -----------------------------------------------------------------------------
    # 🔎 _get_agent_card(): Return the agent’s metadata (GET request)
    # -----------------------------------------------------------------------------
    def _get_agent_card(self, request: Request) -> JSONResponse:
        """
        Endpoint for agent discovery (GET /.well-known/agent.json)

        Returns:
            JSONResponse: Agent metadata as a dictionary
        """
        return JSONResponse(self.agent_card.model_dump(exclude_none=True))

    # -----------------------------------------------------------------------------
    # 📥 _handle_request(): Handle incoming POST requests for tasks
    # -----------------------------------------------------------------------------
    async def _handle_request(self, request: Request):
        """
        This method handles task requests sent to the root path ("/").

        - Parses incoming JSON
        - Validates the JSON-RPC message
        - For supported task types, delegates to the task manager
        - Returns a response or error
        """
        try:
            # Step 1: Parse incoming JSON body
            body = await request.json()
            print("\n🔍 Incoming JSON:", json.dumps(body, indent=2))  # Log input for visibility

            # Step 2: Parse and validate request using discriminated union
            json_rpc = A2ARequest.validate_python(body)

            # Step 3: If it’s a send-task request, call the task manager to handle it
            if isinstance(json_rpc, SendTaskRequest):
                result = await self.task_manager.on_send_task(json_rpc)
            else:
                raise ValueError(f"Unsupported A2A method: {type(json_rpc)}")

            # Step 4: Convert the result into a proper JSON response
            return self._create_response(result)

        except Exception as e:
            logger.error(f"Exception: {e}")
            # Return a JSON-RPC compliant error response if anything fails
            return JSONResponse(
                JSONRPCResponse(id=None, error=InternalError(message=str(e))).model_dump(),
                status_code=400
            )

    # -----------------------------------------------------------------------------
    # 🧾 _create_response(): Converts result object to JSONResponse
    # -----------------------------------------------------------------------------
    def _create_response(self, result):
        """
        Converts a JSONRPCResponse object into a JSON HTTP response.

        Args:
            result: The response object (must be a JSONRPCResponse)

        Returns:
            JSONResponse: Starlette-compatible HTTP response with JSON body
        """
        if isinstance(result, JSONRPCResponse):
            # jsonable_encoder automatically handles datetime and UUID
            return JSONResponse(content=jsonable_encoder(result.model_dump(exclude_none=True)))
        else:
            raise ValueError("Invalid response type")

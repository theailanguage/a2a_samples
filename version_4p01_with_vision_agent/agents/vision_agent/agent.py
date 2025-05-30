# =============================================================================
# agent.py
# =============================================================================
# 🎯 Purpose:
# This file defines the GeminiVisionAgent class, which uses Google's Gemini model
# to answer questions about images given as file paths or URLs.
# =============================================================================

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

import os  # Provides functions to interact with the operating system
from urllib.parse import urlparse  # Helps break down URLs into components
from pathlib import Path  # Provides an object-oriented way to work with file paths

# Import the Gemini LLM (large language model) agent class from the ADK
from google.adk.agents.llm_agent import LlmAgent

# Runner is responsible for coordinating the agent, memory, session, and artifacts
from google.adk.runners import Runner

# In-memory session service manages chat sessions in memory
from google.adk.sessions import InMemorySessionService

# In-memory memory service stores prior conversation context in memory
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService

# In-memory artifact service stores files (like images) temporarily in RAM
from google.adk.artifacts import InMemoryArtifactService

# Types provides helper structures for inputs/outputs (like Part, Content, Blob)
from google.genai import types

# Loads environment variables from a .env file
from dotenv import load_dotenv

# aiohttp is an async library for making HTTP requests (used to fetch remote images)
import aiohttp

# -----------------------------------------------------------------------------
# Load environment variables from .env (e.g., GOOGLE_API_KEY)
# -----------------------------------------------------------------------------

load_dotenv()

# -----------------------------------------------------------------------------
# GeminiVisionAgent Class
# -----------------------------------------------------------------------------

class GeminiVisionAgent:

    # Declare which content types this agent accepts by default
    SUPPORTED_CONTENT_TYPES = ["text", "text/plain"]

    def __init__(self):
        # Print a message during initialization
        print("[Init] Initializing GeminiVisionAgent...")

        # Build the actual LLM agent object (Gemini model)
        self._agent = self._build_agent()

        # Give a user ID to associate session and memory
        self._user_id = "vision_agent_user"

        # Create a Runner object that manages the agent + all supporting services
        self._runner = Runner(
            app_name=self._agent.name,  # Use the agent's name as app identifier
            agent=self._agent,  # The Gemini agent to use
            artifact_service=InMemoryArtifactService(),  # Store uploaded files in memory
            session_service=InMemorySessionService(),    # Store sessions in memory
            memory_service=InMemoryMemoryService(),      # Store chat history in memory
        )

        print("[Init] Initialization complete.\n")

    def _build_agent(self) -> LlmAgent:
        # Print during agent construction
        print("[BuildAgent] Building Gemini LLM agent...")

        # Create a Gemini agent using a specific model version and description
        agent = LlmAgent(
            model="gemini-2.0-flash",  # Gemini model version (vision-capable)
            name="gemini_vision_agent",  # Internal name for the agent
            description="Answers questions about images from file or URL.",  # Description shown in UI or agent directory
            instruction="Analyze the image and answer the user's question based on its content."  # System-level prompt
        )

        print("[BuildAgent] Agent built successfully.\n")
        return agent

    async def _load_image_part(self, file_path_or_url: str) -> types.Part:
        """
        Loads image content from a local file or a remote URL and returns a `types.Part` object,
        which wraps the image data along with its MIME type (e.g., image/jpeg or image/png).

        Args:
            file_path_or_url (str): The file path (local) or URL (remote) of the image.

        Returns:
            types.Part: A Gemini-compatible Part containing the image as inline binary data.
        """

        print(f"[ImageLoader] Loading image from: {file_path_or_url}")

        try:
            # -------------------------------------------------------------
            # Step 1: Determine the correct MIME type from the file extension
            # -------------------------------------------------------------
            def get_mime_type(path: str) -> str:
                """
                Infers the MIME type based on file extension (jpg, jpeg, png).
                Raises an error if the format is not supported.
                """
                ext = path.lower().split(".")[-1]  # Get the last part after the dot, e.g., 'jpg'
                if ext == "jpg" or ext == "jpeg":
                    return "image/jpeg"
                elif ext == "png":
                    return "image/png"
                else:
                    raise ValueError("Unsupported image format. Please use JPG or PNG.")

            # -------------------------------------------------------------
            # Step 2: If it's a URL (starts with http or https)
            # -------------------------------------------------------------
            if urlparse(file_path_or_url).scheme in ("http", "https"):
                print("[ImageLoader] Detected remote URL. Attempting to fetch via HTTP...")

                # Determine MIME type from URL string
                mime_type = get_mime_type(file_path_or_url)

                # Start an asynchronous HTTP session
                async with aiohttp.ClientSession() as session:
                    # Send GET request to the URL
                    async with session.get(file_path_or_url) as resp:
                        print(f"[ImageLoader] HTTP status: {resp.status}")
                        if resp.status == 200:
                            # Read the image content into memory
                            data = await resp.read()
                            print("[ImageLoader] Remote image loaded successfully.")

                            # Wrap the image bytes inside a Part with MIME type
                            return types.Part(
                                inline_data=types.Blob(
                                    data=data,
                                    mime_type=mime_type
                                )
                            )
                        else:
                            raise Exception(f"Failed to load image from URL: HTTP {resp.status}")

            # -------------------------------------------------------------
            # Step 3: If it's a local file path
            # -------------------------------------------------------------
            else:
                # Expand ~ to full home path if used
                path = Path(file_path_or_url).expanduser()
                print(f"[ImageLoader] Interpreted as local path: {path}")
                print(f"[ImageLoader] Exists: {path.exists()}, Is File: {path.is_file()}")

                # Check that file actually exists and is a regular file
                if not path.exists() or not path.is_file():
                    raise FileNotFoundError(f"File does not exist: {path}")

                # Determine MIME type from the file extension
                mime_type = get_mime_type(str(path))

                # Open and read file bytes into memory
                with open(path, "rb") as f:
                    data = f.read()
                    print(f"[ImageLoader] Local image loaded successfully, size = {len(data)} bytes")

                    # Wrap the image data into a Gemini Part
                    return types.Part(
                        inline_data=types.Blob(
                            data=data,
                            mime_type=mime_type
                        )
                    )

        # -------------------------------------------------------------
        # Step 4: Handle errors
        # -------------------------------------------------------------
        except Exception as e:
            print(f"[ImageLoader] ERROR: {e}")
            # Wrap and re-raise the error with a clearer message
            raise RuntimeError(f"Image loading failed: {e}")
        
    async def invoke(self, query: str, session_id: str) -> str:
        # Log start of invocation
        print(f"\n[Invoke] New invocation with session_id={session_id}")
        print(f"[Invoke] Raw query: {query}")

        try:
            # Validate query format: must contain ||
            if "||" not in query:
                return "Invalid input format. Please provide '<question> || <file_path_or_url>'"

            # Split the input into question and image path
            user_question, image_path = query.split("||", 1)
            user_question = user_question.strip()  # Remove extra whitespace
            image_path = image_path.strip()

            print(f"[Invoke] Parsed question: '{user_question}'")
            print(f"[Invoke] Parsed image path/URL: '{image_path}'")

            try:
                # Try to load the image from path or URL
                image_part = await self._load_image_part(image_path)
            except Exception as e:
                # If image fails to load, return a message
                return f"[Image loading failed: {e}]"

            # Try to reuse an existing session (if exists)
            session = await self._runner.session_service.get_session(
                app_name=self._agent.name,
                user_id=self._user_id,
                session_id=session_id
            )

            # If session doesn't exist, create a new one
            if session is None:
                print("[Invoke] Creating new session...")
                session = await self._runner.session_service.create_session(
                    app_name=self._agent.name,
                    user_id=self._user_id,
                    session_id=session_id,
                    state={}  # Optional session state
                )
            else:
                print("[Invoke] Reusing existing session.")

            # Construct a Content object with the image and user query
            content = types.Content(
                role="user",  # Message is coming from user
                parts=[
                    image_part,  # First part: the image
                    types.Part.from_text(text=user_question)  # Second part: the question
                ]
            )

            print("[Invoke] Sending content to runner...")

            # Run the agent with this input and collect response
            last_event = None
            async for event in self._runner.run_async(
                user_id=self._user_id,
                session_id=session.id,
                new_message=content
            ):
                last_event = event  # Save the latest event as the result

            # Handle case where no response was returned
            if not last_event or not last_event.content or not last_event.content.parts:
                print("[Invoke] No response from model.")
                return "[No response generated.]"

            # Join all response text parts and return as single string
            result = "\n".join([p.text for p in last_event.content.parts if p.text])
            print(f"[Invoke] Agent response: {result}\n")
            return result

        except Exception as e:
            # Catch and return any unexpected errors
            print(f"[Invoke] ERROR: {e}")
            return f"[Agent invocation failed: {e}]"
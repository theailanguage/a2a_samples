# =============================================================================
# models/agent.py
# =============================================================================
# Purpose:
# This file defines the agent-related data models used throughout the Agent2Agent (A2A) system.
# These include:
# - Capabilities that an agent supports (e.g., streaming, push notifications)
# - Metadata about the agent itself (AgentCard)
# - Metadata for each skill the agent can perform (AgentSkill)
#
# These classes help describe the agent's identity, its features, and how it interacts
# with other agents or clients in a structured and consistent way.
# =============================================================================

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

# BaseModel is a powerful base class from Pydantic.
# It automatically validates and converts input data into Python types
from pydantic import BaseModel

# List type hint for declaring list fields
from typing import List


# -----------------------------------------------------------------------------
# AgentCapabilities
# -----------------------------------------------------------------------------
# This class defines what features or protocols the agent supports.
# These capabilities can be used by A2A clients or directories to understand how to interact with the agent.
class AgentCapabilities(BaseModel):
    # Indicates if the agent can send intermediate task results through streaming
    streaming: bool = False

    # Indicates if the agent can push updates via HTTP push/webhooks
    pushNotifications: bool = False

    # If enabled, the agent keeps track of the history of task state transitions (e.g., "started", "completed")
    # Useful for debugging or auditing
    stateTransitionHistory: bool = False


# -----------------------------------------------------------------------------
# AgentSkill
# -----------------------------------------------------------------------------
# This class defines metadata about a single skill that the agent offers.
# Each skill corresponds to a specific type of task the agent can perform.
class AgentSkill(BaseModel):
    # Unique identifier for the skill (e.g., "get_time")
    id: str

    # Human-readable name for the skill (e.g., "Get Current Time")
    name: str

    # Optional description to help users understand what the skill does
    description: str | None = None

    # Optional tags to help categorize or search for the skill (e.g., ["time", "clock"])
    tags: List[str] | None = None

    # Optional example phrases that this skill might respond to
    # Useful for interfaces that suggest user queries
    examples: List[str] | None = None

    # Optional list of supported input modes (e.g., ["text", "json"])
    inputModes: List[str] | None = None

    # Optional list of supported output modes (e.g., ["text", "image"])
    outputModes: List[str] | None = None

# -----------------------------------------------------------------------------
# AgentCard
# -----------------------------------------------------------------------------
# This class provides core metadata about an agent.
# This information can be shared with a directory service or other agents
# to describe what the agent does, where to reach it, and what capabilities it supports.
class AgentCard(BaseModel):
    # Human-readable name of the agent (e.g., "Time Teller")
    name: str

    # Description of the agent's purpose or use case
    description: str

    # URL where the agent is hosted (can be used to send requests to it)
    url: str

    # Semantic version of the agent (e.g., "1.0.0")
    version: str

    # The capabilities this agent supports (uses the AgentCapabilities model above)
    capabilities: AgentCapabilities

    # List of skills (as strings) this agent can perform
    # These are references to the full AgentSkill definitions, which might be fetched elsewhere
    skills: List[AgentSkill]

# Import the Flask class and utility functions from the flask package.
# Flask is a lightweight web framework used to build HTTP APIs and web servers in Python.
from flask import Flask, request, jsonify

# Import the datetime class from Python's built-in datetime module.
# We'll use this to get the current date and time.
from datetime import datetime

# Create a new Flask app instance.
# This initializes our server application so we can define endpoints on it.
app = Flask(__name__)

# ---------------------------------------
# Endpoint: Agent Card (Discovery Phase)
# ---------------------------------------

# Define an HTTP GET route for the well-known agent discovery path.
# According to the A2A spec, clients discover an agent by calling `/.well-known/agent.json`.
@app.route("/.well-known/agent.json", methods=["GET"])
def agent_card():
    # Return metadata about this agent in JSON format.
    # This includes the agent's name, description, base URL, version, and capabilities.
    return jsonify({
        "name": "TellTimeAgent",  # Human-readable name of the agent
        "description": "Tells the current time when asked.",  # Short summary of what the agent does
        "url": "http://localhost:5000",  # Where this agent is hosted (used by clients to send tasks)
        "version": "1.0",  # Version info for the agent
        "capabilities": {
            "streaming": False,           # Indicates that this agent does not support real-time streaming
            "pushNotifications": False    # Indicates that the agent does not send async push notifications
        }
    })

# ---------------------------------------
# Endpoint: Task Handling (tasks/send)
# ---------------------------------------

# Define an HTTP POST route at /tasks/send
# This is the main endpoint that A2A clients use to send a task to the agent.
@app.route("/tasks/send", methods=["POST"])
def handle_task():
    try:
        # Parse the incoming JSON payload into a Python dictionary.
        task = request.get_json()

        # Extract the task ID from the payload.
        # This uniquely identifies the task in the A2A protocol.
        task_id = task.get("id")

        # Extract the user message text from the first message part.
        # A2A represents messages as a list of "parts", where the first part usually contains text.
        user_message = task["message"]["parts"][0]["text"]

    # If the request doesn't match the expected structure, return a 400 error.
    except (KeyError, IndexError, TypeError):
        return jsonify({"error": "Invalid task format"}), 400

    # ---------------------------------------
    # Generate a response to the user message
    # ---------------------------------------

    # Get the current system time as a formatted string.
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Build the agent's response message text.
    reply_text = f"The current time is: {current_time}"

    # Return a properly formatted A2A task response.
    # This includes the original message and a new message from the agent.
    return jsonify({
        "id": task_id,  # Reuse the same task ID in the response
        "status": {"state": "completed"},  # Mark the task as completed
        "messages": [
            task["message"],  # Include the original user message for context
            {
                "role": "agent",              # This message is from the agent
                "parts": [{"text": reply_text}]  # Reply content in text format
            }
        ]
    })

# ---------------------------------------
# Run the Flask server
# ---------------------------------------

# This block runs the Flask app only if this script is executed directly.
# It starts a local development server on port 5000.
if __name__ == "__main__":
    app.run(port=5000)

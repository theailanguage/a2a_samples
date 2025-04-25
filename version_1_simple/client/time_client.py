# Import the requests library to send HTTP GET and POST requests.
# This allows the client to talk to the server over HTTP.
import requests

# Import the uuid module to generate unique task IDs.
# Each A2A task must have a unique ID.
import uuid

# ---------------------------------------
# Step 1 – Discover the Agent
# ---------------------------------------

# Define the base URL where the server agent is hosted.
# In this case, it runs locally on port 5000.
base_url = "http://127.0.0.1:5000"

# Use HTTP GET to fetch the agent's card from the well-known discovery endpoint.
res = requests.get(f"{base_url}/.well-known/agent.json")

# If the request fails (not status code 200), raise an error.
if res.status_code != 200:
    raise Exception("Failed to discover agent.")

# Parse the response JSON into a Python dictionary.
agent_info = res.json()

# Display some basic info about the discovered agent.
print(f"Connected to: {agent_info['name']} – {agent_info['description']}")

# ---------------------------------------
# Step 2 – Prepare a Task
# ---------------------------------------

# Generate a unique ID for this task using uuid4 (random UUID).
task_id = str(uuid.uuid4())

# Construct the A2A task payload as a Python dictionary.
# According to A2A spec, we need to include:
# - "id": the unique task ID
# - "message": an object with "role": "user" and a list of "parts" (in this case, text only)
task_payload = {
    "id": task_id,
    "message": {
        "role": "user",  # Indicates that the message is coming from the user
        "parts": [
            {"text": "What time is it?"}  # This is the question the user is asking
        ]
    }
}

# ---------------------------------------
# Step 3 – Send the Task to the Agent
# ---------------------------------------

# Send an HTTP POST request to the /tasks/send endpoint of the agent.
# We use the `json=` parameter so requests will serialize our dictionary as JSON.
response = requests.post(f"{base_url}/tasks/send", json=task_payload)

# If the server didn’t return a 200 OK status, raise an error.
if response.status_code != 200:
    raise Exception(f"Task failed: {response.text}")

# Parse the agent's JSON response into a Python dictionary.
response_data = response.json()

# ---------------------------------------
# Step 4 – Display the Agent's Response
# ---------------------------------------

# Extract the list of messages returned in the response.
# This typically includes both the user's message and the agent's reply.
messages = response_data.get("messages", [])

# If there are messages, extract and print the last one (agent’s response).
if messages:
    final_reply = messages[-1]["parts"][0]["text"]
    print("Agent says:", final_reply)
else:
    # If no messages were received, notify the user.
    print("No response received.")

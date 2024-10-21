import subprocess
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Use the service name 'rasa' to refer to the Rasa container
RASA_URL = "http://rasa:5005/webhooks/rest/webhook"

@app.route("/chat/", methods=["POST"])
def chat():
    user_message = request.json.get("message")
    response = requests.post(RASA_URL, json={"sender": "user", "message": user_message})
    
    # Handle response from Rasa
    if response.status_code == 200:
        return jsonify(response.json()), 200
    else:
        return jsonify({"error": "Failed to communicate with Rasa"}), 500


@app.route("/train/", methods=["POST"])
def train():
    try:
        # Trigger the Rasa training process
        result = subprocess.run(["rasa", "train"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Check if the training was successful
        if result.returncode == 0:
            return jsonify({"message": "Training complete", "status": "success"}), 200
        else:
            # If there was an error, return the error message
            return jsonify({"message": "Training complete", "status": "failed"}), 500
    except Exception as e:
        # Handle any other exceptions
        return jsonify({"message": "An error occured while training", "error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

from flask import Flask, request, jsonify
import os
import openai
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Set OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route('/translate/', methods=['POST'])
def translate_text():
    # Parse JSON from the request
    data = request.get_json()
    query = data.get("query")
    from_language = data.get("src_lang")
    to_language = data.get("target_lang")
    
    # Validate required fields
    if not query or not from_language or not to_language:
        return jsonify({"error": "Missing required parameters"}), 400
    
    try:
        # Use OpenAI's ChatCompletion for translation
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": f"Translate the following text from {from_language} to {to_language}."},
                {"role": "user", "content": query}
            ]
        )
        translate_text = response.choices[0].message['content']

        return jsonify({"translated_text": translate_text}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=1000)

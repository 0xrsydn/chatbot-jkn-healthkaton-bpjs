from flask import Flask, request, jsonify
from groq_translation import groq_translate
import os

app = Flask(__name__)

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
        # Call the Groq translation function
        translation = groq_translate(query, from_language, to_language)
        return jsonify({"translation": translation.dict()}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=1000)

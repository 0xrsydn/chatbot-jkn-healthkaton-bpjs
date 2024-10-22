from flask import Flask, request, jsonify
from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException

# Set seed for consistent results
DetectorFactory.seed = 0

app = Flask(__name__)

@app.route("/detect_lang/", methods=["POST"])
def detect_lang():
    try:
        # Get the text from the POST request
        data = request.json
        text = data.get("text", "")

        if not text:
            return jsonify({"error": "No text provided"}), 400

        # Detect the language
        lang = detect(text)
        return jsonify({"language": lang}), 200
    
    except LangDetectException as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "An error occurred"}), 500
    

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3030)
import re
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from aksharamukha import transliterate

app = Flask(__name__)
CORS(app)

GOOGLE_TRANSLATE_API_KEY = "AIzaSyAG5SrlVZT9iUBTFYLi15GEMZAfVR931Hs"

TAMIL_HINT_WORDS = {
    "vanakkam", "enna", "epdi", "iruka", "saptiya", "sapta",
    "seri", "illa", "unga", "inga", "po", "vara",
    "naan", "nee", "avanga", "namma"
}


def contains_tamil_script(text: str) -> bool:
    return any("\u0B80" <= ch <= "\u0BFF" for ch in text)


def transliterate_tamil(text: str) -> str:
    return transliterate.process("Tamil", "ISO", text)


def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def has_tamil_word(transliterated: str) -> bool:
    tokens = normalize(transliterated).split()
    return any(token in TAMIL_HINT_WORDS for token in tokens)


def detect_language_google(text: str) -> tuple:
    url = "https://translation.googleapis.com/language/translate/v2/detect"
    response = requests.post(
        url,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={"q": text, "key": GOOGLE_TRANSLATE_API_KEY},
        timeout=30
    )
    response.raise_for_status()
    data = response.json()["data"]["detections"][0][0]
    return data["language"], data["confidence"]


@app.route("/detect", methods=["POST"])
def detect():
    body = request.get_json(force=True)
    user_input = body.get("text", "").strip()

    if not user_input:
        return jsonify({"error": "No text provided"}), 400

    try:
        tamil_script = contains_tamil_script(user_input)
        translit = ""
        detection_input = user_input
        final_label = ""

        if tamil_script:
            translit = transliterate_tamil(user_input)
            if has_tamil_word(translit):
                detection_input = user_input
                final_label = "Tamil"
            else:
                detection_input = translit
                final_label = "English (Tamil Script)"
        else:
            detection_input = user_input
            code, _ = detect_language_google(detection_input)
            if code == "ta-Latn":
                final_label = "Tamil (Romanized)"
            else:
                final_label = "English"

        code, confidence = detect_language_google(detection_input)

        return jsonify({
            "tamil_script": tamil_script,
            "transliteration": translit,
            "detected_code": code,
            "final_label": final_label,
            "confidence": round(confidence, 4),
            "api_input": detection_input
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)

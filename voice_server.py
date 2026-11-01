import io
from flask import Flask, request, Response, jsonify
from flask_cors import CORS
from gtts import gTTS

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def home():
    return "Server is Awake and Running!", 200

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})

@app.route('/speak', methods=['POST'])
def speak():
    data = request.get_json(silent=True) or {}
    text = str(data.get('text', '')).strip()
    language = str(data.get('language', 'english')).lower()

    if not text:
        return jsonify({"error": "Text missing"}), 400

    lang_code = 'hi' if language == 'hindi' else 'en'

    try:
        tts = gTTS(text=text[:3000], lang=lang_code, slow=False)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return Response(fp.read(), mimetype="audio/mpeg")
    except Exception as e:
        print(f"[TTS ERROR]: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)
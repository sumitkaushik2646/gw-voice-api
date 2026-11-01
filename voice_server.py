import re
import asyncio
import edge_tts
from flask import Flask, request, Response, jsonify
from flask_cors import CORS

# Windows asyncio freeze fix
import os
if os.name == 'nt':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

app = Flask(__name__)
CORS(app)  # file:// se aane wali requests (origin "null") ke liye bhi chalega

VOICES = {
    "hindi": "hi-IN-MadhurNeural",
    "english": "en-US-ChristopherNeural",
}

# Emoji / markdown symbols jo TTS ko "No audio received" error de dete hain
_EMOJI = re.compile(
    "[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F000-\U0001F2FF\uFE0F\u200d]+",
    flags=re.UNICODE,
)

def clean_text(text: str) -> str:
    text = _EMOJI.sub(" ", text)
    text = re.sub(r"[*#_`~>|\[\]{}]", " ", text)   # markdown symbols
    text = re.sub(r"https?://\S+", " ", text)       # links
    text = re.sub(r"\s+", " ", text).strip()
    return text[:3000]                              # bahut lamba text avoid karo

async def synth(text: str, voice: str) -> bytes:
    """Audio seedha memory me banta hai - koi temp file nahi, koi cleanup nahi."""
    comm = edge_tts.Communicate(text, voice, rate="+5%")
    audio = bytearray()
    async for chunk in comm.stream():
        if chunk["type"] == "audio":
            audio.extend(chunk["data"])
    return bytes(audio)

# ---- NAYA CODE: UptimeRobot error theek karne ke liye ----
@app.route('/', methods=['GET'])
def home():
    return "Server is Awake and Running!", 200
# --------------------------------------------------------

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})

@app.route('/speak', methods=['POST'])
def speak():
    data = request.get_json(silent=True) or {}
    text = clean_text(str(data.get('text', '')))
    language = str(data.get('language', 'english')).lower()

    if not text:
        return jsonify({"error": "Text missing"}), 400

    voice = VOICES["hindi"] if language == "hindi" else VOICES["english"]

    try:
        audio = asyncio.run(synth(text, voice))
        if not audio:
            return jsonify({"error": "Empty audio received"}), 502
        return Response(audio, mimetype="audio/mpeg")
    except Exception as e:
        print(f"[TTS ERROR] {type(e).__name__}: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("===================================================")
    print("🚀 GW Voice Server is RUNNING on http://127.0.0.1:5000")
    print("===================================================")
    # debug=False: reloader band, warna server beech me restart ho jata hai
    app.run(host="127.0.0.1", port=5000, debug=False, threaded=True)
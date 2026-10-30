import os
import asyncio
import edge_tts
from flask import Flask, request, send_file
from flask_cors import CORS

app = Flask(__name__)
# CORS allow karta hai taaki aapki HTML file is API ko call kar sake
CORS(app) 

# Async function aawaz banane ke liye
async def generate_audio(text, voice, filename):
    communicate = edge_tts.Communicate(text, voice, rate="+5%")
    await communicate.save(filename)

@app.route('/speak', methods=['POST'])
def speak():
    data = request.json
    text = data.get('text', '')
    language = data.get('language', 'english')
    
    if not text:
        return {"error": "No text provided"}, 400
        
    # Language ke hisaab se premium voice set karein
    voice = "hi-IN-MadhurNeural" if language == "hindi" else "en-US-ChristopherNeural"
    filename = "temp_voice.mp3"
    
    # Audio generate karein
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
    loop.run_until_complete(generate_audio(text, voice, filename))
    
    # Audio file seedha browser ko bhej dega (Frontend khud play karega)
    return send_file(filename, mimetype="audio/mpeg")

if __name__ == '__main__':
    print("===================================================")
    print("🚀 GW Voice Server is RUNNING on http://127.0.0.1:5000")
    print("===================================================")
    app.run(port=5000, debug=True)
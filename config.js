// === JARVISH SMART VOICE CONFIG (LOCAL -> CLOUD -> BROWSER VOICE) ===
const CLOUD_API_URL = "https://gw-voice-api.onrender.com";
const LOCAL_API_URL = "http://127.0.0.1:5000";

// Ek server se audio mangta hai. Fail hone par exact wajah console me dikhata hai.
async function fetchAudio(baseUrl, text, lang, timeoutMs, label) {
    const ctrl = new AbortController();
    const timer = setTimeout(() => ctrl.abort(), timeoutMs);
    try {
        const res = await fetch(`${baseUrl}/speak`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: text, language: lang }),
            signal: ctrl.signal
        });
        if (!res.ok) {
            let detail = '';
            try { detail = await res.text(); } catch (_) {}
            console.warn(`[Voice] ${label} server error ${res.status}:`, detail);
            return null;
        }
        const blob = await res.blob();
        if (!blob || blob.size < 500) {
            console.warn(`[Voice] ${label} ne khali/chhota audio diya (${blob ? blob.size : 0} bytes)`);
            return null;
        }
        return blob;
    } catch (e) {
        console.warn(`[Voice] ${label} se connect nahi hua:`, e.name === 'AbortError' ? 'timeout' : e.message);
        return null;
    } finally {
        clearTimeout(timer);
    }
}

// Last fallback: browser ki apni awaaz (koi server nahi chahiye)
function speakWithBrowserVoice(text, lang, onDone) {
    if (!('speechSynthesis' in window)) return false;
    const u = new SpeechSynthesisUtterance(text);
    u.lang = lang === 'hindi' ? 'hi-IN' : 'en-US';
    const voices = window.speechSynthesis.getVoices();
    const match = voices.find(v => v.lang === u.lang) ||
                  voices.find(v => v.lang.startsWith(u.lang.slice(0, 2)));
    if (match) u.voice = match;
    u.rate = 1.05;
    u.onend = onDone;
    u.onerror = onDone;
    window.speechSynthesis.speak(u);
    return true;
}

async function triggerVoice(text) {
    if (typeof isMuted !== 'undefined' && isMuted) return;

    if (window.currentAudio) {
        window.currentAudio.pause();
        window.currentAudio.currentTime = 0;
        window.currentAudio = null;
    }
    if ('speechSynthesis' in window) { window.speechSynthesis.cancel(); }

    const orb = document.getElementById('jarvisOrb');
    const textEl = document.getElementById('statusText');
    const finish = () => {
        if (orb) orb.classList.remove('ai-speaking');
        if (textEl) textEl.innerText = "Online System";
    };

    if (orb) orb.classList.add('ai-speaking');
    if (textEl) textEl.innerText = "Speaking...";

    const cleanText = String(text || '')
        .replace(/<[^>]*>?/gm, ' ')
        .replace(/[*#_`\[\]()✔•🚀👇]/g, ' ')
        .replace(/\s+/g, ' ')
        .trim();

    if (!cleanText) { finish(); return; }

    const lang = typeof preferredLanguage !== 'undefined' ? preferredLanguage : 'english';

    // 1. Local server (band ho to turant fail hota hai, time waste nahi)
    let audioBlob = await fetchAudio(LOCAL_API_URL, cleanText, lang, 4000, 'Local');

    // 2. Cloud server (Render free plan so jata hai, isliye 10 sec wait)
    if (!audioBlob) {
        audioBlob = await fetchAudio(CLOUD_API_URL, cleanText, lang, 80000, 'Cloud');
    }

    // 3. Server se audio mila to play karo
    if (audioBlob) {
        const audioUrl = URL.createObjectURL(audioBlob);
        const audio = new Audio(audioUrl);
        window.currentAudio = audio;
        audio.onended = () => { finish(); URL.revokeObjectURL(audioUrl); };
        audio.onerror = () => { console.warn('[Voice] Audio file play nahi ho payi'); finish(); };
        try {
            await audio.play();
            return;
        } catch (e) {
            console.warn('[Voice] play() block hua (page par ek baar click karein):', e.message);
            // neeche browser voice try hogi
        }
    }

    // 4. Dono server fail -> browser ki awaaz
    console.warn('[Voice] Server audio nahi mila, browser voice use ho rahi hai');
    const ok = speakWithBrowserVoice(cleanText, lang, finish);
    if (!ok) {
        if (textEl) textEl.innerText = "Audio Error!";
        setTimeout(finish, 2000);
    }
}

// Kuch browsers me voices der se load hoti hain
if ('speechSynthesis' in window) { window.speechSynthesis.getVoices(); }
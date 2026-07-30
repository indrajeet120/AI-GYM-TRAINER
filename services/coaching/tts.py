from io import BytesIO
from gtts import gTTS
import threading


class TextToSpeech:
    def __init__(self):
        self.cache = {}
        self.lock = threading.Lock()

    def speak(self, text, lang="en"):
        if not text:
            return None

        cleaned = text.strip()
        if not cleaned:
            return None

        with self.lock:
            if cleaned in self.cache:
                return self.cache[cleaned]

        try:
            buffer = BytesIO()
            tts = gTTS(
                text=cleaned,
                lang=lang,
                tld="co.in",
                slow=False
            )
            tts.write_to_fp(buffer)
            buffer.seek(0)
            audio = buffer.read()

            with self.lock:
                self.cache[cleaned] = audio

            return audio

        except Exception as e:
            print("TTS Generation Error:", e)
            return None
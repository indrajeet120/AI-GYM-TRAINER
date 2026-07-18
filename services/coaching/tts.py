from io import BytesIO
from gtts import gTTS


class TextToSpeech:

    def __init__(self):
        self.cache = {}


    def speak(self, text, lang="en"):

        if not text:
            return None

        cleaned = text.strip()

        if not cleaned:
            return None


        # cache check
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

            self.cache[cleaned] = audio

            return audio


        except Exception as e:

            print("TTS ERROR:", e)
            return None
import io
import time
import hashlib
import threading
from queue import PriorityQueue

try:
    import pygame
    pygame.mixer.init()
    PYGAME_AVAILABLE = True
except Exception as e:
    PYGAME_AVAILABLE = False
    print("Pygame mixer not available, using browser audio:", e)


class AudioManager:
    """
    Thread-safe Singleton Audio & Voice Queue Manager.
    Dual-mode playback:
    1. Plays directly through system speakers via Pygame when running locally.
    2. Serves audio_bytes to Streamlit st.audio() for Streamlit Cloud browser playback.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(AudioManager, cls).__new__(cls)
                cls._instance._init_manager()
            return cls._instance

    def _init_manager(self):
        self.queue = PriorityQueue()
        self.cooldown_seconds = 3.5
        self.current_audio = None  # dict with audio_bytes, audio_id, text, expire_time
        self.recent_phrase_ids = []
        self.latest_spoken_text = "AI Coach ready!"
        self.lock = threading.Lock()

        # Start background queue processor worker thread
        self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker_thread.start()

    def estimate_duration(self, text):
        words = len(text.split())
        return max(2.2, (words / 2.5) + 0.6)

    def enqueue_speech(self, priority, text, audio_bytes):
        if not text or not audio_bytes:
            return False

        msg_id = hashlib.md5(text.encode("utf-8")).hexdigest()
        now = time.time()

        with self.lock:
            # Avoid repeating recent phrases
            if msg_id in self.recent_phrase_ids[-4:]:
                return False

            # Drop stale items if queue builds up
            if self.queue.qsize() > 3:
                temp = []
                while not self.queue.empty():
                    item = self.queue.get()
                    if item[0] <= 2 and (now - item[1]) < 5.0:
                        temp.append(item)
                for item in temp:
                    self.queue.put(item)

            item = {
                "priority": priority,
                "text": text,
                "audio_bytes": audio_bytes,
                "msg_id": msg_id,
                "timestamp": now,
            }
            self.queue.put((priority, now, item))
            return True

    def _worker_loop(self):
        while True:
            try:
                now = time.time()
                with self.lock:
                    # Clear current audio if speech + cooldown period finished
                    if self.current_audio and now >= self.current_audio["expire_time"]:
                        self.current_audio = None

                    # If slot is free and items are in queue
                    if self.current_audio is None and not self.queue.empty():
                        priority, ts, item = self.queue.get()
                        if (now - ts) <= 6.0:  # Valid within 6 seconds
                            duration = self.estimate_duration(item["text"])

                            # Native Pygame Speaker Playback (Local Execution)
                            if PYGAME_AVAILABLE:
                                try:
                                    fp = io.BytesIO(item["audio_bytes"])
                                    pygame.mixer.music.load(fp)
                                    pygame.mixer.music.play()
                                except Exception as pe:
                                    print("Pygame audio playback error:", pe)

                            expire_time = now + duration + self.cooldown_seconds

                            self.current_audio = {
                                "audio_bytes": item["audio_bytes"],
                                "audio_id": item["msg_id"],
                                "text": item["text"],
                                "expire_time": expire_time
                            }
                            self.latest_spoken_text = item["text"]
                            self.recent_phrase_ids.append(item["msg_id"])
                            if len(self.recent_phrase_ids) > 10:
                                self.recent_phrase_ids.pop(0)

                time.sleep(0.1)
            except Exception as e:
                print("AudioManager worker exception:", e)
                time.sleep(0.5)

    def get_active_audio(self):
        with self.lock:
            if not self.current_audio:
                return None
            return self.current_audio["audio_bytes"], self.current_audio["audio_id"]

    def get_latest_text(self):
        with self.lock:
            return self.latest_spoken_text

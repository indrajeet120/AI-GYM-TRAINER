import time
import random
import hashlib
import threading
from queue import PriorityQueue


class VoiceQueueManager:
    """
    Thread-safe priority queue manager for AI Gym Trainer audio cues.
    Prevents audio interruptions, enforces a 3-5s cooldown between sentences,
    cancels duplicate/stale messages, and prioritizes safety-critical form corrections.
    """
    def __init__(self, cooldown_seconds=3.5):
        self.cooldown_seconds = cooldown_seconds
        self._queue = PriorityQueue()
        self._lock = threading.Lock()
        self.is_speaking = False
        self.speech_end_time = 0.0
        self.last_spoken_id = None
        self.recent_phrase_ids = []

    def estimate_speech_duration(self, text):
        words = len(text.split())
        # ~2.5 words per second + 0.6s padding for TTS audio start/end
        return max(2.2, (words / 2.5) + 0.6)

    def is_speech_active(self, now=None):
        if now is None:
            now = time.time()
        return now < self.speech_end_time

    def can_speak_now(self, now=None):
        if now is None:
            now = time.time()
        # Must finish current sentence PLUS cooldown period
        return now >= (self.speech_end_time + self.cooldown_seconds)

    def enqueue(self, priority, text, event_type, audio_data=None):
        """
        Priority levels:
        1: Critical Safety (Postural errors, spine collapse, excessive arch, sagging hips)
        2: Range of Motion & Speed (Partial reps, rushing/too fast)
        3: Milestones & Set Completion (Rep praise, set complete, workout complete)
        4: Inactivity & Encouragement
        """
        now = time.time()
        msg_id = hashlib.md5(text.encode("utf-8")).hexdigest()

        with self._lock:
            # Don't queue identical phrase if recently spoken
            if msg_id in self.recent_phrase_ids[-4:]:
                return False

            # Clear stale low-priority items if queue has > 3 items
            if self._queue.qsize() > 3:
                temp_list = []
                while not self._queue.empty():
                    item = self._queue.get()
                    # Keep priority 1 & 2 items queued within last 5 seconds
                    if item[0] <= 2 and (now - item[1]["timestamp"]) < 5.0:
                        temp_list.append(item)
                for item in temp_list:
                    self._queue.put(item)

            item_data = {
                "text": text,
                "event_type": event_type,
                "msg_id": msg_id,
                "timestamp": now,
                "audio_data": audio_data
            }
            # PriorityQueue sorts by first element (priority level 1..4, then timestamp)
            self._queue.put((priority, now, item_data))
            return True

    def get_next_speech(self, now=None):
        if now is None:
            now = time.time()

        if not self.can_speak_now(now):
            return None

        with self._lock:
            while not self._queue.empty():
                priority, ts, data = self._queue.get()
                # Discard messages older than 6 seconds (stale context)
                if (now - ts) > 6.0:
                    continue

                duration = self.estimate_speech_duration(data["text"])
                self.speech_end_time = now + duration
                self.last_spoken_id = data["msg_id"]
                self.recent_phrase_ids.append(data["msg_id"])
                if len(self.recent_phrase_ids) > 10:
                    self.recent_phrase_ids.pop(0)

                data["duration"] = duration
                return data

        return None


class VoicePipeline:
    def __init__(self, llm=None, tts=None):
        self.llm = llm
        self.tts = tts
        self.queue_manager = VoiceQueueManager(cooldown_seconds=3.5)
        self.last_status = None

        # --- Dynamic Non-Repeating Phrase Pools ---
        self.MOTIVATIONAL_REPS = {
            "Beginner": [
                "Great pace! Keep your focus.",
                "Smooth control! Stay steady.",
                "Awesome effort! Keep breathing.",
                "Nice rhythm! You're doing great.",
                "Strong work! Stay locked in.",
            ],
            "Intermediate": [
                "Solid form! Squeeze at the peak.",
                "Great tempo! Maintain control.",
                "Drive through! Clean execution.",
                "Looking strong! Keep your posture tight.",
                "Excellent power! Keep pushing.",
            ],
            "Advanced": [
                "Maximum focus! Explode up!",
                "Elite control! Crush this set!",
                "Flawless mechanics! Keep the tension.",
                "Relentless energy! Drive it home!",
                "Pure strength! Hold that strict form.",
            ]
        }

        self.POSTURE_CUES = {
            "Squats": {
                "Torso Collapse": (1, [
                    "Keep your chest up and spine neutral.",
                    "Don't collapse forward! Lift your chest.",
                    "Proud chest, stay tall throughout."
                ]),
                "Excessive Forward Lean": (1, [
                    "Avoid leaning too far forward.",
                    "Sit back into your hips with chest high.",
                    "Keep your weight balanced over mid-foot."
                ]),
                "Too High": (2, [
                    "Go a little deeper into the squat.",
                    "Aim for ninety degrees at the knees.",
                    "Lower down slightly more."
                ]),
                "PARTIAL": (2, [
                    "Hit full depth on every rep!",
                    "Don't cut the rep short, lower down completely.",
                    "Push through full range of motion."
                ])
            },
            "Push-ups": {
                "Alignment": (1, [
                    "Keep your body in a straight line.",
                    "Brace your core tight, don't sag.",
                    "Tight core! Maintain plank alignment."
                ]),
                "Hip": (1, [
                    "Lift your hips slightly.",
                    "Don't let your hips sag toward the floor.",
                    "Squeeze your glutes to level your hips."
                ]),
                "PARTIAL": (2, [
                    "Lower your chest closer to the floor.",
                    "Push through full range of motion.",
                    "Complete the full press down and up."
                ])
            },
            "Biceps Curls (Dumbbell)": {
                "Swing": (1, [
                    "Avoid swinging the weight. Use strict muscle power.",
                    "Control the momentum! Keep your torso still.",
                    "No swinging! Strict arm movement only."
                ]),
                "Shoulder": (1, [
                    "Pin your elbows to your sides.",
                    "Keep your shoulder stable throughout the curl.",
                    "Lock your elbows in place."
                ]),
                "PARTIAL": (2, [
                    "Extend all the way down, then squeeze at top.",
                    "Don't cut the range short! Full arm extension.",
                    "Squeeze your biceps fully at the peak."
                ])
            },
            "Shoulder Press": {
                "Excessive Arch": (1, [
                    "Brace your core tight! Don't arch your back.",
                    "Keep your spine neutral and hips tucked.",
                    "Avoid leaning back during the press."
                ]),
                "Slight Arch": (1, [
                    "Stay tall and keep your abs engaged.",
                    "Press overhead without leaning back.",
                    "Maintain a rigid core."
                ]),
                "PARTIAL": (2, [
                    "Lock out overhead completely.",
                    "Drive the weight all the way up.",
                    "Full arm extension at the peak."
                ])
            },
            "Lunges": {
                "Balance": (1, [
                    "Keep your balance steady.",
                    "Focus your eyes ahead to stabilize your stance.",
                    "Control your balance on the descent."
                ]),
                "Knee": (1, [
                    "Keep your front knee aligned over your foot.",
                    "Don't let your front knee collapse inward.",
                    "Track your knee straight ahead."
                ]),
                "PARTIAL": (2, [
                    "Step deeper and lower your back knee down.",
                    "Full depth lunge! Lower with control.",
                    "Drive down deeper into the lunge."
                ])
            }
        }

        self.SPEED_CUES = (2, [
            "Slow down, control the movement.",
            "Lift with control! Don't rush.",
            "Maintain a steady tempo on every rep.",
            "Control the descent phase!"
        ])

        self.INACTIVITY_CUES = (4, [
            "Let me see your next rep! Let me guide you.",
            "Keep the momentum going! Begin the movement.",
            "Stay engaged! Ready for the next rep."
        ])

        self.SET_COMPLETED_CUES = (3, [
            "Fantastic set! Take a brief rest.",
            "Great set completed! Shake it off.",
            "Outstanding work on that set! Rest up.",
            "Set crushed! Catch your breath."
        ])

        self.WORKOUT_COMPLETED_CUES = (3, [
            "Workout complete! Outstanding job today!",
            "Incredible workout! Session finished strong!",
            "All sets finished! Great dedication!"
        ])

    def _select_phrase(self, pool):
        return self.queue_manager._queue and random.choice(pool) or random.choice(pool)

    def process_event(self, event, exercise, metrics, experience_level="Intermediate"):
        now = time.time()
        text = None
        priority = 3

        current_rep = metrics.get("reps", 0)
        speed = metrics.get("speed_status", "NORMAL")
        rom = metrics.get("rom_status", "FULL")
        partial = metrics.get("partial_rep", False)
        inactivity = metrics.get("inactivity_warning", False)

        # 1. SET COMPLETED
        if event == "set_completed":
            priority, pool = self.SET_COMPLETED_CUES
            text = random.choice(pool)
            self.last_status = "set_completed"

        # 2. WORKOUT COMPLETED
        elif event == "workout_completed":
            priority, pool = self.WORKOUT_COMPLETED_CUES
            text = random.choice(pool)
            self.last_status = "workout_completed"

        # 3. NO POSE DETECTED
        elif event == "no_pose_detected":
            priority = 2
            text = "Please step inside the camera frame so I can guide your form."
            self.last_status = "no_pose"

        # 4. IN-REP FORM & POSTURE CHECK
        elif event in ["ongoing_form_check", "rep_completed"]:
            cues = self.POSTURE_CUES.get(exercise, {})

            # Priority 1: Check Specific Posture Issues
            if exercise == "Squats":
                posture = metrics.get("posture_status", "")
                depth = metrics.get("depth_status", "")
                if posture in cues:
                    p, pool = cues[posture]
                    text, priority = random.choice(pool), p
                elif depth == "Too High" and self.last_status != "Too High":
                    p, pool = cues["Too High"]
                    text, priority = random.choice(pool), p
            elif exercise == "Push-ups":
                alignment = metrics.get("body_alignment", "")
                hip = metrics.get("hip_status", "")
                if alignment != "Straight" and self.last_status != "Alignment":
                    p, pool = cues.get("Alignment", (1, ["Keep your body straight."]))
                    text, priority = random.choice(pool), p
                elif hip == "SAGGING" and self.last_status != "Hip":
                    p, pool = cues.get("Hip", (1, ["Lift your hips slightly."]))
                    text, priority = random.choice(pool), p
            elif exercise == "Biceps Curls (Dumbbell)":
                swing = metrics.get("swing_status", "")
                shoulder = metrics.get("shoulder_status", "")
                if swing == "SWINGING" and self.last_status != "Swing":
                    p, pool = cues.get("Swing", (1, ["Avoid swinging."]))
                    text, priority = random.choice(pool), p
                elif shoulder != "STABLE" and self.last_status != "Shoulder":
                    p, pool = cues.get("Shoulder", (1, ["Keep your shoulder stable."]))
                    text, priority = random.choice(pool), p
            elif exercise == "Shoulder Press":
                back_arch = metrics.get("back_arch_status", "")
                if back_arch == "Excessive Arch" and self.last_status != "Excessive Arch":
                    p, pool = cues.get("Excessive Arch", (1, ["Brace your core."]))
                    text, priority = random.choice(pool), p
                elif back_arch == "Slight Arch" and self.last_status != "Slight Arch":
                    p, pool = cues.get("Slight Arch", (1, ["Stay tall."]))
                    text, priority = random.choice(pool), p
            elif exercise == "Lunges":
                balance = metrics.get("balance_status", "")
                if balance == "OFF BALANCE" and self.last_status != "Balance":
                    p, pool = cues.get("Balance", (1, ["Keep your balance steady."]))
                    text, priority = random.choice(pool), p

            # Priority 2: Partial Rep Warning
            if not text and (partial or rom == "PARTIAL") and self.last_status != "PARTIAL":
                if "PARTIAL" in cues:
                    p, pool = cues["PARTIAL"]
                    text, priority = random.choice(pool), p
                    self.last_status = "PARTIAL"

            # Priority 2: Speed / Rushing Warning
            if not text and speed == "TOO FAST" and self.last_status != "TOO FAST":
                p, pool = self.SPEED_CUES
                text, priority = random.choice(pool), p
                self.last_status = "TOO FAST"

            # Priority 4: Inactivity Warning
            if not text and inactivity and self.last_status != "INACTIVITY":
                p, pool = self.INACTIVITY_CUES
                text, priority = random.choice(pool), p
                self.last_status = "INACTIVITY"

            # Priority 3: Rep Completion Praise (Every rep or milestone reps: 3, 5, 7, 10)
            if not text and event == "rep_completed":
                level_pool = self.MOTIVATIONAL_REPS.get(experience_level, self.MOTIVATIONAL_REPS["Intermediate"])
                praise = random.choice(level_pool)
                text = f"{praise} Rep {current_rep}."
                priority = 3
                self.last_status = f"rep_{current_rep}"

        # If a phrase was selected, generate TTS audio and enqueue
        if text:
            audio_data = None
            if self.tts:
                audio_data = self.tts.speak(text)
            self.queue_manager.enqueue(priority, text, event, audio_data=audio_data)

        # Check if queue has a pending speech item ready for playback
        speech_item = self.queue_manager.get_next_speech(now)
        if speech_item:
            audio = speech_item.get("audio_data")
            spk_text = speech_item.get("text")
            msg_id = speech_item.get("msg_id")
            return audio, spk_text, msg_id

        return None
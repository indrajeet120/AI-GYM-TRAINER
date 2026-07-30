import time
import random
from services.coaching.audio_manager import AudioManager


class VoicePipeline:
    def __init__(self, llm=None, tts=None):
        self.llm = llm
        self.tts = tts
        self.audio_manager = AudioManager()
        self.last_status = None
        self.last_rep_evaluated = 0

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

    def evaluate_and_speak(self, event, exercise, metrics, experience_level="Intermediate"):
        text = None
        priority = 3

        current_rep = metrics.get("reps", 0)
        speed = metrics.get("speed_status", "NORMAL")
        rom = metrics.get("rom_status", "FULL")
        partial = metrics.get("partial_rep", False)
        inactivity = metrics.get("inactivity_warning", False)

        if event == "set_completed":
            priority, pool = self.SET_COMPLETED_CUES
            text = random.choice(pool)
            self.last_status = "set_completed"

        elif event == "workout_completed":
            priority, pool = self.WORKOUT_COMPLETED_CUES
            text = random.choice(pool)
            self.last_status = "workout_completed"

        elif event == "no_pose_detected":
            priority = 2
            text = "Please step inside the camera frame so I can guide your form."
            self.last_status = "no_pose"

        elif event in ["ongoing_form_check", "rep_completed"]:
            cues = self.POSTURE_CUES.get(exercise, {})

            # Priority 1: Posture Check
            if exercise == "Squats":
                posture = metrics.get("posture_status", "")
                depth = metrics.get("depth_status", "")
                if posture in cues and self.last_status != posture:
                    p, pool = cues[posture]
                    text, priority = random.choice(pool), p
                    self.last_status = posture
                elif depth == "Too High" and self.last_status != "Too High":
                    p, pool = cues["Too High"]
                    text, priority = random.choice(pool), p
                    self.last_status = "Too High"

            elif exercise == "Push-ups":
                alignment = metrics.get("body_alignment", "")
                hip = metrics.get("hip_status", "")
                if alignment != "Straight" and self.last_status != "Alignment":
                    p, pool = cues.get("Alignment", (1, ["Keep your body straight."]))
                    text, priority = random.choice(pool), p
                    self.last_status = "Alignment"
                elif hip == "SAGGING" and self.last_status != "Hip":
                    p, pool = cues.get("Hip", (1, ["Lift your hips slightly."]))
                    text, priority = random.choice(pool), p
                    self.last_status = "Hip"

            elif exercise == "Biceps Curls (Dumbbell)":
                swing = metrics.get("swing_status", "")
                shoulder = metrics.get("shoulder_status", "")
                if swing == "SWINGING" and self.last_status != "Swing":
                    p, pool = cues.get("Swing", (1, ["Avoid swinging."]))
                    text, priority = random.choice(pool), p
                    self.last_status = "Swing"
                elif shoulder != "STABLE" and self.last_status != "Shoulder":
                    p, pool = cues.get("Shoulder", (1, ["Keep your shoulder stable."]))
                    text, priority = random.choice(pool), p
                    self.last_status = "Shoulder"

            elif exercise == "Shoulder Press":
                back_arch = metrics.get("back_arch_status", "")
                if back_arch == "Excessive Arch" and self.last_status != "Excessive Arch":
                    p, pool = cues.get("Excessive Arch", (1, ["Brace your core."]))
                    text, priority = random.choice(pool), p
                    self.last_status = "Excessive Arch"
                elif back_arch == "Slight Arch" and self.last_status != "Slight Arch":
                    p, pool = cues.get("Slight Arch", (1, ["Stay tall."]))
                    text, priority = random.choice(pool), p
                    self.last_status = "Slight Arch"

            elif exercise == "Lunges":
                balance = metrics.get("balance_status", "")
                if balance == "OFF BALANCE" and self.last_status != "Balance":
                    p, pool = cues.get("Balance", (1, ["Keep your balance steady."]))
                    text, priority = random.choice(pool), p
                    self.last_status = "Balance"

            # Priority 2: Partial Rep Check
            if not text and (partial or rom == "PARTIAL") and self.last_status != "PARTIAL":
                if "PARTIAL" in cues:
                    p, pool = cues["PARTIAL"]
                    text, priority = random.choice(pool), p
                    self.last_status = "PARTIAL"

            # Priority 2: Speed Check
            if not text and speed == "TOO FAST" and self.last_status != "TOO FAST":
                p, pool = self.SPEED_CUES
                text, priority = random.choice(pool), p
                self.last_status = "TOO FAST"

            # Priority 4: Inactivity Warning
            if not text and inactivity and self.last_status != "INACTIVITY":
                p, pool = self.INACTIVITY_CUES
                text, priority = random.choice(pool), p
                self.last_status = "INACTIVITY"

            # Priority 3: Rep Praise
            if not text and event == "rep_completed" and current_rep > self.last_rep_evaluated:
                self.last_rep_evaluated = current_rep
                level_pool = self.MOTIVATIONAL_REPS.get(experience_level, self.MOTIVATIONAL_REPS["Intermediate"])
                praise = random.choice(level_pool)
                text = f"{praise} Rep {current_rep}."
                priority = 3
                self.last_status = f"rep_{current_rep}"

        if text and self.tts:
            audio_bytes = self.tts.speak(text)
            if audio_bytes:
                self.audio_manager.enqueue_speech(priority, text, audio_bytes)
                return text

        return None
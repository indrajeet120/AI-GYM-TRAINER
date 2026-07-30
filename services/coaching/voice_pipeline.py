import time
import random


class VoicePipeline:
    def __init__(self, llm=None, tts=None):
        self.llm = llm
        self.tts = tts
        self.last_spoken_at = 0
        self.last_status = None
        self.recent_phrases = []

        # --- Dynamic Phrase Libraries ---
        self.MOTIVATIONAL_REPS = {
            "Beginner": [
                "Great pace! Keep moving.",
                "Awesome control, stay focused.",
                "Nice work! Focus on your breathe.",
                "You're doing fantastic, keep going!",
                "Strong effort, smooth movement.",
            ],
            "Intermediate": [
                "Solid form! Squeeze at the top.",
                "Great tempo, maintain that control.",
                "Drive through! Perfect execution.",
                "Looking strong! Keep that posture locked.",
                "Excellent power! Keep pushing.",
            ],
            "Advanced": [
                "Maximum focus! Explode up!",
                "Elite control, crush this set!",
                "Flawless mechanics! Keep the tension.",
                "Relentless energy! Drive it home!",
                "Pure strength! Hold that strict form.",
            ]
        }

        self.POSTURE_CUES = {
            "Squats": {
                "Torso Collapse": [
                    "Keep your chest up and spine neutral.",
                    "Don't collapse forward, lift your chest!",
                    "Proud chest, stay tall throughout."
                ],
                "Excessive Forward Lean": [
                    "Avoid leaning too far forward.",
                    "Sit back into your hips, chest high.",
                    "Keep your weight over mid-foot."
                ],
                "Too High": [
                    "Go a little deeper into the squat.",
                    "Aim for 90 degrees at the knees.",
                    "Lower down slightly more."
                ],
                "PARTIAL": [
                    "Full range of motion! Hit full depth.",
                    "Don't cut the rep short, lower down completely.",
                    "Push through full range of motion."
                ]
            },
            "Push-ups": {
                "Alignment": [
                    "Keep your body in a straight line.",
                    "Brace your core, don't bend at the waist.",
                    "Tight core, maintain plank alignment."
                ],
                "Hip": [
                    "Lift your hips slightly.",
                    "Don't let your hips sag toward the floor.",
                    "Squeeze your glutes to level your hips."
                ],
                "PARTIAL": [
                    "Lower your chest closer to the floor.",
                    "Push through full range of motion.",
                    "Complete the full press down and up."
                ]
            },
            "Biceps Curls (Dumbbell)": {
                "Swing": [
                    "Avoid swinging the weight. Use muscle power.",
                    "Control the momentum, keep your body still.",
                    "No swinging! Strict arm movement only."
                ],
                "Shoulder": [
                    "Pin your elbows to your sides.",
                    "Keep your shoulder stable throughout the curl.",
                    "Lock your elbows in place."
                ],
                "PARTIAL": [
                    "Extend all the way down, then squeeze at top.",
                    "Don't cut the range short! Full arm extension.",
                    "Squeeze your biceps fully at the top."
                ]
            },
            "Shoulder Press": {
                "Excessive Arch": [
                    "Brace your core tight. Don't arch your back excessively.",
                    "Keep your spine neutral and hips tucked.",
                    "Avoid leaning back during the press."
                ],
                "Slight Arch": [
                    "Stay tall and keep your abdominal muscle engaged.",
                    "Press overhead without leaning back.",
                    "Maintain a rigid core."
                ],
                "PARTIAL": [
                    "Lock out overhead completely.",
                    "Drive the weight all the way up.",
                    "Full arm extension at the peak."
                ]
            },
            "Lunges": {
                "Balance": [
                    "Keep your balance steady.",
                    "Find a focal point to stabilize your stance.",
                    "Control your balance on the descent."
                ],
                "Knee": [
                    "Keep your front knee aligned over your foot.",
                    "Don't let your front knee collapse inward.",
                    "Track your knee straight ahead."
                ],
                "PARTIAL": [
                    "Step deeper and drop your back knee down.",
                    "Full depth lunge, lower with control.",
                    "Drive down deeper into the lunge."
                ]
            }
        }

        self.SPEED_CUES = [
            "Slow down, control the movement.",
            "Lift with control, don't rush.",
            "Maintain a steady tempo on every rep.",
            "Control the eccentric phase!"
        ]

        self.INACTIVITY_CUES = [
            "Let's get moving! Start your next rep.",
            "Keep the momentum going! Begin the movement.",
            "Stay engaged! Ready for the next rep."
        ]

        self.SET_COMPLETED_CUES = [
            "Fantastic set! Take a brief rest.",
            "Great set completed! Shake it off.",
            "Outstanding work on that set! Rest up.",
            "Set crushed! Catch your breath."
        ]

        self.WORKOUT_COMPLETED_CUES = [
            "Workout complete! Outstanding job today!",
            "Incredible workout! Session finished strong!",
            "All sets done! Great dedication!"
        ]

    def _get_unique_phrase(self, phrase_list):
        available = [p for p in phrase_list if p not in self.recent_phrases]
        if not available:
            self.recent_phrases.clear()
            available = phrase_list
        chosen = random.choice(available)
        self.recent_phrases.append(chosen)
        if len(self.recent_phrases) > 5:
            self.recent_phrases.pop(0)
        return chosen

    def process_event(self, event, exercise, metrics, experience_level="Intermediate"):
        now = time.time()
        text = ""

        current_rep = metrics.get("reps", 0)
        speed = metrics.get("speed_status", "NORMAL")
        rom = metrics.get("rom_status", "FULL")
        partial = metrics.get("partial_rep", False)
        inactivity = metrics.get("inactivity_warning", False)

        # 1. SET COMPLETED
        if event == "set_completed":
            text = self._get_unique_phrase(self.SET_COMPLETED_CUES)
            self.last_status = "set_completed"

        # 2. WORKOUT COMPLETED
        elif event == "workout_completed":
            text = self._get_unique_phrase(self.WORKOUT_COMPLETED_CUES)
            self.last_status = "workout_completed"

        # 3. NO POSE DETECTED
        elif event == "no_pose_detected":
            text = "Please step inside the camera frame so I can guide your form."
            self.last_status = "no_pose"

        # 4. FORM SAFETY & POSTURE CORRECTIONS (Highest In-Rep Priority)
        elif event == "ongoing_form_check" or event == "rep_completed":
            cues = self.POSTURE_CUES.get(exercise, {})

            # Check Specific Posture Issues
            if exercise == "Squats":
                posture = metrics.get("posture_status", "")
                depth = metrics.get("depth_status", "")
                if posture in cues:
                    text = self._get_unique_phrase(cues[posture])
                elif depth == "Too High" and self.last_status != "Too High":
                    text = self._get_unique_phrase(cues["Too High"])
            elif exercise == "Push-ups":
                alignment = metrics.get("body_alignment", "")
                hip = metrics.get("hip_status", "")
                if alignment != "Straight" and self.last_status != "Alignment":
                    text = self._get_unique_phrase(cues.get("Alignment", ["Keep your body straight."]))
                elif hip == "SAGGING" and self.last_status != "Hip":
                    text = self._get_unique_phrase(cues.get("Hip", ["Lift your hips slightly."]))
            elif exercise == "Biceps Curls (Dumbbell)":
                swing = metrics.get("swing_status", "")
                shoulder = metrics.get("shoulder_status", "")
                if swing == "SWINGING" and self.last_status != "Swing":
                    text = self._get_unique_phrase(cues.get("Swing", ["Avoid swinging."]))
                elif shoulder != "STABLE" and self.last_status != "Shoulder":
                    text = self._get_unique_phrase(cues.get("Shoulder", ["Keep your shoulder stable."]))
            elif exercise == "Shoulder Press":
                back_arch = metrics.get("back_arch_status", "")
                if back_arch == "Excessive Arch" and self.last_status != "Excessive Arch":
                    text = self._get_unique_phrase(cues.get("Excessive Arch", ["Brace your core."]))
                elif back_arch == "Slight Arch" and self.last_status != "Slight Arch":
                    text = self._get_unique_phrase(cues.get("Slight Arch", ["Stay tall."]))
            elif exercise == "Lunges":
                balance = metrics.get("balance_status", "")
                if balance == "OFF BALANCE" and self.last_status != "Balance":
                    text = self._get_unique_phrase(cues.get("Balance", ["Keep your balance steady."]))

            # Partial Rep Warning
            if not text and (partial or rom == "PARTIAL") and self.last_status != "PARTIAL":
                if "PARTIAL" in cues:
                    text = self._get_unique_phrase(cues["PARTIAL"])
                    self.last_status = "PARTIAL"

            # Speed / Rushing Warning
            if not text and speed == "TOO FAST" and self.last_status != "TOO FAST":
                text = self._get_unique_phrase(self.SPEED_CUES)
                self.last_status = "TOO FAST"

            # Inactivity Cue
            if not text and inactivity and self.last_status != "INACTIVITY":
                text = self._get_unique_phrase(self.INACTIVITY_CUES)
                self.last_status = "INACTIVITY"

            # Rep Completion & Praise (if no form errors were triggered)
            if not text and event == "rep_completed":
                level_pool = self.MOTIVATIONAL_REPS.get(experience_level, self.MOTIVATIONAL_REPS["Intermediate"])
                praise = self._get_unique_phrase(level_pool)
                text = f"{praise} Rep {current_rep}."
                self.last_status = f"rep_{current_rep}"

        if not text:
            return None

        # Cooldown guard: minimum 2.5 seconds between speech to keep audio smooth
        if now - self.last_spoken_at < 2.5 and event not in ["set_completed", "workout_completed"]:
            return None

        print("AI COACH SPOKEN:", text)

        try:
            if self.tts:
                voice = self.tts.speak(text)
                if voice:
                    self.last_spoken_at = now
                    return voice, text
            return None, text
        except Exception as e:
            print("TTS Execution Error:", e)
            return None, text
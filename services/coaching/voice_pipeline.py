

import time
import os
# import threading
# import io

# try:
#     os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"
#     import pygame
#     pygame.mixer.init()
# except Exception as e:
#     print("Pygame mixer initialization failed:", e)


# def play_audio_native(audio_bytes):
#     def play():
#         try:
#             fp = io.BytesIO(audio_bytes)
#             pygame.mixer.music.load(fp)
#             pygame.mixer.music.play()
#             while pygame.mixer.music.get_busy():
#                 time.sleep(0.1)
#         except Exception as e:
#             print("NATIVE AUDIO PLAY ERROR:", e)

#     threading.Thread(target=play, daemon=True).start()


class VoicePipeline:
    def __init__(self, llm, tts):
        self.llm = llm
        self.tts = tts
        self.last_spoken_at = 0
        self.last_status = None

    def process_event(self, event, exercise, metrics):
        now = time.time()

        current_rep = metrics.get("reps", 0)
        extension = metrics.get("extension_status", "")
        back_arch = metrics.get("back_arch_status", "")

        text = ""

        # ---------------- SHOULDER PRESS ----------------
        if exercise == "Shoulder Press":
            if back_arch == "Excessive Arch" and self.last_status != "Excessive Arch":
                text = "Brace your core. Keep your spine neutral."
                self.last_status = "Excessive Arch"

            elif back_arch == "Slight Arch" and self.last_status != "Slight Arch":
                text = "Stay tall and avoid leaning back."
                self.last_status = "Slight Arch"

            elif extension == "PRESSING" and self.last_status != "PRESSING":
                text = "Drive the weight overhead."
                self.last_status = "PRESSING"

            # elif extension == "FULL EXTENSION" and self.last_status != "FULL EXTENSION":
            #     text = f"Excellent lockout. Rep {current_rep}."
            #     self.last_status = "FULL EXTENSION"
            elif event == "rep_completed":
              text = f"Excellent lockout. Rep {current_rep}."
              self.last_status = "FULL EXTENSION"
            # elif extension == "START POSITION" and self.last_status != "START POSITION":
            #     text = "Control the weight on the way down."
            #     self.last_status = "START POSITION"

        # ---------------- SQUATS ----------------
        elif exercise == "Squats":
            depth = metrics.get("depth_status", "")
            back = metrics.get("back_angle", 0)

            if depth == "Too High" and self.last_status != "Too High":
                text = "Go a little deeper."
                self.last_status = "Too High"

            elif back < 40 and self.last_status != "Back Bent":
                text = "Keep your chest up and back straight."
                self.last_status = "Back Bent"

            elif event == "rep_completed":
                self.last_status = "Good"
                if current_rep % 3 == 1:
                    text = f"Good squat. Rep {current_rep}."
                elif current_rep % 3 == 2:
                    text = f"Nice depth. Rep {current_rep}."
                else:
                    text = f"Excellent form. Rep {current_rep}."

        # ---------------- PUSH-UPS ----------------
        elif exercise == "Push-ups":
            alignment = metrics.get("body_alignment", "")
            hip = metrics.get("hip_status", "")

            if alignment != "Straight" and self.last_status != "Alignment":
                text = "Keep your body in a straight line."
                self.last_status = "Alignment"

            elif hip == "Sagging" and self.last_status != "Hip":
                text = "Lift your hips slightly."
                self.last_status = "Hip"

            elif event == "rep_completed":
                self.last_status = "Good"
                if current_rep % 2 == 0:
                    text = f"Strong push-up. Rep {current_rep}."
                else:
                    text = f"Great control. Rep {current_rep}."

        # ---------------- BICEPS CURLS ----------------
        elif exercise == "Biceps Curls (Dumbbell)":
            swing = metrics.get("swing_status", "")
            shoulder = metrics.get("shoulder_status", "")

            if swing == "Swinging" and self.last_status != "Swing":
                text = "Avoid swinging the dumbbell."
                self.last_status = "Swing"

            elif shoulder != "Stable" and self.last_status != "Shoulder":
                text = "Keep your shoulder stable."
                self.last_status = "Shoulder"

            elif event == "rep_completed":
                self.last_status = "Good"
                if current_rep % 2 == 0:
                    text = f"Nice curl. Rep {current_rep}."
                else:
                    text = f"Squeeze at the top. Rep {current_rep}."

        # ---------------- LUNGES ----------------
        elif exercise == "Lunges":
            balance = metrics.get("balance_status", "")
            knee = metrics.get("front_knee_angle", 0)

            if balance != "Balanced" and self.last_status != "Balance":
                text = "Keep your balance steady."
                self.last_status = "Balance"

            elif knee < 70 and self.last_status != "Knee":
                text = "Keep the front knee aligned with the foot."
                self.last_status = "Knee"

            elif event == "rep_completed":
                self.last_status = "Good"
                if current_rep % 2 == 0:
                    text = f"Good lunge. Rep {current_rep}."
                else:
                    text = f"Nice control. Rep {current_rep}."

        # ---------------- NO MESSAGE ----------------
        if not text:
            return None

        # Smooth cooldown
        if now - self.last_spoken_at < 1.0:
            return None

        print("COACH LIVE TRACKING TEXT:", text)

        # try:
        #     voice = self.tts.speak(text)
        #     if voice:
        #         play_audio_native(voice)
        #         self.last_spoken_at = now
        #         return voice, text
        # except Exception as e:
        #     print("TTS Native execution error:", e)

        # return None
        try:
          voice = self.tts.speak(text)

          if voice:
            self.last_spoken_at = now
            return voice

        except Exception as e:
          print("TTS execution error:", e)

        return None
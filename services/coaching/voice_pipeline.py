# import time
# import streamlit as st
# import base64


# class VoicePipeline:
#     def __init__(self, llm, tts):
#         self.llm = llm
#         self.tts = tts
#         self.last_spoken_at = 0

#     def _find_form_issue(self, exercise, metrics):
#         if "issue" in metrics:
#             return metrics["issue"]

#         if exercise == "Squats":
#             depth = metrics.get("depth_status", "")
#             back_angle = metrics.get("back_angle", 180)
            
#             if depth == "START":
#                 return "Go deeper into your squat."

#             if isinstance(back_angle, (int, float)) and back_angle < 130:
#                 return "The user is leaning too far forward during the squat."

#         elif exercise == "Push-ups":
#             alignment = metrics.get("body_alignment", "")
#             hip_status = metrics.get("hip_status", "")
            
#             if alignment == "Poor Form":
#                 return "The user's body is not straight during the push-up."

#             if hip_status == "SAGGING":
#                 return "The user's hips are sagging down during the push-up."

#             if hip_status == "PIKED UP":
#                 return "The user's hips are too high — lower them to form a straight line."

#         elif exercise == "Biceps Curls (Dumbbell)":
#             swing = metrics.get("swing_status", "")
#             shoulder = metrics.get("shoulder_status", "")
            
#             if swing == "SWINGING":
#                 return "The user is swinging their torso during the curl — keep the body still."

#             if shoulder == "ELBOW DRIFTING":
#                 return "The user's elbow is drifting away from their side during the curl."

#         elif exercise == "Shoulder Press":
#          back_arch = metrics.get("back_arch_status", "")
#          extension = metrics.get("extension_status", "")

#          if back_arch == "Excessive Arch":
#           return "Brace your core and avoid arching your back."

#          if back_arch == "Slight Arch":
#           return "Keep your spine neutral."

#          if extension == "START POSITION":
#           return "Press the dumbbells upward."

#          if extension == "PRESSING":
#           return "Continue pressing upward."

#          if extension == "NEARLY EXTENDED" and metrics.get("elbow_angle", 180) < 150:
#           return "Lock out your arms fully."

#          if extension == "FULL EXTENSION":
#           return None
#         elif exercise == "Lunges":
#             balance = metrics.get("balance_status", "")
            
#             if balance == "OFF BALANCE":
#                 return "The user is losing balance during the lunge — feet should be hip-width apart."

#         return None

#     def process_event(self, event, exercise, metrics):

#     # ---- Shoulder Press special handling ----
#      if exercise == "Shoulder Press":
#         # state change nahi hua → kuch mat bolo
#         if not metrics.get("state_changed", False):
#             return None

#         # sirf useful states par voice do
#         extension = metrics.get("extension_status", "")
#         if extension not in ["START POSITION", "PRESSING", "NEARLY EXTENDED"]:
#             return None

#      issue = self._find_form_issue(exercise, metrics)

#      now = time.time()

#      is_major_issue = event in [
#         "workout_started",
#         "set_completed",
#         "workout_completed"
#      ]

#      if not is_major_issue:
#         if not issue:
#             return None

#         if now - self.last_spoken_at < 12:
#             return None

#      try:
#         text = self.llm.give_feedback(event, issue)
#      except Exception as e:
#         print("LLM ERROR:", e)
#         text = issue if issue else "Keep going."

#      if len(text.split()) > 5:
#         text = " ".join(text.split()[:5]) + "."

#      print("COACH TEXT:", text)
#      print("TEXT LENGTH:", len(text))

#      try:
#         voice = self.tts.speak(text)
#      except Exception as e:
#         print("TTS ERROR:", e)
#         voice = None

#      if voice:
#         print("VOICE GENERATED")
#      else:
#         print("VOICE FAILED")

#      self.last_spoken_at = now
 
#      return voice, text
    
# def autoplay_audio(audio_bytes):

#     if not audio_bytes:
#         return

#     b64 = base64.b64encode(audio_bytes).decode()

#     audio_html = f"""
#     <audio autoplay>
#         <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
#     </audio>
#     """

#     st.components.v1.html(
#         audio_html,
#         height=0
#     )




# import time


# class VoicePipeline:

#     def __init__(self, llm, tts):
#         self.llm = llm
#         self.tts = tts
#         self.last_spoken_at = 0


#     def _find_form_issue(self, exercise, metrics):

#         if "issue" in metrics:
#             return metrics["issue"]


#         if exercise == "Squats":

#             depth = metrics.get("depth_status", "")
#             back_angle = metrics.get("back_angle", 180)

#             if depth == "START":
#                 return "Go deeper into your squat."

#             if isinstance(back_angle, (int, float)) and back_angle < 130:
#                 return "Keep your back straight."



#         elif exercise == "Push-ups":

#             alignment = metrics.get("body_alignment", "")
#             hip_status = metrics.get("hip_status", "")

#             if alignment == "Poor Form":
#                 return "Keep your body straight."

#             if hip_status == "SAGGING":
#                 return "Keep your hips up."



#         elif exercise == "Biceps Curls (Dumbbell)":

#             swing = metrics.get("swing_status", "")
#             shoulder = metrics.get("shoulder_status", "")

#             if swing == "SWINGING":
#                 return "Avoid swinging your body."

#             if shoulder == "ELBOW DRIFTING":
#                 return "Keep your elbow stable."



#         elif exercise == "Shoulder Press":

#             back_arch = metrics.get("back_arch_status", "")
#             extension = metrics.get("extension_status", "")


#             if back_arch == "Excessive Arch":
#                 return "Brace your core and avoid arching your back."


#             if back_arch == "Slight Arch":
#                 return "Keep your spine neutral."


#             if extension == "START POSITION":
#                 return "Press the dumbbells upward."


#             if extension == "PRESSING":
#                 return "Continue pressing upward."


#             if extension == "NEARLY EXTENDED":
#                 return "Extend your arms fully."


#             # full extension par voice nahi
#             if extension == "FULL EXTENSION":
#                 return None



#         elif exercise == "Lunges":

#             balance = metrics.get("balance_status", "")

#             if balance == "OFF BALANCE":
#                 return "Maintain your balance."


#         return None



#     def process_event(self, event, exercise, metrics):


#         # Shoulder Press special control
#         if exercise == "Shoulder Press":

#             if not metrics.get("state_changed", False):
#                 return None



#         issue = self._find_form_issue(
#             exercise,
#             metrics
#         )


#         now = time.time()


#         major_event = event in [
#             "workout_started",
#             "set_completed",
#             "workout_completed"
#         ]



#         if not major_event:

#             if not issue:
#                 return None


#             if now - self.last_spoken_at < 10:
#                 return None



#         # LLM response

#         try:

#             text = self.llm.give_feedback(
#                 event,
#                 issue
#             )


#         except Exception as e:

#             print("LLM ERROR:", e)

#             text = issue if issue else "Keep going."



#         # short sentence

#         words = text.split()

#         if len(words) > 7:
#             text = " ".join(words[:7]) + "."



#         print("COACH TEXT:", text)


#         # TTS

#         try:

#             voice = self.tts.speak(text)


#         except Exception as e:

#             print("TTS ERROR:", e)

#             voice = None



#         if voice:
#             print("VOICE GENERATED")

#         else:
#             print("VOICE FAILED")



#         self.last_spoken_at = now


#         return voice, text



# import time


# class VoicePipeline:

#     def __init__(self, llm, tts):
#         self.llm = llm
#         self.tts = tts
#         self.last_spoken_at = 0


#     def _find_form_issue(self, exercise, metrics):

#         if "issue" in metrics:
#             return metrics["issue"]


#         if exercise == "Squats":

#             depth = metrics.get("depth_status", "")
#             back_angle = metrics.get("back_angle", 180)

#             if depth == "START":
#                 return "Go deeper into your squat."

#             if isinstance(back_angle, (int, float)) and back_angle < 130:
#                 return "Keep your back straight."


#         elif exercise == "Push-ups":

#             alignment = metrics.get("body_alignment", "")
#             hip_status = metrics.get("hip_status", "")

#             if alignment == "Poor Form":
#                 return "Keep your body straight."

#             if hip_status == "SAGGING":
#                 return "Keep your hips up."

#             if hip_status == "PIKED UP":
#                 return "Lower your hips and stay straight."


#         elif exercise == "Biceps Curls (Dumbbell)":

#             swing = metrics.get("swing_status", "")
#             shoulder = metrics.get("shoulder_status", "")

#             if swing == "SWINGING":
#                 return "Avoid swinging your body."

#             if shoulder == "ELBOW DRIFTING":
#                 return "Keep your elbow stable."


#         elif exercise == "Shoulder Press":

#             back_arch = metrics.get("back_arch_status", "")
#             extension = metrics.get("extension_status", "")


#             if back_arch == "Excessive Arch":
#                 return "Brace your core and avoid arching."


#             if back_arch == "Slight Arch":
#                 return "Keep your spine neutral."


#             if extension == "START POSITION":
#                 return "Press upward."


#             if extension == "PRESSING":
#                 return "Continue pressing."


#             if extension == "NEARLY EXTENDED":
#                 return "Extend your arms fully."


#             return None



#         elif exercise == "Lunges":

#             balance = metrics.get("balance_status", "")

#             if balance == "OFF BALANCE":
#                 return "Maintain your balance."


#         return None



#     def process_event(self, event, exercise, metrics):


#         # Shoulder press optimization
#         # if exercise == "Shoulder Press":

#         #     if not metrics.get("state_changed", False):
#         #         return None
#         if exercise == "Shoulder Press":

#           if not metrics.get("state_changed", False) and event != "rep_completed":
#             return None

#         issue = self._find_form_issue(
#             exercise,
#             metrics
#         )


#         now = time.time()


#         major_event = event in [
#             "workout_started",
#             "set_completed",
#             "workout_completed"
#         ]


#         if not major_event:

#             if not issue:
#                 return None


#             # 10 sec cooldown
#             if now - self.last_spoken_at < 10:
#                 return None



#         # Generate coach text

#         try:

#             text = self.llm.give_feedback(
#                 event,
#                 issue
#             )

#         except Exception as e:

#             print("LLM ERROR:", e)

#             text = issue or "Keep going."



#         # Short voice

#         words = text.split()

#         if len(words) > 7:
#             text = " ".join(words[:7]) + "."



#         print("COACH TEXT:", text)


#         # Generate audio bytes only

#         try:

#             voice = self.tts.speak(text)

#         except Exception as e:

#             print("TTS ERROR:", e)

#             voice = None



#         if voice:
#             print("VOICE GENERATED")
#         else:
#             print("VOICE FAILED")


#         self.last_spoken_at = now


#         return voice, text




# gemini ka code
# import time
# import os
# import threading
# import io

# # pygame को म्यूट मोड में इनिशियलाइज़ करने के लिए ताकि टर्मिनल क्लीन रहे
# try:
#     os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
#     import pygame
#     pygame.mixer.init()
# except Exception as e:
#     print("Pygame mixer initialization failed:", e)

# def play_audio_native(audio_bytes):
#     """बिना ब्राउज़र को डिस्टर्ब किए बैकग्राउंड हार्डवेयर थ्रेड में ऑडियो प्ले करने के लिए"""
#     def play():
#         try:
#             # bytes डेटा को सीधे मेमोरी स्ट्रीम में लोड करें
#             fp = io.BytesIO(audio_bytes)
#             pygame.mixer.music.load(fp)
#             pygame.mixer.music.play()
#             while pygame.mixer.music.get_busy():
#                 time.sleep(0.1)
#         except Exception as e:
#             print("NATIVE AUDIO PLAY ERROR:", e)
    
#     # कैमरे के थ्रेड को बिना ब्लॉक किए अलग थ्रेड में ऑडियो रन करें
#     threading.Thread(target=play, daemon=True).start()


# class VoicePipeline:
#     def __init__(self, llm, tts):
#         self.llm = llm
#         self.tts = tts
#         self.last_spoken_at = 0
#         self.last_status = None

#     def process_event(self, event, exercise, metrics):
#         now = time.time()
        
#         current_rep = metrics.get("reps", 0)
#         extension = metrics.get("extension_status", "")
#         back_arch = metrics.get("back_arch_status", "")
        
#         text = ""

#         # ---------------- SHOULDER PRESS ----------------
#         if exercise == "Shoulder Press":
#           if back_arch == "Excessive Arch":
#              text = "Brace your core. Keep your spine neutral."
#           elif back_arch == "Slight Arch":
#             text = "Stay tall and avoid leaning back."
#           elif extension == "PRESSING" and self.last_status != "PRESSING":
#             text = "Drive the weight overhead."
#             self.last_status = "PRESSING"
#           elif extension == "FULL EXTENSION" and self.last_status != "FULL EXTENSION":
#             text = f"Excellent lockout. Rep {current_rep}."
#             self.last_status = "FULL EXTENSION"
#           elif extension == "START POSITION" and self.last_status != "START POSITION":
#             text = "Control the weight on the way down."
#             self.last_status = "START POSITION"

# # ---------------- SQUATS ----------------
#         elif exercise == "Squats":
#           depth = metrics.get("depth_status", "")
#           back = metrics.get("back_angle", 0)

#           if depth == "Too High":
#             text = "Go a little deeper."
#           elif back < 40:
#             text = "Keep your chest up and back straight."
#           elif event == "rep_completed":
#              if current_rep % 3 == 1:
#                text = f"Good squat. Rep {current_rep}."
#              elif current_rep % 3 == 2:
#                text = f"Nice depth. Rep {current_rep}."
#              else:
#                text = f"Excellent form. Rep {current_rep}."

# # ---------------- PUSH-UPS ----------------
#         elif exercise == "Push-ups":
#            alignment = metrics.get("body_alignment", "")
#            hip = metrics.get("hip_status", "")

#            if alignment != "Straight":
#              text = "Keep your body in a straight line."
#            elif hip == "Sagging":
#              text = "Lift your hips slightly."
#            elif event == "rep_completed":
#               if current_rep % 2 == 0:
#                 text = f"Strong push-up. Rep {current_rep}."
#               else:
#                text = f"Great control. Rep {current_rep}."

# # ---------------- BICEPS CURLS ----------------
#         elif exercise == "Biceps Curls (Dumbbell)":
#           swing = metrics.get("swing_status", "")
#           shoulder = metrics.get("shoulder_status", "")

#           if swing == "Swinging":
#             text = "Avoid swinging the dumbbell."
#           elif shoulder != "Stable":
#             text = "Keep your shoulder stable."
#           elif event == "rep_completed":
#            if current_rep % 2 == 0:
#             text = f"Nice curl. Rep {current_rep}."
#            else:
#             text = f"Squeeze at the top. Rep {current_rep}."

# # ---------------- LUNGES ----------------
#         elif exercise == "Lunges":
#           balance = metrics.get("balance_status", "")
#           knee = metrics.get("front_knee_angle", 0)

#           if balance != "Balanced":
#             text = "Keep your balance steady."
#           elif knee < 70:
#             text = "Keep the front knee aligned with the foot."
#           elif event == "rep_completed":
#             if current_rep % 2 == 0:
#               text = f"Good lunge. Rep {current_rep}."
#             else:
#              text = f"Nice control. Rep {current_rep}."

#         if not text:
#             return None

#         # लाइव क्यूशन कूलडाउन (1.8 सेकंड)
#         if now - self.last_spoken_at < 1.0:
#             return None

#         print("COACH LIVE TRACKING TEXT:", text)

#         try:
#             voice = self.tts.speak(text)
#             if voice:
#                 # 🔥 ब्राउज़र को बायपास करके सीधे सिस्टम स्पीकर से ऑडियो प्ले करें
#                 play_audio_native(voice)
#                 self.last_spoken_at = now
#                 return voice, text
#         except Exception as e:
#             print("TTS Native execution error:", e)
            
#         return None




import time
import os
import threading
import io

try:
    os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"
    import pygame
    pygame.mixer.init()
except Exception as e:
    print("Pygame mixer initialization failed:", e)


def play_audio_native(audio_bytes):
    def play():
        try:
            fp = io.BytesIO(audio_bytes)
            pygame.mixer.music.load(fp)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
        except Exception as e:
            print("NATIVE AUDIO PLAY ERROR:", e)

    threading.Thread(target=play, daemon=True).start()


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

            elif extension == "FULL EXTENSION" and self.last_status != "FULL EXTENSION":
                text = f"Excellent lockout. Rep {current_rep}."
                self.last_status = "FULL EXTENSION"

            elif extension == "START POSITION" and self.last_status != "START POSITION":
                text = "Control the weight on the way down."
                self.last_status = "START POSITION"

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
        if now - self.last_spoken_at < 0.6:
            return None

        print("COACH LIVE TRACKING TEXT:", text)

        try:
            voice = self.tts.speak(text)
            if voice:
                play_audio_native(voice)
                self.last_spoken_at = now
                return voice, text
        except Exception as e:
            print("TTS Native execution error:", e)

        return None
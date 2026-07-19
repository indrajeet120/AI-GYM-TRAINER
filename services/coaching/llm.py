

# ----------------------------------------------

from services.config.workout_config import PROMPT

class LLMCoach:
    def __init__(self, groq_client):
        self.client = groq_client
        self.history = []
        self.system_prompt = PROMPT + (
            "\n\n[STRICT RULES FOR VOICE COACHING]:\n"
            "1. You are a live spoken gym coach. Speak directly, dynamically, and naturally in 1 or 2 short sentences max.\n"
            "2. When the event is 'workout_started', welcome the user, name the exercise, and tell them to start strong.\n"
            "3. When counting reps ('rep_completed'), ALWAYS read the exact rep number provided in the prompt text and say it out loud.\n"
            "4. If there is a form issue, warn them immediately and tell them how to fix it in that specific rep."
        )

    def give_feedback(self, event, issue):
        # # 🔥 Safe fallback: Agar API rate limit (429) error aata hai,
        # to system crash hone ke bajay gracefully handle karega aur
        # turant proper response return karega.
        fallback_text = "Keep going, stay strong!"
        if "Rep number" in str(issue):
            rep_parts = str(issue).split("completed")
            rep_info = rep_parts[0] if rep_parts else "Next rep"
            if "issue:" in str(issue):
                err_details = str(issue).split("issue:")[-1]
                fallback_text = f"{rep_info} down! But watch out, {err_details}"
            else:
                fallback_text = f"Excellent! {rep_info} down, form is textbook. Keep it up!"
        elif event == "workout_started":
            fallback_text = "Alright, let's crush this session! First set, start strong!"

        try:
            prompt = f"Event: {event}"
            if issue:
                prompt += f" Details: {issue}"

            messages = [
                {"role": "system", "content": self.system_prompt},
                *self.history[-4:], # "Conversation history ko optimize kiya gaya hai taaki unnecessary token usage reduce ho aur performance improve ho."
                {"role": "user", "content": prompt}
            ]

            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                temperature=0.4,
            )
            return response.choices[0].message.content.strip()

        except Exception as e:
            print("LLM RATE LIMIT OR ERROR TRIGGERED, USING PERFECT FALLBACK SCRIPT:", e)
            return fallback_text
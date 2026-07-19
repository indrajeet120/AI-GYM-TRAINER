

import warnings

warnings.filterwarnings(
    "ignore",
    message=".*GetPrototype.*"
)

import streamlit as st
import os
import time
import pandas as pd
from services.auth.login_wall import render_login_wall
from services.state.session_defaults import initial_session_defaults
from services.config.workout_config import EXERCISE_OPTIONS
from services.ui.style_loader import load_css, inject_local_font, inject_webrtc_styles
from services.persistence.exercise_repository import init_db
from streamlit_webrtc import webrtc_streamer, WebRtcMode
from services.vision.exercise_video_processor import VideoProcessorClass
from services.tracking.metrics import sync_metrics_update
from services.persistence.exercise_repository import get_users_exercises
from groq import Groq
from services.coaching.llm import LLMCoach
from services.coaching.tts import TextToSpeech
from services.coaching.voice_pipeline import VoicePipeline
from dotenv import load_dotenv
from streamlit_autorefresh import st_autorefresh

load_dotenv()

def main():
    st.set_page_config(
        page_icon="🏋️‍♀️",
        page_title="AI Real-time GYM Coach",
        initial_sidebar_state="expanded",
        layout="centered"
    )

    load_css(os.path.join(os.getcwd(), "static", "style.css"))
    inject_local_font(os.path.join(os.getcwd(), "static", "AdobeClean.otf"), "AdobeClean")

    init_db()

    if not render_login_wall():
        return 

    initial_session_defaults()

    if "audio_to_play" not in st.session_state:
     st.session_state.audio_to_play = None

    if "last_spoken_rep" not in st.session_state:
        st.session_state.last_spoken_rep = 0

    if "voice_pipeline" not in st.session_state:
        try:
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                st.error("GORQ_API_KEY not found in .env file")
                st.stop()
                
            groq_client = Groq(api_key=api_key)
            llm_coach = LLMCoach(groq_client)
            tts = TextToSpeech()
            st.session_state.voice_pipeline = VoicePipeline(llm_coach, tts)
        except Exception as e:
            st.error(f"Voice pipeline init failed: {e}")
            st.session_state.voice_pipeline = None

    workout_started = st.session_state.get("workout_started", False)
    
    with st.sidebar:
        st.title("🏋️‍♂️ Apna AI Coach")
        if st.session_state.username:
            st.caption(f"👤 Login as {st.session_state.username}")

        st.divider()
        st.subheader("Workout Plan")

        if not workout_started:
            plan_exercise = st.selectbox("Exercise", options=EXERCISE_OPTIONS, key="plan_exercise")
            plan_sets = st.number_input("Sets", min_value=0, max_value=50, key="plan_sets", step=1)
            plan_reps = st.number_input("Reps per Set", min_value=0, max_value=50, key="plan_reps", step=1)

            st.markdown("")
            start_session_button = st.button("Start Workout", width="stretch", key="start_session_button")

            if start_session_button:
                st.session_state.exercise_type = plan_exercise
                st.session_state.target_sets = int(plan_sets)
                st.session_state.reps_per_set = int(plan_reps)
                st.session_state.reps = 0
                st.session_state.workout_started = True
                st.session_state.set_cycle_started_at = time.time()
                st.session_state.last_saved_sets_completed = 0
                st.session_state.last_spoken_rep = 0
                st.rerun()
        else:
            exercise = st.session_state.get("exercise_type")
            sets = st.session_state.get("target_sets")
            reps = st.session_state.get("reps_per_set")

            st.info(f"**{exercise}** -- {sets} Sets / {reps} Reps")
            end_session_button = st.button("End Workout", key="end_session_button", width="stretch")

            if end_session_button:
                st.session_state.workout_started = False
                st.rerun()

        if workout_started:
            st.divider()
            exercise = st.session_state.get("exercise_type")
            total_reps = st.session_state.get("reps")
            current_set_reps = st.session_state.get("current_set_reps")
            reps_per_set = st.session_state.get("reps_per_set")
            sets_completed = st.session_state.get("sets_completed")
            target_sets = st.session_state.get("target_sets")

            st.subheader("Progress")
            st.metric("Total Reps", f"{total_reps}")
            st.metric("Current Set Reps", f"{current_set_reps} / {reps_per_set}")
            st.metric("Sets Completed", f"{sets_completed} / {target_sets}")

            st.divider()

            if exercise == "Squats":
                st.subheader("Squat Metrics")
                st.metric("Knee Angle", f"{st.session_state.knee_angle}°")
                st.metric("Back Angle", f"{st.session_state.back_angle}°")
                st.metric("Depth Status", st.session_state.depth_status)
            elif exercise == "Push-ups":
                st.subheader("Push-up Metrics")
                st.metric("Elbow Angle", f"{st.session_state.elbow_angle}°")
                st.metric("Body Alignment", st.session_state.body_alignment)
                st.metric("Hip Position", st.session_state.hip_status)
            elif exercise == "Biceps Curls (Dumbbell)":
                st.subheader("Curl Metrics")
                st.metric("Elbow Angle", f"{st.session_state.elbow_angle}°")
                st.metric("Shoulder Stability", st.session_state.shoulder_status)
                st.metric("Swing Detection", st.session_state.swing_status)
            elif exercise == "Shoulder Press":
                st.subheader("Shoulder Press Metrics")
                st.metric("Elbow Angle", f"{st.session_state.elbow_angle}°")
                st.metric("Arm Extension", st.session_state.extension_status)
                st.metric("Back Arch", st.session_state.back_arch_status)
            elif exercise == "Lunges":
                st.subheader("Lunge Metrics")
                st.metric("Front Knee Angle", f"{st.session_state.front_knee_angle}°")
                st.metric("Torso Angle", f"{st.session_state.torso_angle}°")
                st.metric("Balance Status", st.session_state.balance_status)

    st.title("AI Real-time GYM Coach")
    st.markdown("#### Real-time pose detection with proactive AI voice coaching")

    if not workout_started:
        st.markdown(
            f'<div style="border: 10px dashed #444; padding: 48px 32px; text-align: center; color: #888; margin: 32px 0;">'
            f'<h2 style="color:#ccc; margin-bottom:8px;">👈 Set your workout plan</h2>'
            f'<p style="font-size:1.05rem;">Choose your exercise, sets and reps in the sidebar,<br>'
            f'then click <strong>Start Workout</strong> to activate the camera.</p></div>',
            unsafe_allow_html=True
        )
    else:
        # Thread-safe video component
        context = webrtc_streamer(
            key="exercise-analysis",
            mode=WebRtcMode.SENDRECV,
            video_processor_factory=VideoProcessorClass,
            rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
            media_stream_constraints={
                "video": {"width": 320, "height": 240, "frameRate": 15},
                "audio": False
            },
            async_processing=True
        )

        if context.video_processor:
            context.video_processor.set_exercise(st.session_state.get("exercise_type", "Squats"))
            sync_metrics_update(context)

            latest_processor_metrics = context.video_processor.get_latest_metrics()
            if latest_processor_metrics:
                processor_reps = latest_processor_metrics.get("reps", 0)
                last_spoken = st.session_state.last_spoken_rep

                if processor_reps > last_spoken :#or latest_processor_metrics.get("extension_status"):
                    if st.session_state.voice_pipeline:
                        metric_context = latest_processor_metrics.copy()
                        metric_context["target_sets"] = st.session_state.get("target_sets", 0)
                        metric_context["sets_completed"] = st.session_state.get("sets_completed", 0)

                        #"Yahan audio directly play hoga, aur UI rendering par koi extra load nahi padega, jisse application smooth chalegi."
                        # st.session_state.voice_pipeline.process_event(
                        #     event= "rep_completed",#"ongoing_form_check",
                        #     exercise=st.session_state.get("exercise_type"),
                        #     metrics=metric_context
                        # )
                        audio = st.session_state.voice_pipeline.process_event(
                          event="rep_completed",
                          exercise=st.session_state.get("exercise_type"),
                          metrics=metric_context
                         )

                        if audio:
                          st.session_state.audio_to_play = audio

                        st.session_state.last_spoken_rep = processor_reps

        # "Auto-refresh ko 2 seconds ke interval par set kiya gaya hai, jisse UI consistently refresh hogi aur performance stable rahegi."
        if st.session_state.audio_to_play:

           st.audio(
              st.session_state.audio_to_play,
              format="audio/mp3",
              autoplay=True
        )
        st.session_state.audio_to_play = None

        st_autorefresh(interval=2000, key="gym_counter_refresh")

    inject_webrtc_styles()

    # --- History Block ---
    st.divider()
    st.markdown("#### 📊 Workout History")
    user_id = st.session_state.get("user_id", 1)
    try:
        history_rows = get_users_exercises(user_id)
        if history_rows and len(history_rows) > 0:
            arr = [{"Exercise": row['exercise_name'], "Reps": row['reps'], "Sets": row['sets'], "Time (sec)": int(row['time']) if row['time'] else 0, "Date": row['created_at']} for row in history_rows]
            df = pd.DataFrame(arr)
            if not df.empty:
                df["Date"] = pd.to_datetime(df["Date"]).dt.date
                agg_df = df.groupby(["Exercise", "Date"]).agg({"Reps": 'sum', "Sets": "sum", "Time (sec)": "sum"}).reset_index()
                agg_df.index += 1
                st.table(agg_df, border="horizontal")
        else:
            st.info("🏋️‍♂️ No workout history found. Complete a set to save progress!")
    except Exception as e:
        st.warning("Could not load workout history table.")

if __name__ == "__main__":
    main()
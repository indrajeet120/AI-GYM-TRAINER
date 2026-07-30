import streamlit as st
import time
from services.config.workout_config import METRICS_FIELDS
from services.persistence.exercise_repository import add_exercise


def sync_metrics_update(context):
    if not context or not hasattr(context, "state") or not context.state.playing:
        return
    
    processor = getattr(context, "video_processor", None)
    if not processor:
        return 
    
    exercise = st.session_state.get("exercise_type")
    if not exercise:
        return

    latest_metrics = processor.get_latest_metrics()
    if not latest_metrics:
        return
    
    reps = latest_metrics.get("reps", 0)
    if reps is None:
        reps = 0

    st.session_state.reps = reps

    fields = METRICS_FIELDS.get(exercise)
    if fields:
        for key, default in fields.items():
            st.session_state[key] = latest_metrics.get(key, default)

    reps_per_set = st.session_state.get("reps_per_set", 0)
    target_sets = st.session_state.get("target_sets", 0)

    if reps is not None and reps_per_set > 0 and target_sets > 0:
        sets_completed = reps // reps_per_set
        current_set_reps = reps % reps_per_set
        workout_completed = sets_completed >= target_sets 
    else:
        sets_completed = 0
        current_set_reps = 0
        workout_completed = False

    st.session_state.sets_completed = sets_completed
    st.session_state.current_set_reps = current_set_reps
    st.session_state.workout_completed = workout_completed

    last_saved_sets = st.session_state.get("last_saved_sets_completed", 0)
    exp_level = st.session_state.get("experience_level", "Intermediate")

    # 1. SET COMPLETED EVENT
    if target_sets > 0 and reps_per_set > 0 and sets_completed > last_saved_sets:
        newly_completed = sets_completed - last_saved_sets
        now_ts = time.time()
        started_at = st.session_state.get("set_cycle_started_at", now_ts)
        time_taken = now_ts - started_at
        user_id = st.session_state.get("user_id", 0)

        add_exercise(user_id, exercise, newly_completed * reps_per_set, newly_completed, time_taken)

        if st.session_state.get("voice_pipeline"):
            res = st.session_state.voice_pipeline.process_event(
                event="set_completed",
                exercise=exercise,
                metrics=latest_metrics,
                experience_level=exp_level
            )
            if res:
                audio, text = res if isinstance(res, tuple) else (res, "Great set completed!")
                if audio:
                    st.session_state.audio_to_play = audio
                if text:
                    st.session_state.coach_feedback_text = text
                st.rerun()

        st.session_state.set_cycle_started_at = now_ts
        st.session_state.last_saved_sets_completed = sets_completed

    # 2. WORKOUT COMPLETED EVENT
    if workout_completed and not st.session_state.get("last_notified_workout_complete", False):
        st.session_state.last_notified_workout_complete = True

        if st.session_state.get("voice_pipeline"):
            res = st.session_state.voice_pipeline.process_event(
                event="workout_completed",
                exercise=exercise,
                metrics=latest_metrics,
                experience_level=exp_level
            )
            if res:
                audio, text = res if isinstance(res, tuple) else (res, "Workout completed!")
                if audio:
                    st.session_state.audio_to_play = audio
                if text:
                    st.session_state.coach_feedback_text = text
                st.rerun()

    # 3. NO POSE DETECTED EVENT
    pose_detected = latest_metrics.get("pose_detected", True)
    if not pose_detected and st.session_state.get("voice_pipeline"):
        last_pose_alert = st.session_state.get("last_pose_alert_time", 0)
        if time.time() - last_pose_alert > 6.0:
            res = st.session_state.voice_pipeline.process_event(
                event="no_pose_detected",
                exercise=exercise,
                metrics={"issue": "No pose detected"},
                experience_level=exp_level
            )
            if res:
                audio, text = res if isinstance(res, tuple) else (res, "Please step inside the camera frame.")
                if audio:
                    st.session_state.audio_to_play = audio
                if text:
                    st.session_state.coach_feedback_text = text
                st.session_state.last_pose_alert_time = time.time()
                st.rerun()

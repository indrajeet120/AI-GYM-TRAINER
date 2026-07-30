import os
os.environ["QT_QPA_PLATFORM"] = "offscreen"
os.environ["OPENCV_VIDEOWRITE_GPU_API"] = "0"

import cv2
import av
import numpy as np
import mediapipe as mp
import threading
import time

from streamlit_webrtc import VideoProcessorBase
from detectors.squat import SquatDetector
from detectors.pushup import PushUpDetector
from detectors.biceps_curl import BicepsCurlDetector
from detectors.shoulder_press import ShoulderPressDetector
from detectors.lunges import LungesDetector

from services.config.workout_config import POSE_CONNECTIONS
from services.coaching.voice_pipeline import VoicePipeline
from services.coaching.tts import TextToSpeech


class VideoProcessorClass(VideoProcessorBase):
    def __init__(self):
        self._lock = threading.Lock()
        self._latest_metrics = None
        self._exercise_type = "Squats"
        self._experience_level = "Intermediate"
        self.frame_count = 0
        self.process_every = 2  # Process every 2nd frame for 30+ FPS responsiveness
        self.last_processed_frame = None
        self.prev_landmarks = None
        self.last_voice_eval_time = 0.0
        self.last_rep_count = 0

        self.voice_pipeline = VoicePipeline(tts=TextToSpeech())

        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=0,  # Ultra-fast lightweight model for 30+ FPS performance
            smooth_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self._detectors = {
            "Squats": SquatDetector(),
            "Push-ups": PushUpDetector(),
            "Biceps Curls (Dumbbell)": BicepsCurlDetector(),
            "Shoulder Press": ShoulderPressDetector(),
            "Lunges": LungesDetector(),
        }

    def set_latest_metrics(self, metrics):
        with self._lock:
            self._latest_metrics = metrics.copy()

    def get_latest_metrics(self):
        with self._lock:
            return None if self._latest_metrics is None else self._latest_metrics.copy()

    def set_exercise(self, exercise_type):
        with self._lock:
            self._exercise_type = exercise_type

    def get_exercise(self):
        with self._lock:
            return self._exercise_type

    def set_experience_level(self, level):
        with self._lock:
            self._experience_level = level

    def get_experience_level(self):
        with self._lock:
            return self._experience_level

    def smooth_points(self, landmarks, alpha=0.65):
        if self.prev_landmarks is None:
            self.prev_landmarks = landmarks
            return landmarks
        smooth = []
        for prev, curr in zip(self.prev_landmarks, landmarks):
            lm = type(curr)()
            lm.x = alpha * prev.x + (1-alpha) * curr.x
            lm.y = alpha * prev.y + (1-alpha) * curr.y
            lm.z = alpha * prev.z + (1-alpha) * curr.z
            lm.visibility = curr.visibility
            smooth.append(lm)
        self.prev_landmarks = smooth
        return smooth

    def _draw_skeleton(self, img, landmarks):
        h, w = img.shape[:2]
        if not landmarks:
            return
        for start_idx, end_idx in POSE_CONNECTIONS:
            if start_idx < len(landmarks) and end_idx < len(landmarks):
                p1 = landmarks[start_idx]
                p2 = landmarks[end_idx]
                cv2.line(img, (int(p1.x * w), int(p1.y * h)), (int(p2.x * w), int(p2.y * h)), (0, 255, 0), 2)

    def recv(self, frame):
        try:
            image = frame.to_ndarray(format="bgr24")
            image = cv2.flip(image, 1)
            self.frame_count += 1
            
            if self.frame_count % self.process_every != 0:
                if self.last_processed_frame is not None:
                    return av.VideoFrame.from_ndarray(self.last_processed_frame, format="bgr24")
                return av.VideoFrame.from_ndarray(image, format="bgr24")

            # Resize frame for ultra-fast MediaPipe inference (480x360)
            small_rgb = cv2.cvtColor(cv2.resize(image, (480, 360)), cv2.COLOR_BGR2RGB)
            results = self.pose.process(small_rgb)
            now = time.time()

            if results.pose_landmarks:
                landmarks = results.pose_landmarks.landmark
                landmarks = self.smooth_points(landmarks)
                self._draw_skeleton(image, landmarks)

                ex_type = self.get_exercise()
                exp_level = self.get_experience_level()
                detector = self._detectors.get(ex_type)

                if detector:
                    try:
                        metrics = detector.process(landmarks)
                        if metrics is None:
                            metrics = self.get_latest_metrics() or {"reps": 0, "pose_detected": True}
                    except Exception:
                        metrics = self.get_latest_metrics() or {"reps": 0, "pose_detected": True}

                    metrics["pose_detected"] = True 
                    self.set_latest_metrics(metrics)

                    reps = metrics.get("reps", 0)
                    event_type = "ongoing_form_check"

                    if reps > self.last_rep_count:
                        event_type = "rep_completed"
                        self.last_rep_count = reps

                    # Asynchronous evaluation: triggers TTS in background thread without blocking recv()
                    if event_type == "rep_completed" or (now - self.last_voice_eval_time > 1.8):
                        self.voice_pipeline.evaluate_and_speak(event_type, ex_type, metrics, exp_level)
                        self.last_voice_eval_time = now
                else:
                    self.set_latest_metrics({"pose_detected": True, "reps": 0})
            else:
                old_m = self.get_latest_metrics() or {"reps": 0}
                old_m["pose_detected"] = False
                self.set_latest_metrics(old_m)

                if now - self.last_voice_eval_time > 5.0:
                    self.voice_pipeline.evaluate_and_speak("no_pose_detected", self.get_exercise(), old_m, self.get_experience_level())
                    self.last_voice_eval_time = now
            
            self.last_processed_frame = image
            return av.VideoFrame.from_ndarray(image, format="bgr24")
        except Exception as e:
            print("VIDEO PROCESSOR ERROR:", e)
            return av.VideoFrame.from_ndarray(image, format="bgr24")
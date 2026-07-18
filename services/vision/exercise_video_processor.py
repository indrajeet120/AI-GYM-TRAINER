# import os
# import cv2
# import av
# import numpy as np
# import mediapipe as mp
# import threading
# from streamlit_webrtc import VideoProcessorBase
# from mediapipe.tasks import python
# from mediapipe.tasks.python import vision
# from detectors.squat import SquatDetector
# from detectors.pushup import PushUpDetector
# from detectors.biceps_curl import BicepsCurlDetector
# from detectors.shoulder_press import ShoulderPressDetector
# from detectors.lunges import LungesDetector
# from services.config.workout_config import POSE_CONNECTIONS


# class VideoProcessorClass(VideoProcessorBase):
#     def __init__(self):
#         self._lock = threading.Lock()
#         self._latest_metrics = None
#         self._exercise_type = "Squats"

#         model_path = os.path.join(os.getcwd(), "ml_models", "pose_landmarker_full.task")
#         base_option = python.BaseOptions(model_asset_path=model_path)

#         options = vision.PoseLandmarkerOptions(
#             base_options=base_option,
#             running_mode=vision.RunningMode.VIDEO,
#             min_pose_detection_confidence=0.7,
#             min_pose_presence_confidence=0.7,
#             min_tracking_confidence=0.7,
#             output_segmentation_masks=False
#         )

#         self._landmarker = vision.PoseLandmarker.create_from_options(options)

#         self._detectors = {
#             "Squats": SquatDetector(),
#             "Push-ups": PushUpDetector(),
#             "Biceps Curls (Dumbbell)": BicepsCurlDetector(),
#             "Shoulder Press": ShoulderPressDetector(),
#             "Lunges": LungesDetector(),
#         }

#         self._frame_timestamps_ms = 0
    
#     def set_latest_metrics(self, metrics):
#         with self._lock:
#             self._latest_metrics = metrics.copy()

#     def get_latest_metrics(self):
#         with self._lock:
#             return None if self._latest_metrics is None else self._latest_metrics.copy()
        
#     def set_exercise(self, exercise_type):
#         with self._lock:
#             self._exercise_type = exercise_type

#     def get_exercise(self):
#         with self._lock:
#             return self._exercise_type
        
#     # def _draw_skeleton(self, img, landmarks):
#     #     h, w = img.shape[:2]

#     #     for start_idx, end_idx in POSE_CONNECTIONS:
#     #         p1 = landmarks[start_idx]
#     #         p2 = landmarks[end_idx]

#     #         if p1.visibility > 0.7 and p2.visibility > 0.7:
#     #             cv2.line(
#     #                 img,
#     #                 (int(p1.x * w), int(p1.y * h)),
#     #                 (int(p2.x * w), int(p2.y * h)),
#     #                 (0, 255, 0),
#     #                 8
#     #             )
        
#     #     for lm in landmarks:
#     #         if lm.visibility > 0.7:
#     #             cv2.circle(
#     #                 img, 
#     #                 (int(lm.x * w), int(lm.y * h)),
#     #                 8,
#     #                 (255, 0, 0),
#     #                 -1
#     #             )


#     def _draw_skeleton(self, img, landmarks):
#      h, w = img.shape[:2]

#     # Draw connections
#      for start_idx, end_idx in POSE_CONNECTIONS:
#         p1 = landmarks[start_idx]
#         p2 = landmarks[end_idx]

#         cv2.line(
#             img,
#             (int(p1.x * w), int(p1.y * h)),
#             (int(p2.x * w), int(p2.y * h)),
#             (0, 255, 0),
#             4
#         )

#     # Draw landmarks
#      for lm in landmarks:
#         cv2.circle(
#             img,
#             (int(lm.x * w), int(lm.y * h)),
#             6,
#             (0, 0, 255),
#             -1
#         )
            
#     def _draw_no_pose_warnings(self, img):
#         cv2.putText(
#             img,
#             "NO POSE DETECTED",
#             (30, 50),
#             cv2.FONT_HERSHEY_SIMPLEX,
#             1,
#             (0, 255, 0),
#             2,
#             cv2.LINE_AA,
#         )

#         cv2.putText(
#             img,
#             "PLEASE FACE THE CAMERA",
#             (30, 100),
#             cv2.FONT_HERSHEY_SIMPLEX,
#             1,
#             (0, 255, 0),
#             2,
#             cv2.LINE_AA,
#         )

#     def _draw_overlays(self, img, metrics, ex_type):
#         if ex_type == "Squats":
#             self._draw_squats_overlays(img, metrics)
#         elif ex_type == "Push-ups":
#             self._draw_pushup_overlays(img, metrics)
#         elif ex_type == "Biceps Curls (Dumbbell)":
#             self._draw_curl_overlays(img, metrics)
#         elif ex_type == "Shoulder Press":
#             self._draw_press_overlays(img, metrics)
#         elif ex_type == "Lunges":
#             self._draw_lunge_overlays(img, metrics)


#     def _draw_squats_overlays(self, img, metrics):
#         h, _ = img.shape[:2]

#         cv2.putText(
#             img,
#             f"DEPTH: {metrics['depth_status']}",
#             (20, h - 20),
#             cv2.FONT_HERSHEY_SIMPLEX,
#             1,
#             (0, 255, 0),
#             2,
#         )
    
#     def _draw_pushup_overlays(self, img, metrics):
#         h, _ = img.shape[:2]

#         cv2.putText(
#             img,
#             f"BODY: {metrics['body_alignment']} | HIP: {metrics['hip_status']}",
#             (20, h - 20),
#             cv2.FONT_HERSHEY_SIMPLEX,
#             1,
#             (0, 255, 0),
#             2,
#         )

#     def _draw_curl_overlays(self, img, metrics):
#         h, _ = img.shape[:2]

#         cv2.putText(
#             img,
#             f"SWING: {metrics['swing_status']}",
#             (20, h - 20),
#             cv2.FONT_HERSHEY_SIMPLEX,
#             1,
#             (0, 255, 0),
#             2,
#         )

#     def _draw_press_overlays(self, img, metrics):
#         h, _ = img.shape[:2]

#         cv2.putText(
#             img,
#             f"EXT: {metrics['extension_status']} | BACK: {metrics['back_arch_status']}",
#             (20, h - 20),
#             cv2.FONT_HERSHEY_SIMPLEX,
#             1,
#             (0, 255, 0),
#             2,
#         )

#     def _draw_lunge_overlays(self, img, metrics):
#         h, _ = img.shape[:2]

#         cv2.putText(
#             img,
#             f"BALANCE: {metrics['balance_status']}",
#             (20, h - 20),
#             cv2.FONT_HERSHEY_SIMPLEX,
#             1,
#             (0, 255, 0),
#             2,
#         )

#     # def recv(self, frame):
#     #     image = np.asarray(
#     #         cv2.flip(frame.to_ndarray(format="bgr24"), 1),
#     #         dtype=np.uint8
#     #     )

#     #     # mp_image = mp.Image(
#     #     #     image_format=mp.ImageFormat.SRGB,
#     #     #     data=cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
#     #     # )

#     #     rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

#     #     mp_image = mp.Image(
#     #        image_format=mp.ImageFormat.SRGB,
#     #        data=rgb_image
#     #     )

#     #     self._frame_timestamps_ms += 30
#     #     result = self._landmarker.detect_for_video(mp_image, self._frame_timestamps_ms)
        
#     #     print("Pose landmarks:", len(result.pose_landmarks))  #new

#     #     if result.pose_landmarks:
#     #         landmarks = result.pose_landmarks[0]

#     #         self._draw_skeleton(image, landmarks)

#     #         ex_type = self.get_exercise()

#     #         detector = self._detectors.get(ex_type)

#     #         if detector:
#     #             metrics = detector.process(landmarks)

#     #             metrics["pose_detected"] = True

#     #             self._draw_overlays(image, metrics, ex_type)

#     #             self.set_latest_metrics(metrics)
#     #     else:
#     #         self._draw_no_pose_warnings(image)
            
#     #         with self._lock:
#     #             if self._latest_metrics is not None:
#     #                 self._latest_metrics["pose_detected"] = False
#     #             else:
#     #                 self._latest_metrics = {"pose_detected": False}

#     #     return av.VideoFrame.from_ndarray(image, format="bgr24")
    
#     def recv(self, frame):
#      image = frame.to_ndarray(format="bgr24")
#      image = cv2.flip(image, 1)

#      rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
#      rgb_image = np.ascontiguousarray(rgb_image)
 
#      mp_image = mp.Image.create_from_array(
#         rgb_image,
#         image_format=mp.ImageFormat.SRGB
#      )

#      import time
#      self._frame_timestamps_ms = int(time.time() * 1000)

#      result = self._landmarker.detect_for_video(
#          mp_image,
#          self._frame_timestamps_ms
#      )

#      print("Pose landmarks:", len(result.pose_landmarks) if result.pose_landmarks else 0)

#      if result.pose_landmarks:
#         landmarks = result.pose_landmarks[0]

#         self._draw_skeleton(image, landmarks)

#         ex_type = self.get_exercise()
#         detector = self._detectors.get(ex_type)

#         if detector:
#             metrics = detector.process(landmarks)
#             metrics["pose_detected"] = True

#             self._draw_overlays(image, metrics, ex_type)
#             self.set_latest_metrics(metrics)

#      else:
#         self._draw_no_pose_warnings(image)

#         with self._lock:
#             self._latest_metrics = {"pose_detected": False}

#      return av.VideoFrame.from_ndarray(image, format="bgr24")


# import os
# import cv2
# import av
# import numpy as np
# import mediapipe as mp
# import threading
# import time

# from streamlit_webrtc import VideoProcessorBase
# # from mediapipe.tasks import python
# # from mediapipe.tasks.python import vision

# from detectors.squat import SquatDetector
# from detectors.pushup import PushUpDetector
# from detectors.biceps_curl import BicepsCurlDetector
# from detectors.shoulder_press import ShoulderPressDetector
# from detectors.lunges import LungesDetector

# from services.config.workout_config import POSE_CONNECTIONS


# class VideoProcessorClass(VideoProcessorBase):
#     def __init__(self):
#         self._lock = threading.Lock()
#         self._latest_metrics = None
#         self._exercise_type = "Squats"
#         self.frame_count = 0
#         self.process_every = 5
#         self.last_processed_frame = None
#         self.prev_landmarks = None
#         self.last_extension_status = None

#         # model_path = os.path.join(
#         #     os.getcwd(),
#         #     "ml_models",
#         #     "pose_landmarker_full.task"
#         # )

#         # base_option = python.BaseOptions(model_asset_path=model_path)

#         # options = vision.PoseLandmarkerOptions(
#         #     base_options=base_option,
#         #     running_mode=vision.RunningMode.VIDEO,
#         #     min_pose_detection_confidence=0.5,
#         #     min_pose_presence_confidence=0.5,
#         #     min_tracking_confidence=0.5,
#         #     output_segmentation_masks=False
#         # )

#         # self._landmarker = vision.PoseLandmarker.create_from_options(options)
#         self.mp_pose = mp.solutions.pose
#         self.pose = self.mp_pose.Pose(
#          static_image_mode=False,
#          model_complexity=1,
#          smooth_landmarks=True,
#          min_detection_confidence=0.6,
#          min_tracking_confidence=0.7
#         )
#         self._detectors = {
#             "Squats": SquatDetector(),
#             "Push-ups": PushUpDetector(),
#             "Biceps Curls (Dumbbell)": BicepsCurlDetector(),
#             "Shoulder Press": ShoulderPressDetector(),
#             "Lunges": LungesDetector(),
#         }

#         self._frame_timestamps_ms =0

#     # ------------------ THREAD SAFE ------------------
#     def set_latest_metrics(self, metrics):
#         with self._lock:
#             self._latest_metrics = metrics.copy()

#     def get_latest_metrics(self):
#         with self._lock:
#             return None if self._latest_metrics is None else self._latest_metrics.copy()

#     def set_exercise(self, exercise_type):
#         with self._lock:
#             self._exercise_type = exercise_type

#     def get_exercise(self):
#         with self._lock:
#             return self._exercise_type
        
    
#     def smooth_points(self, landmarks, alpha=0.65):

#      if self.prev_landmarks is None:
#         self.prev_landmarks = landmarks
#         return landmarks

#      smooth = []

#      for prev, curr in zip(self.prev_landmarks, landmarks):

#         lm = type(curr)()

#         lm.x = alpha * prev.x + (1-alpha) * curr.x
#         lm.y = alpha * prev.y + (1-alpha) * curr.y
#         lm.z = alpha * prev.z + (1-alpha) * curr.z
#         lm.visibility = curr.visibility

#         smooth.append(lm)

#      self.prev_landmarks = smooth

#      return smooth




#     # ------------------ DRAW SKELETON ------------------
#     def _draw_skeleton(self, img, landmarks):
#         h, w = img.shape[:2]

#         if not landmarks:
#             return

#         # connections
#         for start_idx, end_idx in POSE_CONNECTIONS:
#             if start_idx < len(landmarks) and end_idx < len(landmarks):
#                 p1 = landmarks[start_idx]
#                 p2 = landmarks[end_idx]

#                 cv2.line(
#                     img,
#                     (int(p1.x * w), int(p1.y * h)),
#                     (int(p2.x * w), int(p2.y * h)),
#                     (0, 255, 0),
#                     2
#                 )

#         # points
#         for lm in landmarks:
#             cv2.circle(
#                 img,
#                 (int(lm.x * w), int(lm.y * h)),
#                 3,
#                 (0, 0, 255),
#                 -1
#             )

#     # ------------------ NO POSE WARNING ------------------
#     def _draw_no_pose_warnings(self, img):
#         cv2.putText(
#             img,
#             "NO POSE DETECTED",
#             (30, 50),
#             cv2.FONT_HERSHEY_SIMPLEX,
#             1,
#             (0, 255, 0),
#             2
#         )

#         cv2.putText(
#             img,
#             "PLEASE FACE CAMERA",
#             (30, 100),
#             cv2.FONT_HERSHEY_SIMPLEX,
#             1,
#             (0, 255, 0),
#             2
#         )

#     # ------------------ OVERLAYS ------------------
#     def _draw_overlays(self, img, metrics, ex_type):

#      if not metrics:
#         return

#      if ex_type == "Squats":
#         cv2.putText(
#             img,
#             f"DEPTH: {metrics.get('depth_status','N/A')}",
#             (20,50),
#             cv2.FONT_HERSHEY_SIMPLEX,
#             1,
#             (0,255,0),
#             2
#         )

#      elif ex_type == "Push-ups":
#         cv2.putText(
#             img,
#             f"BODY: {metrics.get('body_alignment','N/A')} | HIP: {metrics.get('hip_status','N/A')}",
#             (20,50),
#             cv2.FONT_HERSHEY_SIMPLEX,
#             1,
#             (0,255,0),
#             2
#         )

#      elif ex_type == "Biceps Curls (Dumbbell)":
#         cv2.putText(
#             img,
#             f"SWING: {metrics.get('swing_status','N/A')}",
#             (20,50),
#             cv2.FONT_HERSHEY_SIMPLEX,
#             1,
#             (0,255,0),
#             2
#         )

#      elif ex_type == "Shoulder Press":
#         cv2.putText(
#             img,
#             f"EXT: {metrics.get('extension_status','N/A')} | BACK: {metrics.get('back_arch_status','N/A')}",
#             (20,50),
#             cv2.FONT_HERSHEY_SIMPLEX,
#             1,
#             (0,255,0),
#             2
#         )

#      elif ex_type == "Lunges":
#         cv2.putText(
#             img,
#             f"BALANCE: {metrics.get('balance_status','N/A')}",
#             (20,50),
#             cv2.FONT_HERSHEY_SIMPLEX,
#             1,
#             (0,255,0),
#             2
#         )

#     # ------------------ MAIN PIPELINE ------------------
#     def recv(self, frame):
#      try:
#         print("FRAME RECEIVED")
#         # ------------------ FRAME TO ARRAY ------------------
#         image = frame.to_ndarray(format="bgr24")

#         # Mirror camera
#         image = cv2.flip(image, 1)

#         # ------------------ FRAME SKIP FOR PERFORMANCE ------------------
#         self.frame_count += 1
#         if self.frame_count % self.process_every != 0:
#          if self.last_processed_frame is not None:
#           return av.VideoFrame.from_ndarray(self.last_processed_frame, format="bgr24")
#          return av.VideoFrame.from_ndarray(image, format="bgr24")

#         # ------------------ BRIGHTNESS IMPROVEMENT ------------------
#         image = cv2.convertScaleAbs(image, alpha=1.2, beta=20)

#         # ------------------ BGR -> RGB ------------------
#         rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

#         # ------------------ POSE DETECTION ------------------
#         results = self.pose.process(rgb)

#         if results.pose_landmarks:
#             landmarks = results.pose_landmarks.landmark
#             landmarks = self.smooth_points(landmarks)
#             print("POSE DETECTED")
#             # Draw skeleton
#             self._draw_skeleton(image, landmarks)

#             # Current selected exercise
#             ex_type = self.get_exercise()
#             detector = self._detectors.get(ex_type)

#             if detector:
#                 try:
#                   metrics = detector.process(landmarks)
#                   if metrics is None:
#                    print("Detector failed for:", ex_type)
#                   else:
#                    print("DETECTOR OUTPUT:", metrics)

#                 except Exception as e:
#                   import traceback
#                   traceback.print_exc()
#                   metrics = None

#                 # ------------------ DETECTOR FAILED ------------------
#                 if metrics is None:

#                   metrics = {
#                    "reps": 0,
#                    "pose_detected": True
#                    }

#                 metrics["pose_detected"] = True 

#                 # ------------------ ALWAYS UPDATE ------------------
#                 self._draw_overlays(image, metrics, ex_type)
#                 self.set_latest_metrics(metrics)

#             else:
#                 self.set_latest_metrics({"pose_detected": True})

#         # ------------------ NO POSE DETECTED ------------------
#         else:
#             print("NO POSE")
#             self._draw_no_pose_warnings(image)
#             self.set_latest_metrics({"pose_detected": False})
        
#         # ------------------ SAVE LAST FRAME ------------------
#         self.last_processed_frame = image.copy()
#         # ------------------ RETURN FRAME ------------------
#         return av.VideoFrame.from_ndarray(image, format="bgr24")

#      except Exception as e:
#         print("VIDEO PROCESSOR ERROR:", e)

#         return av.VideoFrame.from_ndarray(image, format="bgr24")












# 
import os
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


class VideoProcessorClass(VideoProcessorBase):
    def __init__(self):
        self._lock = threading.Lock()
        self._latest_metrics = None
        self._exercise_type = "Squats"
        self.frame_count = 0
        self.process_every = 3  
        self.last_processed_frame = None
        self.prev_landmarks = None

        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            smooth_landmarks=True,
            min_detection_confidence=0.6,
            min_tracking_confidence=0.7
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

    def _draw_no_pose_warnings(self, img):
        cv2.putText(img, "NO POSE DETECTED", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    def recv(self, frame):
        try:
            image = frame.to_ndarray(format="bgr24")
            image = cv2.flip(image, 1)
            self.frame_count += 1
            
            if self.frame_count % self.process_every != 0:
                if self.last_processed_frame is not None:
                    return av.VideoFrame.from_ndarray(self.last_processed_frame, format="bgr24")
                return av.VideoFrame.from_ndarray(image, format="bgr24")

            image = cv2.convertScaleAbs(image, alpha=1.2, beta=20)
            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = self.pose.process(rgb)

            if results.pose_landmarks:
                landmarks = results.pose_landmarks.landmark
                landmarks = self.smooth_points(landmarks)
                self._draw_skeleton(image, landmarks)

                ex_type = self.get_exercise()
                detector = self._detectors.get(ex_type)

                if detector:
                    try:
                        metrics = detector.process(landmarks)
                        if metrics is None:
                            metrics = self.get_latest_metrics() or {"reps": 0, "pose_detected": True}
                    except Exception as e:
                        metrics = self.get_latest_metrics() or {"reps": 0, "pose_detected": True}

                    metrics["pose_detected"] = True 
                    self.set_latest_metrics(metrics)
                else:
                    self.set_latest_metrics({"pose_detected": True, "reps": 0})
            else:
                old_m = self.get_latest_metrics() or {"reps": 0}
                old_m["pose_detected"] = False
                self.set_latest_metrics(old_m)
            
            self.last_processed_frame = image.copy()
            return av.VideoFrame.from_ndarray(image, format="bgr24")
        except Exception as e:
            print("VIDEO PROCESSOR ERROR:", e)
            return av.VideoFrame.from_ndarray(image, format="bgr24")
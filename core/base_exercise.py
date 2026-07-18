import math
from abc import ABC ,abstractmethod

# class BaseExercise(ABC):
#     def __init__(self):
#         self.reps =0
#         self.stage = None

#     def calculate_angle(self, a, b, c):
#      if a is None or b is None or c is None:
#         return None

#      try:
#         ax, ay = a
#         bx, by = b
#         cx, cy = c

#         angle = math.degrees(
#             math.atan2(cy - by, cx - bx) -
#             math.atan2(ay - by, ax - bx)
#         )

#         angle = abs(angle)

#         if angle > 180:
#             angle = 360 - angle

#         return angle

#      except Exception:
#         return None
#     # def get_point(self, landmarks, idx):
#     #     p = landmarks[idx]
          
#     def get_point(self, landmarks, idx):
#      if landmarks is None:
#         return None

#      if idx >= len(landmarks):
#         return None

#      lm = landmarks[idx]

#      if lm is None:
#         return None

#      return (lm.x, lm.y)

#     @abstractmethod
#     def process(self, landmarks):
#         pass

#     @abstractmethod
#     def reset(self):
#         pass


import math
from abc import ABC

class BaseExercise(ABC):

    def __init__(self):
        self.reps = 0
        self.stage = None

    def calculate_angle(self, a, b, c):
        if a is None or b is None or c is None:
            return None

        try:
            ax, ay = a
            bx, by = b
            cx, cy = c

            radians = (
                math.atan2(cy - by, cx - bx)
                -
                math.atan2(ay - by, ax - bx)
            )

            angle = abs(math.degrees(radians))

            if angle > 180:
                angle = 360 - angle

            return angle

        except Exception as e:
            print("ANGLE ERROR:", e)
            return None

    # ===== THIS METHOD IS REQUIRED =====
    def get_point(self, landmarks, index):
        try:
            if landmarks is None:
                return None

            lm = landmarks[index]

            return (
                float(lm.x),
                float(lm.y)
            )

        except Exception as e:
            print("POINT ERROR:", e)
            return None
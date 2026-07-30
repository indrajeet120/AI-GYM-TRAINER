import time
from core.base_exercise import BaseExercise


class SquatDetector(BaseExercise):
    DOWN_THRESHOLD = 100
    UP_THRESHOLD = 160
    MIN_VISIBILITY = 0.4

    LEFT_SHOULDER = 11
    RIGHT_SHOULDER = 12
    LEFT_HIP = 23
    RIGHT_HIP = 24
    LEFT_KNEE = 25
    RIGHT_KNEE = 26
    LEFT_ANKLE = 27
    RIGHT_ANKLE = 28

    def __init__(self):
        super().__init__()
        self.reset()

    def reset(self) -> None:
        self.reps = 0
        self.stage = None
        self.stage_start_time = None
        self.last_rep_time = time.time()
        self.min_knee_angle_in_rep = 180

    def process(self, landmarks):
        try:
            left_angle = self.calculate_angle(
                self.get_point(landmarks, self.LEFT_HIP),
                self.get_point(landmarks, self.LEFT_KNEE),
                self.get_point(landmarks, self.LEFT_ANKLE)
            )

            right_angle = self.calculate_angle(
                self.get_point(landmarks, self.RIGHT_HIP),
                self.get_point(landmarks, self.RIGHT_KNEE),
                self.get_point(landmarks, self.RIGHT_ANKLE)
            )

            if left_angle is None or right_angle is None:
                return {
                    "reps": self.reps,
                    "pose_detected": True,
                    "inactivity_warning": False
                }

            if left_angle < right_angle:
                knee_angle = left_angle
                hip_idx, knee_idx, shoulder_idx = self.LEFT_HIP, self.LEFT_KNEE, self.LEFT_SHOULDER
            else:
                knee_angle = right_angle
                hip_idx, knee_idx, shoulder_idx = self.RIGHT_HIP, self.RIGHT_KNEE, self.RIGHT_SHOULDER

            back_angle = self.calculate_angle(
                self.get_point(landmarks, shoulder_idx),
                self.get_point(landmarks, hip_idx),
                self.get_point(landmarks, knee_idx)
            )
            if back_angle is None:
                back_angle = 180

            now = time.time()
            speed_status = "NORMAL"
            partial_rep = False

            # Track minimum depth reached during current rep cycle
            if self.stage == "down":
                self.min_knee_angle_in_rep = min(self.min_knee_angle_in_rep, knee_angle)

            # Stage Transitions & Speed Detection
            if knee_angle < self.DOWN_THRESHOLD:
                if self.stage != "down":
                    self.stage = "down"
                    self.stage_start_time = now
                    self.min_knee_angle_in_rep = knee_angle

            if knee_angle > self.UP_THRESHOLD and self.stage == "down":
                rep_duration = now - (self.stage_start_time or now)
                self.stage = "up"
                
                # Range of motion check
                if self.min_knee_angle_in_rep > (self.DOWN_THRESHOLD - 5):
                    partial_rep = True

                # Speed check: rep under 0.85s is rushing
                if rep_duration < 0.85:
                    speed_status = "TOO FAST"
                else:
                    speed_status = "CONTROLLED"

                self.reps += 1
                self.last_rep_time = now
                self.min_knee_angle_in_rep = 180

            # Inactivity Check (>8 seconds standing without starting down stage)
            inactivity = (now - self.last_rep_time > 8.0) and (self.stage != "down")

            # Depth Status
            if knee_angle < 85:
                depth = "DEEP SQUAT"
            elif knee_angle < self.DOWN_THRESHOLD:
                depth = "GOOD DEPTH"
            elif self.stage == "down" and knee_angle > self.DOWN_THRESHOLD + 10:
                depth = "PARTIAL DEPTH"
            elif self.stage == "up":
                depth = "STANDING"
            else:
                depth = "START"

            # Posture Status
            if back_angle < 45:
                posture = "Torso Collapse"
            elif back_angle < 65:
                posture = "Excessive Forward Lean"
            else:
                posture = "Good Spine"

            rom_status = "PARTIAL" if partial_rep else ("FULL" if depth in ["DEEP SQUAT", "GOOD DEPTH"] else "NORMAL")

            return {
                "reps": self.reps,
                "knee_angle": int(knee_angle),
                "back_angle": int(back_angle),
                "depth_status": depth,
                "posture_status": posture,
                "speed_status": speed_status,
                "rom_status": rom_status,
                "partial_rep": partial_rep,
                "inactivity_warning": inactivity,
                "pose_detected": True
            }

        except Exception as e:
            print("SQUAT ERROR:", e)
            return None
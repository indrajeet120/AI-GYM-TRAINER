from core.base_exercise import BaseExercise


class ShoulderPressDetector(BaseExercise):
    UP_THRESHOLD = 160
    DOWN_THRESHOLD = 90
    MIN_VISIBILITY = 0.4

    LEFT_SHOULDER = 11
    LEFT_ELBOW = 13
    LEFT_WRIST = 15
    RIGHT_SHOULDER = 12
    RIGHT_ELBOW = 14
    RIGHT_WRIST = 16
    LEFT_HIP = 23
    RIGHT_HIP = 24
    LEFT_KNEE = 25
    RIGHT_KNEE = 26

    # def __init__(self):
    #     super().__init__()
    def __init__(self):
     super().__init__()

     self.reps = 0
     self.stage = None

     # For stable state change detection
     self.last_extension_status = None
     self.last_back_arch_status = None

    def reset(self) -> None:
        self.reps = 0
        self.stage = None

    def process(self, landmarks):
    # ---------- BASIC CHECK ----------
     if landmarks is None or len(landmarks) < 33:
        return {
            "reps": self.reps,
            "elbow_angle": 0,
            "extension_status": "N/A",
            "back_arch_status": "N/A",
        }

     try:
        left_vis = landmarks[self.LEFT_ELBOW].visibility
        right_vis = landmarks[self.RIGHT_ELBOW].visibility

        if left_vis >= right_vis:
            shoulder_idx = self.LEFT_SHOULDER
            elbow_idx = self.LEFT_ELBOW
            wrist_idx = self.LEFT_WRIST
            hip_idx = self.LEFT_HIP
            knee_idx = self.LEFT_KNEE
        else:
            shoulder_idx = self.RIGHT_SHOULDER
            elbow_idx = self.RIGHT_ELBOW
            wrist_idx = self.RIGHT_WRIST
            hip_idx = self.RIGHT_HIP
            knee_idx = self.RIGHT_KNEE

        # ---------- ANGLE ----------
        elbow_angle = self.calculate_angle(
            self.get_point(landmarks, shoulder_idx),
            self.get_point(landmarks, elbow_idx),
            self.get_point(landmarks, wrist_idx),
        )

        if elbow_angle is None:
            elbow_angle = 0

        # ---------- REP COUNT ----------
        if elbow_angle >= self.UP_THRESHOLD:
            self.stage = "up"

        if elbow_angle <= self.DOWN_THRESHOLD and self.stage == "up":
            self.stage = "down"
            self.reps += 1

      # ---------- EXTENSION STATUS (FIXED) ----------
        if elbow_angle >= 162:
          extension_status = "FULL EXTENSION"

        elif elbow_angle >= 140:
         extension_status = "NEARLY EXTENDED"

        elif elbow_angle >= 90:
         extension_status = "PRESSING"

        else:
         extension_status = "START POSITION"

        # ---------- BACK ANGLE ----------
        back_angle = self.calculate_angle(
            self.get_point(landmarks, shoulder_idx),
            self.get_point(landmarks, hip_idx),
            self.get_point(landmarks, knee_idx),
        )

        if back_angle is None:
            back_angle = 180

        # ---------- BACK STATUS ----------
        if back_angle >= 160:
            back_arch_status = "Neutral"
        elif back_angle >= 140:
            back_arch_status = "Slight Arch"
        else:
            back_arch_status = "Excessive Arch"
        
        state_changed = extension_status != self.last_extension_status
        self.last_extension_status = extension_status


        return {
            "reps": self.reps,
            "elbow_angle": int(elbow_angle),
            "extension_status": extension_status,
            "back_arch_status": back_arch_status,
            "state_changed": state_changed
        }

     except Exception as e:
        print("ShoulderPressDetector ERROR:", e)
        return {
            "reps": self.reps,
            "elbow_angle": 0,
            "extension_status": "N/A",
            "back_arch_status": "N/A",
        }
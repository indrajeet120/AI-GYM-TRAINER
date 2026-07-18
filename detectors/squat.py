from core.base_exercise import BaseExercise


class SquatDetector(BaseExercise):

    DOWN_THRESHOLD = 100
    UP_THRESHOLD = 160

    MIN_VISIBILITY = 0.4


    LEFT_HIP=23
    RIGHT_HIP=24

    LEFT_KNEE=25
    RIGHT_KNEE=26

    LEFT_ANKLE=27
    RIGHT_ANKLE=28

    LEFT_SHOULDER=11
    RIGHT_SHOULDER=12



    def process(self,landmarks):

        try:

            left_angle=self.calculate_angle(
                self.get_point(landmarks,23),
                self.get_point(landmarks,25),
                self.get_point(landmarks,27)
            )


            right_angle=self.calculate_angle(
                self.get_point(landmarks,24),
                self.get_point(landmarks,26),
                self.get_point(landmarks,28)
            )


            # if left_angle is None or right_angle is None:
            #     return None
            if left_angle is None or right_angle is None:
              return {
               "reps": self.reps,
               "pose_detected": True
               }

            if left_angle < right_angle:

                knee_angle=left_angle
                hip=23
                knee=25
                shoulder=11

            else:

                knee_angle=right_angle
                hip=24
                knee=26
                shoulder=12



            back_angle=self.calculate_angle(
                self.get_point(landmarks,shoulder),
                self.get_point(landmarks,hip),
                self.get_point(landmarks,knee)
            )


            if back_angle is None:
                back_angle = 180



            if knee_angle < self.DOWN_THRESHOLD:
                self.stage="down"



            if knee_angle > self.UP_THRESHOLD and self.stage=="down":

                self.stage="up"
                self.reps+=1



            if knee_angle < 90:
             depth = "DEEP SQUAT"

            elif knee_angle < self.DOWN_THRESHOLD:
              depth = "GOOD DEPTH"

            elif self.stage == "up":
             depth = "STANDING"

            else:
             depth = "START"



            return {

                "reps":self.reps,

                "knee_angle":int(knee_angle),

                "back_angle":int(back_angle),

                "depth_status":depth,
                
                "pose_detected": True
            }


        except Exception as e:

            print("SQUAT ERROR",e)

            return None
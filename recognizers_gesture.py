from mediapipe.tasks.python.vision.gesture_recognizer import GestureRecognizerResult
from mediapipe.tasks.python.vision.hand_landmarker import HandLandmarkerResult

FINGER_TIPS = [8, 12, 16, 20]
FINGER_PIPS = [6, 10, 14, 18]

THUMB_TIP = 4
THUMB_MCP = 2

# Function to add up the number of finger on both hands to get the final quantity
# This data type is an int becuase it returns the number of fingers detected
def count_fingers(gesture_result: GestureRecognizerResult) -> int:
    total_count = 0
    for landmarks, handedness in zip(
        gesture_result.hand_landmarks, gesture_result.handedness
    ):
        is_left = handedness[0].category_name == "Left"

        thumb_up = (
            landmarks[THUMB_TIP].x < landmarks[THUMB_MCP].x
            if is_left
            else landmarks[THUMB_TIP].x > landmarks[THUMB_MCP].x
        )

        finger_count = sum(
            [
                landmarks[tip].y < landmarks[pip].y
                for tip, pip in zip(FINGER_TIPS, FINGER_PIPS)
            ]
        )

        total_count += finger_count + thumb_up
    return total_count

# I chose to use a boolean data type for this function as it only has two states, either recgonized or not recognized
def recognize_victory(gesture_result: GestureRecognizerResult) -> bool:
    for gestures in gesture_result.gestures:
        for gesture in gestures:
            if gesture.category_name == "Victory":
                return True
    return False

# I chose to use a boolean data type for this function as it only has two states, either recgonized or not recognized
def recognize_thumbs_up(gesture_result: GestureRecognizerResult) -> bool:
    for gestures in gesture_result.gestures:
        for gesture in gestures:
            if gesture.category_name == "Thumb_Up":
                return True
    return False

# I chose to use a boolean data type for this function as it only has two states, either recgonized or not recognized
def recognize_thumbs_down(gesture_result: GestureRecognizerResult) -> bool:
    for gestures in gesture_result.gestures:
        for gesture in gestures:
            if gesture.category_name == "Thumb_Down":
                return True
    return False

    

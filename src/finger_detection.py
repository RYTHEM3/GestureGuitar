import cv2
import mediapipe as mp
import time
import math
from pathlib import Path

from gesture_recognition import recognize_gesture
from chord_mapping import get_chord
from audio_engine import AudioEngine


# -----------------------------------------
# PROJECT SETUP
# -----------------------------------------

ROOT = Path(__file__).resolve().parent.parent
MODEL_PATH = ROOT / "models" / "hand_landmarker.task"

BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
RunningMode = mp.tasks.vision.RunningMode

options = HandLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=str(MODEL_PATH)),
    running_mode=RunningMode.VIDEO,
    num_hands=2,
    min_hand_detection_confidence=0.5,
    min_hand_presence_confidence=0.5,
    min_tracking_confidence=0.5
)


# -----------------------------------------
# FINGER LANDMARKS
# -----------------------------------------

FINGERS = {
    "Index": (8, 6),
    "Middle": (12, 10),
    "Ring": (16, 14),
    "Little": (20, 18)
}


# -----------------------------------------
# HAND CONNECTIONS
# -----------------------------------------

CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),
    (0, 5), (5, 6), (6, 7), (7, 8),
    (5, 9), (9, 10), (10, 11), (11, 12),
    (9, 13), (13, 14), (14, 15), (15, 16),
    (13, 17), (17, 18), (18, 19), (19, 20),
    (0, 17)
]


# -----------------------------------------
# THUMB DETECTION
# -----------------------------------------

def detect_thumb(hand):

    point_a = hand[1]
    point_b = hand[2]
    point_c = hand[3]

    v1 = (
        point_a.x - point_b.x,
        point_a.y - point_b.y,
        point_a.z - point_b.z
    )

    v2 = (
        point_c.x - point_b.x,
        point_c.y - point_b.y,
        point_c.z - point_b.z
    )

    dot = sum(a * b for a, b in zip(v1, v2))

    mag1 = math.sqrt(sum(a * a for a in v1))
    mag2 = math.sqrt(sum(b * b for b in v2))

    if mag1 == 0 or mag2 == 0:
        return False

    cosine = dot / (mag1 * mag2)
    cosine = max(-1.0, min(1.0, cosine))

    angle = math.degrees(math.acos(cosine))

    return angle > 145


# -----------------------------------------
# CAMERA AND AUDIO SETUP
# -----------------------------------------

camera = cv2.VideoCapture(0)

if not camera.isOpened():
    raise RuntimeError("Cannot access webcam")

audio = AudioEngine()

print("GestureGuitar started!")
print("Show a gesture to play a chord.")
print("Remove your hands to stop audio.")
print("Press ESC to exit.")


# -----------------------------------------
# MAIN TRACKING LOOP
# -----------------------------------------

try:

    with HandLandmarker.create_from_options(options) as landmarker:

        while True:

            success, frame = camera.read()

            if not success:
                break

            frame = cv2.flip(frame, 1)

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            image = mp.Image(
                image_format=mp.ImageFormat.SRGB,
                data=rgb
            )

            timestamp = time.monotonic_ns() // 1_000_000

            result = landmarker.detect_for_video(image, timestamp)

            height, width, _ = frame.shape

            # Store the selected chord for this frame.
            selected_chord = None

            # ---------------------------------
            # PROCESS BOTH HANDS
            # ---------------------------------

            for hand_index, hand in enumerate(result.hand_landmarks):

                panel_x = 20 if hand_index == 0 else width - 230

                handedness = "Unknown"

                if result.handedness and hand_index < len(result.handedness):
                    handedness = result.handedness[hand_index][0].category_name

                # ---------------------------------
                # DRAW HAND CONNECTIONS
                # ---------------------------------

                for start, end in CONNECTIONS:

                    x1 = int(hand[start].x * width)
                    y1 = int(hand[start].y * height)

                    x2 = int(hand[end].x * width)
                    y2 = int(hand[end].y * height)

                    cv2.line(
                        frame,
                        (x1, y1),
                        (x2, y2),
                        (255, 150, 0),
                        2
                    )

                # Draw landmarks
                for landmark in hand:

                    x = int(landmark.x * width)
                    y = int(landmark.y * height)

                    cv2.circle(
                        frame,
                        (x, y),
                        5,
                        (0, 255, 0),
                        -1
                    )

                # ---------------------------------
                # HAND INFORMATION
                # ---------------------------------

                cv2.putText(
                    frame,
                    f"Hand {hand_index + 1} ({handedness})",
                    (panel_x, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.65,
                    (255, 255, 0),
                    2
                )

                # ---------------------------------
                # FINGER DETECTION
                # ---------------------------------

                thumb_up = detect_thumb(hand)

                fingers = {
                    "Thumb": thumb_up
                }

                raised_count = 0

                if thumb_up:
                    raised_count += 1

                thumb_status = "UP" if thumb_up else "DOWN"

                thumb_color = (
                    (0, 255, 0) if thumb_up else (0, 0, 255)
                )

                cv2.putText(
                    frame,
                    f"Thumb: {thumb_status}",
                    (panel_x, 80),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    thumb_color,
                    2
                )

                # Detect remaining four fingers
                for row, (finger, (tip, pip)) in enumerate(FINGERS.items()):

                    is_raised = hand[tip].y < hand[pip].y

                    fingers[finger] = is_raised

                    if is_raised:
                        raised_count += 1

                    status = "UP" if is_raised else "DOWN"

                    color = (
                        (0, 255, 0) if is_raised else (0, 0, 255)
                    )

                    cv2.putText(
                        frame,
                        f"{finger}: {status}",
                        (panel_x, 115 + row * 35),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        color,
                        2
                    )

                # ---------------------------------
                # GESTURE RECOGNITION
                # ---------------------------------

                gesture = recognize_gesture(fingers)

                cv2.putText(
                    frame,
                    f"Gesture: {gesture}",
                    (panel_x, 285),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.65,
                    (0, 255, 255),
                    2
                )

                cv2.putText(
                    frame,
                    f"Raised: {raised_count}/5",
                    (panel_x, 320),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 255, 0),
                    2
                )

                # ---------------------------------
                # CHORD MAPPING
                # ---------------------------------

                chord = get_chord(gesture)

                # Select the first valid chord detected.
                if selected_chord is None and chord is not None:
                    selected_chord = chord

            # ---------------------------------
            # AUDIO ENGINE
            # ---------------------------------

            # Same chord continues playing without restarting.
            # A different chord switches the audio.
            # No valid gesture stops the audio.

            audio.play_chord(selected_chord)

            # ---------------------------------
            # DISPLAY CURRENT CHORD
            # ---------------------------------

            if selected_chord is not None:

                display_text = f"PLAYING: {selected_chord}"
                display_color = (0, 255, 0)

            else:

                display_text = "NO CHORD - AUDIO STOPPED"
                display_color = (0, 0, 255)

            cv2.putText(
                frame,
                display_text,
                (20, height - 65),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                display_color,
                2
            )

            # ---------------------------------
            # TOTAL HAND COUNT
            # ---------------------------------

            cv2.putText(
                frame,
                f"Hands detected: {len(result.hand_landmarks)}",
                (20, height - 25),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2
            )

            cv2.imshow(
                "GestureGuitar - Virtual Guitar",
                frame
            )

            if cv2.waitKey(1) & 0xFF == 27:
                break

finally:

    # Stop audio and release resources
    audio.close()

    camera.release()
    cv2.destroyAllWindows()

    print("GestureGuitar stopped.")
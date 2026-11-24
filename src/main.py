import sys
import cv2
import mediapipe as mp
import time
import math

from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QGridLayout, QVBoxLayout, QHBoxLayout,
    QComboBox, QGroupBox
)

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap

from audio_engine import AudioEngine
from chord_mapping import get_chord
from gesture_recognition import recognize_gesture


# =========================================
# MEDIAPIPE SETUP
# =========================================

BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
RunningMode = mp.tasks.vision.RunningMode

MODEL_PATH = "models/hand_landmarker.task"

options = HandLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=MODEL_PATH),
    running_mode=RunningMode.VIDEO,
    num_hands=2,
    min_hand_detection_confidence=0.5,
    min_hand_presence_confidence=0.5,
    min_tracking_confidence=0.5
)


# =========================================
# FINGER LANDMARKS
# =========================================

FINGERS = {
    "Index": (8, 6),
    "Middle": (12, 10),
    "Ring": (16, 14),
    "Little": (20, 18)
}


# =========================================
# THUMB DETECTION
# =========================================

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


# =========================================
# MAIN APPLICATION
# =========================================

class GestureGuitar(QWidget):

    def __init__(self):

        super().__init__()

        self.setWindowTitle("GestureGuitar - Virtual Guitar")
        self.setGeometry(100, 100, 1150, 750)

        self.audio = AudioEngine()

        self.camera = cv2.VideoCapture(0)

        if not self.camera.isOpened():
            raise RuntimeError("Cannot access webcam")

        self.landmarker = HandLandmarker.create_from_options(options)

        self.current_mode = "Gesture Control"

        self.last_timestamp = 0

        self.setup_ui()

        # Camera update timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_camera)
        self.timer.start(30)

        print("GestureGuitar application started!")

    # =====================================
    # GUI DESIGN
    # =====================================

    def setup_ui(self):

        self.setStyleSheet("""
            QWidget {
                background-color: #202020;
                color: white;
                font-family: Arial;
            }

            QPushButton {
                background-color: #353535;
                color: white;
                padding: 10px;
                font-size: 14px;
                border-radius: 6px;
            }

            QPushButton:hover {
                background-color: #007acc;
            }

            QComboBox {
                background-color: #353535;
                padding: 8px;
                font-size: 14px;
            }

            QGroupBox {
                border: 1px solid gray;
                margin-top: 10px;
                padding: 10px;
                font-size: 15px;
            }
        """)

        main_layout = QVBoxLayout()

        # TITLE
        title = QLabel("GESTURE GUITAR")

        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title.setStyleSheet("""
            font-size: 30px;
            font-weight: bold;
            padding: 10px;
        """)

        main_layout.addWidget(title)

        # MODE SELECTION
        mode_layout = QHBoxLayout()

        mode_label = QLabel("CONTROL MODE:")

        self.mode_selector = QComboBox()

        self.mode_selector.addItems([
            "Gesture Control",
            "Mouse Control"
        ])

        self.mode_selector.currentTextChanged.connect(
            self.change_mode
        )

        mode_layout.addWidget(mode_label)
        mode_layout.addWidget(self.mode_selector)

        main_layout.addLayout(mode_layout)

        # STATUS
        self.status = QLabel("Show a hand gesture to play")

        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.status.setStyleSheet("""
            font-size: 22px;
            font-weight: bold;
            padding: 12px;
            color: #00ff88;
        """)

        main_layout.addWidget(self.status)

        # MAIN CONTENT
        content_layout = QHBoxLayout()

        # CAMERA PANEL
        camera_group = QGroupBox("WEBCAM")

        camera_layout = QVBoxLayout()

        self.camera_label = QLabel("Starting camera...")

        self.camera_label.setFixedSize(640, 480)

        self.camera_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        camera_layout.addWidget(self.camera_label)

        camera_group.setLayout(camera_layout)

        content_layout.addWidget(camera_group)

        # CHORD PANEL
        chord_group = QGroupBox("CHORD LIBRARY - 24 CHORDS")

        chord_layout = QGridLayout()

        major_chords = [
            "C Major", "C# Major", "D Major", "D# Major",
            "E Major", "F Major", "F# Major", "G Major",
            "G# Major", "A Major", "A# Major", "B Major"
        ]

        minor_chords = [
            "C Minor", "C# Minor", "D Minor", "D# Minor",
            "E Minor", "F Minor", "F# Minor", "G Minor",
            "G# Minor", "A Minor", "A# Minor", "B Minor"
        ]

        # MAJOR BUTTONS
        for index, chord in enumerate(major_chords):

            button = QPushButton(chord)

            button.clicked.connect(
                lambda checked=False, c=chord: self.mouse_play(c)
            )

            chord_layout.addWidget(
                button,
                index // 3,
                index % 3
            )

        # MINOR BUTTONS
        for index, chord in enumerate(minor_chords):

            button = QPushButton(chord)

            button.clicked.connect(
                lambda checked=False, c=chord: self.mouse_play(c)
            )

            chord_layout.addWidget(
                button,
                4 + index // 3,
                index % 3
            )

        chord_group.setLayout(chord_layout)

        content_layout.addWidget(chord_group)

        main_layout.addLayout(content_layout)

        # STOP BUTTON
        stop_button = QPushButton("STOP AUDIO")

        stop_button.setStyleSheet("""
            background-color: #a83232;
            font-size: 17px;
            padding: 12px;
        """)

        stop_button.clicked.connect(self.stop_audio)

        main_layout.addWidget(stop_button)

        self.setLayout(main_layout)

    # =====================================
    # CHANGE CONTROL MODE
    # =====================================

    def change_mode(self, mode):

        self.current_mode = mode

        self.audio.stop()

        if mode == "Gesture Control":

            self.status.setText(
                "GESTURE MODE - Show your hand"
            )

        else:

            self.status.setText(
                "MOUSE MODE - Select a chord"
            )

    # =====================================
    # MOUSE CHORD CONTROL
    # =====================================

    def mouse_play(self, chord):

        if self.current_mode != "Mouse Control":
            self.status.setText(
                "Switch to Mouse Control first"
            )
            return

        self.audio.play_chord(chord)

        self.status.setText(
            "NOW PLAYING: " + chord
        )

    # =====================================
    # STOP AUDIO
    # =====================================

    def stop_audio(self):

        self.audio.stop()

        self.status.setText("AUDIO STOPPED")

    # =====================================
    # CAMERA PROCESSING
    # =====================================

    def update_camera(self):

        success, frame = self.camera.read()

        if not success:
            return

        frame = cv2.flip(frame, 1)

        if self.current_mode == "Gesture Control":

            rgb = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2RGB
            )

            image = mp.Image(
                image_format=mp.ImageFormat.SRGB,
                data=rgb
            )

            timestamp = time.monotonic_ns() // 1_000_000

            timestamp = max(
                timestamp,
                self.last_timestamp + 1
            )

            self.last_timestamp = timestamp

            result = self.landmarker.detect_for_video(
                image,
                timestamp
            )

            selected_chord = None

            # PROCESS HANDS
            for hand in result.hand_landmarks:

                fingers = {
                    "Thumb": detect_thumb(hand)
                }

                for finger, (tip, pip) in FINGERS.items():

                    fingers[finger] = (
                        hand[tip].y < hand[pip].y
                    )

                gesture = recognize_gesture(fingers)

                chord = get_chord(gesture)

                if selected_chord is None and chord:

                    selected_chord = chord

                # DRAW LANDMARKS
                height, width, _ = frame.shape

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

                cv2.putText(
                    frame,
                    gesture,
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 255),
                    2
                )

            # AUDIO CONTROL
            self.audio.play_chord(selected_chord)

            if selected_chord:

                self.status.setText(
                    "GESTURE PLAYING: " + selected_chord
                )

            else:

                self.status.setText(
                    "NO GESTURE - AUDIO STOPPED"
                )

        # DISPLAY CAMERA
        rgb_frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        height, width, channels = rgb_frame.shape

        bytes_per_line = channels * width

        q_image = QImage(
            rgb_frame.data,
            width,
            height,
            bytes_per_line,
            QImage.Format.Format_RGB888
        )

        pixmap = QPixmap.fromImage(q_image)

        self.camera_label.setPixmap(
            pixmap.scaled(
                self.camera_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
        )

    # =====================================
    # APPLICATION CLEANUP
    # =====================================

    def closeEvent(self, event):

        self.timer.stop()

        self.audio.close()

        self.landmarker.close()

        self.camera.release()

        event.accept()


# =========================================
# START APPLICATION
# =========================================

app = QApplication(sys.argv)

window = GestureGuitar()

window.show()

sys.exit(app.exec())
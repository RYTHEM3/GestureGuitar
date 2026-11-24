import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton,
    QLabel, QGridLayout, QVBoxLayout
)
from PyQt6.QtCore import Qt

from audio_engine import AudioEngine


class GestureGuitarGUI(QWidget):

    def __init__(self):
        super().__init__()

        self.audio = AudioEngine()

        self.setWindowTitle("GestureGuitar - Virtual Guitar")
        self.setGeometry(300, 150, 650, 550)

        self.setStyleSheet("""
            QWidget {
                background-color: #202020;
                color: white;
            }

            QPushButton {
                background-color: #353535;
                color: white;
                padding: 15px;
                font-size: 15px;
                border-radius: 8px;
            }

            QPushButton:hover {
                background-color: #007acc;
            }
        """)

        main_layout = QVBoxLayout()

        self.title = QLabel("GESTURE GUITAR")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setStyleSheet("font-size: 28px; font-weight: bold;")

        main_layout.addWidget(self.title)

        self.status = QLabel("Select a chord to begin")
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status.setStyleSheet("font-size: 20px; padding: 15px;")

        main_layout.addWidget(self.status)

        grid = QGridLayout()

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

        for index, chord in enumerate(major_chords):

            button = QPushButton(chord)
            button.clicked.connect(
                lambda checked=False, c=chord: self.play_chord(c)
            )

            grid.addWidget(button, index // 4, index % 4)

        for index, chord in enumerate(minor_chords):

            button = QPushButton(chord)
            button.clicked.connect(
                lambda checked=False, c=chord: self.play_chord(c)
            )

            grid.addWidget(button, 3 + index // 4, index % 4)

        main_layout.addLayout(grid)

        stop_button = QPushButton("STOP AUDIO")
        stop_button.clicked.connect(self.stop_audio)

        main_layout.addWidget(stop_button)

        self.setLayout(main_layout)

    def play_chord(self, chord):

        self.audio.play_chord(chord)
        self.status.setText("NOW PLAYING: " + chord)

    def stop_audio(self):

        self.audio.stop()
        self.status.setText("AUDIO STOPPED")

    def closeEvent(self, event):

        self.audio.close()
        event.accept()


app = QApplication(sys.argv)

window = GestureGuitarGUI()
window.show()

sys.exit(app.exec())
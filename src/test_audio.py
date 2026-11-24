import time
from audio_engine import AudioEngine

audio = AudioEngine()

try:

    print("Playing C Major...")
    audio.play_chord("C Major")
    time.sleep(4)

    print("Switching to G Major...")
    audio.play_chord("G Major")
    time.sleep(4)

    print("Switching to A Minor...")
    audio.play_chord("A Minor")
    time.sleep(4)

    print("Stopping audio...")
    audio.stop()
    time.sleep(1)

finally:
    audio.close()
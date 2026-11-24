import pygame
import numpy as np


class AudioEngine:

    def __init__(self):

        pygame.mixer.init(
            frequency=44100,
            size=-16,
            channels=2,
            buffer=512
        )

        self.channel = pygame.mixer.Channel(0)
        self.current_chord = None
        self.sound_cache = {}

        self.chords = {

    # MAJOR CHORDS
    "C Major":  [261.63, 329.63, 392.00],
    "C# Major": [277.18, 349.23, 415.30],
    "D Major":  [293.66, 369.99, 440.00],
    "D# Major": [311.13, 392.00, 466.16],
    "E Major":  [329.63, 415.30, 493.88],
    "F Major":  [349.23, 440.00, 523.25],
    "F# Major": [369.99, 466.16, 554.37],
    "G Major":  [196.00, 246.94, 293.66],
    "G# Major": [415.30, 523.25, 622.25],
    "A Major":  [440.00, 554.37, 659.25],
    "A# Major": [466.16, 587.33, 698.46],
    "B Major":  [493.88, 622.25, 739.99],

    # MINOR CHORDS
    "C Minor":  [261.63, 311.13, 392.00],
    "C# Minor": [277.18, 329.63, 415.30],
    "D Minor":  [293.66, 349.23, 440.00],
    "D# Minor": [311.13, 369.99, 466.16],
    "E Minor":  [164.81, 196.00, 246.94],
    "F Minor":  [349.23, 415.30, 523.25],
    "F# Minor": [369.99, 440.00, 554.37],
    "G Minor":  [392.00, 466.16, 587.33],
    "G# Minor": [415.30, 493.88, 622.25],
    "A Minor":  [220.00, 261.63, 329.63],
    "A# Minor": [466.16, 554.37, 698.46],
    "B Minor":  [493.88, 587.33, 739.99]
}
        print("Sustained Guitar Synthesizer Ready!")

    def generate_chord(self, frequencies):

        sample_rate = 44100
        duration = 6

        t = np.arange(sample_rate * duration) / sample_rate

        audio = np.zeros(len(t))

        for frequency in frequencies:

            frequency = round(frequency * duration) / duration

            for harmonic in range(1, 7):

                amplitude = 1 / (harmonic ** 1.5)

                audio += amplitude * np.sin(
                    2 * np.pi * frequency * harmonic * t
                )

        audio /= np.max(np.abs(audio))
        audio *= 0.5

        audio = (audio * 32767).astype(np.int16)

        stereo = np.column_stack((audio, audio))

        return pygame.sndarray.make_sound(stereo)

    def play_chord(self, chord):

        if chord is None:
            self.stop()
            return

        if chord == self.current_chord:
            return

        if chord not in self.chords:
            print("Unknown chord:", chord)
            return

        if chord not in self.sound_cache:

            self.sound_cache[chord] = self.generate_chord(
                self.chords[chord]
            )

        self.channel.play(
            self.sound_cache[chord],
            loops=-1,
            fade_ms=200
        )

        self.current_chord = chord

        print("Playing:", chord)

    def stop(self):

        self.channel.fadeout(300)
        self.current_chord = None

    def close(self):

        self.channel.stop()
        pygame.mixer.quit()
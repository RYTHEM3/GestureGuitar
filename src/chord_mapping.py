# Finger order: Thumb, Index, Middle, Ring, Little
# True = Raised
# False = Folded

GESTURE_CHORD_MAP = {
    (True, True, True, True, True): "C Major",
    (False, False, False, False, True): "C# Major",
    (False, True, True, False, False): "D Major",
    (False, False, False, True, False): "D# Major",
    (False, False, True, False, False): "E Major",
    (False, True, False, True, False): "F Major",
    (False, True, True, True, False): "F# Major",
    (False, False, False, False, False): "G Major",
    (False, True, True, True, True): "G# Major",
    (True, True, False, True, False): "A Major",
    (True, False, False, False, False): "A# Major",
    (True, False, False, False, True): "B Major",

    (True, False, False, True, False): "C Minor",
    (True, False, False, True, True): "C# Minor",
    (True, False, True, False, False): "D Minor",
    (True, False, True, False, True): "D# Minor",
    (False, True, False, False, True): "E Minor",
    (True, False, True, True, False): "F Minor",
    (True, False, True, True, True): "F# Minor",
    (True, True, False, False, False): "G Minor",
    (True, True, False, False, True): "G# Minor",
    (False, True, False, False, False): "A Minor",
    (True, True, False, True, True): "A# Minor",
    (True, True, True, False, False): "B Minor"
}


def get_chord_from_fingers(fingers):

    pattern = (
        fingers["Thumb"],
        fingers["Index"],
        fingers["Middle"],
        fingers["Ring"],
        fingers["Little"]
    )

    return GESTURE_CHORD_MAP.get(pattern)


def get_all_chords():
    return GESTURE_CHORD_MAP.copy()
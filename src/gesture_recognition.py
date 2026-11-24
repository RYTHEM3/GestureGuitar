def recognize_gesture(fingers):

    thumb = fingers["Thumb"]
    index = fingers["Index"]
    middle = fingers["Middle"]
    ring = fingers["Ring"]
    little = fingers["Little"]

    if all(fingers.values()):
        return "OPEN PALM"

    if not any(fingers.values()):
        return "FIST"

    if index and middle and not thumb and not ring and not little:
        return "PEACE"

    if index and not thumb and not middle and not ring and not little:
        return "POINTING"

    # ROCK SIGN: Index + Little raised
    if index and little and not thumb and not middle and not ring:
        return "ROCK SIGN"

    return "UNKNOWN"
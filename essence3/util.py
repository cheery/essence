def clamp(low, high, value):
    if value <= low:
        return low
    if value >= high:
        return high
    return value

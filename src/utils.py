def lerp(a, b, t):
    return a + (b - a) * t

def clamp(x, mi, ma):
    return max(mi, min(x, ma))

def ease(t):
    return t * t * (3 - 2 * t)
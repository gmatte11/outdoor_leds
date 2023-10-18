from time import time as _now

def wheel(p):
    if p < 0 or p > 255:
        r = g = b = 0
    elif p < 85:
        r = int(p * 3)
        g = int(255 - p * 3)
        b = 0
    elif p < 170:
        p -= 85
        r = int(255 - p * 3)
        g = 0
        b = int(p * 3)
    else:
        p -= 170
        r = 0
        g = int(p * 3)
        b = int(255 - p * 3)
    return (r, g, b)

def split_color(c, width=3):
    if type(c) is int:
        if width == 3:
            return (c >> 16 & 0xff, c >> 8 & 0xff, c & 0xff)
        elif width == 4:
            return (c >> 24 & 0xff, c >> 16 & 0xff, c >> 8 & 0xff, c & 0xff)
        else:
            raise
    else:
        return c

def recombine(*args):
    c = args
    if len(c) == 1:
        c = c[0]

    if type(c) in (list, tuple):
        if len(c) == 4:
            return (c[0] & 0xff) << 24 | (c[1] & 0xff) << 16 | (c[2] & 0xff) << 8 | (c[3] & 0xff)
        elif len(c) == 3:
            return (c[0] & 0xff) << 16 | (c[1] & 0xff) << 8 | (c[2] & 0xff)
        else:
            raise
    else:
        return c

def clamp(val, low, high):
    return min(max(val, low), high)

def lerp(a, b, t):
    return (1 - t) * a + t * b

def mix(color1, color2):
    c1 = split_color(color1)
    c2 = split_color(color2)
    return recombine(
        min(c1[0] + c2[0], 0xff),
        min(c1[1] + c2[1], 0xff),
        min(c1[2] + c2[2], 0xff))

def interpolate(color1, color2, t: float):
    t = clamp(t, 0., 1.)
    s = 1. - t
    c1 = split_color(color1)
    c2 = split_color(color2)
    return recombine(
        int(c1[0] * s + c2[0] * t),
        int(c1[1] * s + c2[1] * t),
        int(c1[2] * s + c2[2] * t))

def fade(color1, color2, t: float):
    ease = lambda t: (t * t) / (2. * (t * t - t) + 1.)
    return interpolate(color1, color2, ease(t))

class EggClockTimer:
    def __init__(self, timeout: float = 0.):
        self.set_timeout(timeout)

    def expired(self, relaunch: bool = True):
        if self.start == 0:
            return False

        if (_now() - self.start) >= self.timeout:
           self.start = _now() if relaunch else 0
           return True

        return False

    def reset(self):
        self.start = _now() if self.timeout > 0 else 0

    def set_timeout(self, timeout: float):
        self.timeout = float(timeout)
        self.reset()

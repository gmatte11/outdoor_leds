from time import time as _now

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
    if len(args) == 1:
        return args[0]
    elif len(args) == 4:
        return (args[0] & 0xff) << 24 | (args[1] & 0xff) << 16 | (args[2] & 0xff) << 8 | (args[3] & 0xff)
    elif len(args) == 3:
        return (args[0] & 0xff) << 16 | (args[1] & 0xff) << 8 | (args[2] & 0xff)
    else:
        raise
    

def clamp(val, low, high):
    return min(max(val, low), high)

def lerp(a, b, t, ease = None):
    t = t if ease is None else ease(t)
    return (1 - t) * a + t * b

def blend(color1, color2, t: float, ease = None):
    t = clamp(t, 0., 1.)
    t = t if ease is None else ease(t)
    s = 1. - t

    c1 = split_color(color1)
    c2 = split_color(color2)
    return recombine(
        int(c1[0] * s + c2[0] * t),
        int(c1[1] * s + c2[1] * t),
        int(c1[2] * s + c2[2] * t))

def blend_max(color1, color2):
    c1 = split_color(color1)
    c2 = split_color(color2)
    return recombine(\
        max(c1[0], c2[0]),
        max(c1[1], c2[1]),
        max(c1[2], c2[2]))


def fade(color1, color2, t: float):
    ease = lambda t: (t * t) / (2. * (t * t - t) + 1.)
    return blend(color1, color2, ease(t))

class EggClockTimer:
    def __init__(self, timeout: float = 0.):
        self._time = 0.
        self._timeout = timeout

    def expired(self, relaunch: bool = False):
        if self._time >= self._timeout:
            if relaunch:
                self._time = 0.
            return True

        return False

    def expanded(self):
        return self._time

    def __call__(self, dt):
        self._time += dt

    def reset(self, timeout = None):
        self._time = 0.
        if timeout is not None:
            self._timeout = timeout

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

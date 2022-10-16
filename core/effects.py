import itertools as itt
from .utils import EggClockTimer, split_color, recombine

def train(n, repeat: int = 2, colors=lambda x: 0xff0000, off_colors = lambda x: 0, timer = None):
    if type(repeat) is not int: raise AttributeError('repeat must be an integer')
    
    class _:
        def __init__(self):
            self.cart = [1 if x < n else 0 for x in range(repeat)]

        def __call__(self, leds):
            if timer and not timer.expired():
                return

            for i in range(len(leds)):
                leds[i] = colors(i) if self.cart[i % repeat] else off_colors(i)
            self.cart = [self.cart[-1]] + self.cart[:-1]
            leds.show()
            return

    return _()

def color_train(length, gap, count, colors, timer = None):
    class _():
        def __init__(self):
            self.carts = None

        def launch(self, leds):
            size = length + gap
            self.striplen = len(leds)
            self.carts = [x * -size for x in range(count)]
            self.colors = [next(colors) for _ in range(count)]

        def reset(self):
            self.carts = None
        
        def can_transition(self):
           return not self.carts or self.carts[-1] >= self.striplen + length or self.carts[0] <= 0

        def __call__(self, leds):
            if not self.carts:
                self.launch(leds)

            if timer and not timer.expired():
                return

            leds.fill(0)
            for cart, color in zip(self.carts, self.colors):
                if cart >= 0:
                    for i in range(max(0, cart - length), min(cart, self.striplen)):
                        leds[i] = color

            for i in range(len(self.carts)):
                pos = self.carts[i] + 1
                self.carts[i] = pos 

            leds.show()

            if self.carts[-1] > self.striplen + length:
                self.launch(leds)

    return _()

def rotate(colors, stop_frames):
    class _():
        def __init__(self):
            self._c = colors
            self._t = 0

        def reset(self):
            self._t = 0

        @classmethod
        def _fill(cls, leds, colors):
            it = itt.cycle(colors)
            for i in range(len(leds)):
                leds[i] = next(it)

        def __call__(self, leds):
            if self._t <= 0 or stop_frames <= 0:
                _._fill(leds, self._c)
                self._c = self._c[1:] + [self._c[0]]
                self._t = stop_frames
            else:
                self._t = self._t - 1


    return _()


def breath(colors, speed, timer = None):
    class _():
        def __init__(self):
            self._c = next(colors)
            self._t = 0.

        def can_transition(self):
            return self._t <= speed 

        @classmethod
        def _blend(cls, t: float, color):
            ratio = (t * t) / (2. * (t * t - t) + 1.)
            c = split_color(color)
            return recombine([int(x * ratio) & 0xff for x in c])

        @classmethod
        def _to_blend_t(cls, t: float):
            return 1. - (t - 1.) if t > 1. else t

        def __call__(self, leds):
            if timer and not timer.expired():
                return

            if self._t >= 2.:
                self._t = 0.
                self._c = next(colors)

            c = _._blend(_._to_blend_t(self._t), self._c)
            self._t += speed

            leds.fill(c)
            leds.show()

    return _()
from importlib.abc import FileLoader
import itertools as itt
import random as rnd
import math
import types

from .program import ProgramRunner
from .utils import *

def color_train(length, gap, count, colors):
    _cycle = itt.cycle(colors)

    class _():
        def __init__(self):
            self.carts = None

        def launch(self, leds):
            size = length + gap
            self.striplen = len(leds)
            self.carts = [x * -size for x in range(count)]
            self.colors = [next(_cycle) for _ in range(count)]

        def reset(self, _):
            self.carts = None
        
        def can_transition(self):
           return not self.carts or self.carts[-1] >= self.striplen + length or self.carts[0] <= 0

        def __call__(self, leds, dt):
            if not self.carts:
                self.launch(leds)

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

def rotate(colors, width=1, stop_frames=1):
    class _():
        def __init__(self):
            self._c = colors
            self._t = 0

        def reset(self, _):
            self._t = 0

        @classmethod
        def _fill(cls, leds, colors):
            it = itt.cycle(colors)
            c = next(it)
            n = width
            for i in range(len(leds)):
                leds[i] = c
                n = n - 1
                if n == 0:
                    c = next(it)
                    n = width
            leds.show()

        def __call__(self, leds, dt):
            if self._t <= 0 or stop_frames <= 0:
                _._fill(leds, self._c)
                self._c = self._c[1:] + [self._c[0]]
                self._t = stop_frames
            else:
                self._t = self._t - 1


    return _()

def breath(colors, speed):
    _cycle = itt.cycle(colors)

    class _():
        def __init__(self):
            self._c = next(_cycle)
            self._t = 0.

        def can_transition(self):
            return self._t <= speed 

        def __call__(self, leds, dt):
            if self._t >= 2.:
                self._t = 0.
                self._c = next(_cycle)

            c = fade(0, self._c, self._t, 1., 0., 1.)
            self._t += speed

            leds.fill(c)
            leds.show()

    return _()

def wave(period, intensity_bounds, speed, colors):
    _colors = itt.cycle(colors)
    
    _mi, _ma = intensity_bounds
    _amplitude = _ma - _mi;
    _mod = period * 2 * math.pi

    class _:
        def __init__(self):
            self._phase = 0.0
            self._c = next(_colors)

        def reset(self, _):
            self._phase = 0.0

        def __call__(self, leds, dt):
            n = len(leds)
            for i in range(n):
                x = float(i) / float(n)
                I = _amplitude * math.sin(_mod * (x + self._phase)) + _mi
                leds[i] = interpolate(0x0, self._c, clamp(I, 0.0, 1.0))

            self._phase = self._phase + (speed * dt)

    return _();

def twinkle(background_color, twinkle_colors):
    _lifetime = 90
    _colors = itt.cycle(twinkle_colors)

    class Spark:
        def __init__(self):
            self._t = _lifetime
            self._c = next(_colors)

        def tick(self):
            ratio = (_lifetime - self._t) / _lifetime
            self._t -= 1
            return fade(background_color, self._c, ratio, .45, .1, .45)

        def done(self):
            return self._t < 0

    class _():
        def __init__(self):
            self.reset(None)

        def reset(self, _):
            self._twinkles = {}

        def __call__(self, leds, dt):
            leds.fill(background_color);

            fillrate = len(self._twinkles) / len(leds)
            if rnd.random() > 0.66 and fillrate < 0.75:
                idx = rnd.randrange(len(leds))
                while idx in self._twinkles:
                    idx = rnd.randrange(len(leds))
                
                self._twinkles[idx] = Spark()

            rem = []
            for i, twkl in self._twinkles.items():
                leds[i] = twkl.tick()
                if twkl.done():
                    rem.append(i)

            for i in rem:
                self._twinkles.pop(i)

            leds.show()

    return _()

def firework(colors, rocket_size = 5):
    _cycle = itt.cycle(colors)

    class _:
        def __init__(self):
            self._t = 0
            self._c = next(_cycle)
            pass

        def reset(self, runner: ProgramRunner):
            self._t = 0

            if runner:
                leds = runner.strip
                self._timings = types.SimpleNamespace();
                self._timings.rocket_time = len(leds) + math.ceil(rocket_size * 1.3)
                self._timings.flash_time = 5
                self._timings.delay_time = self._timings.flash_time + 2
                self._timings.decay_time = self._timings.delay_time + 15
                self._timings.total_time = self._timings.rocket_time + self._timings.decay_time

        def can_transition(self):
            return self._t == 0

        def _rocket(self, leds, t):
            # trail decay
            for i in range(len(leds)):
                rate = rnd.random()
                if (rate < .5):
                    leds[i] = interpolate(int(leds[i]), 0, rate);

            # rocket
            for i in range(rocket_size):
                idx = t - i
                if 0 <= idx < len(leds):
                    leds[idx] = self._c

        def _explosion(self, leds, t):
            ease = lambda x: 1 - (1 - x) * (1 - x)
            elastic = lambda x: 2 ** (-10 * x) * math.sin((x * 10 - .75) * (math.tau / 3)) + 1 if 0. < x < 1. else clamp(x, 0., 1.)

            flash_time = self._timings.flash_time

            if t < flash_time:
                max_width = len(leds) * .7
                width = elastic(float(t) / flash_time) * max_width

                for i in range(clamp(math.floor(width), 0, len(leds))):
                    idx = len(leds) - i - 1
                    leds[idx] = interpolate(self._c, interpolate(self._c, 0, .8), ease(float(width - idx) / width) - .5)

            elif t < self._timings.delay_time:
                pass

            else:
                for i in range(len(leds)):
                    rate = rnd.random()
                    if (rate <= .25):
                        leds[i] = interpolate(int(leds[i]), 0, rate);
            pass

        def __call__(self, leds, dt):
            self._t += 1

            rocket_time = self._timings.rocket_time

            if (self._t < rocket_time):
                self._rocket(leds, self._t)
            elif (self._t < self._timings.total_time):
                self._explosion(leds, self._t - rocket_time)
            else:
                self.reset(None)
                self._c = next(_cycle)
                leds.fill(0)
                
    return _()

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

            half = (leds.n + 1) >> 1
            leds[half] = self._c

            for i in range(1, half):
                inout = lambda t: (t if t < .5 else (1. - t)) * 2.

                width = float(half + 2) * inout(self._t * .5)
                t = lerp(1., 0., float(i) / width, lambda x: x * x * x) if i < int(width) else 0.

                color = blend(0, self._c, t)

                if half + i < leds.n:
                    leds[half + i] = color

                if i != 0 and half - i >= 0:
                    leds[half - i] = color
            
            self._t += dt

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

        def __call__(self, leds, dt):
            n = len(leds)
            for i in range(n):
                x = float(i) / float(n)
                I = _amplitude * math.sin(_mod * (x + self._phase)) + _mi
                leds[i] = blend(0, self._c, clamp(I, 0.0, 1.0))

            self._phase = self._phase + (speed * dt)

    return _();

def twinkle(background_color, twinkle_colors):
    _lifetime = 3.
    _colors = itt.cycle(twinkle_colors)

    class Spark:
        def __init__(self):
            self._t = 0.
            self._c = next(_colors)

        def tick(self, dt):
            ratio = self._t / _lifetime
            ratio = (1. - ratio) if ratio > .5 else ratio
            self._t += dt
            return fade(background_color, self._c, ratio / .5)

        def done(self):
            return self._t >= _lifetime

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
                leds[i] = twkl.tick(dt)
                if twkl.done():
                    rem.append(i)

            for i in rem:
                self._twinkles.pop(i)

    return _()

def firework_rocket(colors, rocket_size = 5):
    _cycle = itt.cycle(colors)
    _rocket_speed = 40.

    _particleLifetime = (3., 7.)
    _particleVelocity = (20., 90.)
    _particleCount = (4, 12)

    def _decay(value, threshold = .5):
        rate = rnd.random()
        if rate <= threshold:
            return lerp(value, 0., rate)
        return value

    class _rocket:
        def __init__(self, trail_size):
            self._t = 0.
            self._front = 0
            self._target = trail_size + rocket_size
            pass

        def tick(self, trail, dt):
            sz = len(trail)
            self._t += dt
            self._front = int(self._t * _rocket_speed)

            l = clamp(self._front - rocket_size, 0, sz + 1)
            h = clamp(self._front, 0, sz)

            if h > l:
                trail[l:h] = [1.] * (h - l)
            
        def done(self):
            return self._front >= self._target

    class _particle:
        def __init__(self):
            self._t = 0.
            self._lifetime = rnd.uniform(*_particleLifetime)
            self._velocity = rnd.uniform(*_particleVelocity)
            self._pos = 0.

        def tick(self, trail, dt):
            self._t += dt
            self._pos += self._velocity * dt
            self._velocity -= 0.5 * self._velocity * dt

            ease = lambda x: x * x * x

            idx = int(math.floor(self._pos))
            if 0 < idx <= len(trail):
                trail[-idx] = 1. * (1. - ease(self._t / self._lifetime))

            if idx > len(trail):
                self._t = self._lifetime
            pass

        def done(self):
            return self._t >= self._lifetime

    class _:
        def __init__(self):
            self._rocket = None
            self._particles = None
            self._trail = None

        def reset(self, runner: ProgramRunner):
            if runner:
                self._trail = [0.] * runner.strip.n

            self._rocket = _rocket(len(self._trail))
            self._particles = None
            self._c = next(_cycle)
            self._dir = 1 if rnd.randint(0, 1) == 0 else -1


        def can_transition(self):
            return self._rocket == self._explosion == None

        def __call__(self, leds, dt):
            #trail decay
            self._trail[:] = [_decay(x, .5) for x in self._trail]

            if not self._rocket.done():
                self._rocket.tick(self._trail, dt)

                if self._rocket.done():
                    self._particles = [_particle() for x in range(rnd.randint(*_particleCount))]

            if self._particles:
                fully_done = True
                for p in self._particles:
                    done = p.done()
                    fully_done = fully_done if done else False
                    if not done:
                        p.tick(self._trail, dt)

                if fully_done:
                    self.reset(None)
                    self._trail = [0.] * leds.n
                    leds.fill(0)
                    return

            it = iter(self._trail)
            for i in range(0, leds.n)[::self._dir]:
                leds[i] = blend(0, self._c, next(it))
                
    return _()

def firework_explosion(colors, max_ratio = .90):
    _particleLifetime = (2., 6.)
    _particleVelocity = (3., 15.)
    _particleCount = (4, 12)

    class _particle:
        def __init__(self, color, pos, vel):
            self._c = color
            self._t = 0.
            self._lifetime = rnd.uniform(*_particleLifetime)
            self._velocity = vel 
            self._pos = float(pos)

        _ease = lambda x: x * x * x

        def tick(self, leds, dt):
            self._pos += self._velocity * dt
            self._velocity -= 0.5 * self._velocity * dt

            idx = int(math.floor(self._pos))
            if 0 < idx < len(leds):
                fade_ratio = self._t / self._lifetime
                leds[idx] = blend_max(leds[idx], blend(self._c, 0, fade_ratio, _particle._ease))
            else:
                self._t = self._lifetime

            self._t += dt

        def done(self):
            return self._t >= self._lifetime


    class _:
        def __init__(self):
            self._particles = []
            pass

        def reset(self, runner: ProgramRunner):
            self._particles = []

        def __call__(self, leds, dt):
            strip = [0] * leds.n

            if (float(len(self._particles)) / leds.n) < max_ratio:
                if rnd.random() < .3:
                    center = rnd.randint(5, leds.n - 5)
                    count = rnd.randint(*_particleCount)

                    for i in range(count):
                        c = rnd.choice(colors)
                        vel = rnd.uniform(*_particleVelocity)
                        self._particles += [ _particle(c, center, vel), _particle(c, center, -vel) ]
                    pass

            for p in self._particles:
                p.tick(strip, dt)

            self._particles = [p for p in self._particles if not p.done()]

            leds[:] = strip[:]

    return _()



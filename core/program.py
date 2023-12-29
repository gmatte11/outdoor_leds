from abc import abstractclassmethod
import datetime as dt
from typing import Tuple, List

import core.effects as fx
from .colors import *
from .utils import EggClockTimer, blend, clamp
import itertools as itt

__all__ = ['ProgramRunner']
_now = dt.datetime.now

_is_resettable = lambda obj: callable(getattr(obj, 'reset', None))
_can_transition = lambda obj: callable(getattr(obj, 'can_transition', None))

class ProgramRunner:
    pass

class ProgramBase:
    @abstractclassmethod
    def is_scheduled(cls, when: dt.datetime) -> bool:
        return False

    def start(self, runner: ProgramRunner) -> None:
        pass

    def end(self, runner: ProgramRunner) -> None:
        pass

    def update(self, runner: ProgramRunner, dt: float) -> None:
        pass

class DefaultProgram(ProgramBase):
    @classmethod
    def is_scheduled(cls, when: dt.date) -> bool:
        return True

    def start(self, runner: ProgramRunner) -> None:
        self._fx = fx.twinkle(0x101010, itt.cycle([0xa0a0f0, 0xa0f6f6, 0xf0a0f0, 0xf0f0a0]))

    def update(self, runner: ProgramRunner, dt: float) -> None:
        self._fx(runner.strip, dt)

class FxLoopProgram(ProgramBase):
    def start(self, runner: ProgramRunner, delay=120, fade=3) -> None:
        self._gen = None
        self._fx = None
        self._nextfx = None

        effects = self._createEffects(runner)
        n = len(effects)

        if n == 1:
            self._fx = effects[0]
        elif n > 1:
            self._gen = itt.cycle(effects)
            self._fx = next(self._gen)
            self._timer = EggClockTimer(delay)
            self._transition_time = fade
            self._effect_time = delay

        if _is_resettable(self._fx):
            self._fx.reset(runner)

    def update(self, runner: ProgramRunner, dt: float) -> None:
        self._update_timer(dt)

        if self._nextfx is not None:
            self._update_transition(runner, dt)
        else:
            if self._fx:
                self._fx(runner.strip, dt)

            if self._gen and self._timer.expired():
                #if not _can_transition(self._fx) or self._fx.can_transition():
                    self._timer.reset(self._transition_time)
                    self._nextfx = next(self._gen)

    def _update_timer(self, dt):
        if self._gen:
            self._timer(dt)

    def _update_transition(self, runner, dt):
        a = StripBuffer(runner.strip.n)
        b = StripBuffer(runner.strip.n)

        self._fx(a, dt)
        self._nextfx(b, dt)

        cubic = lambda x: x * x * x
        for idx, color_a, color_b in zip(range(len(a)), a, b):
            runner.strip[idx] = blend(color_a, color_b, clamp(self._timer.expanded() / self._transition_time, 0., 1.), cubic)

        if self._timer.expired():
            self._timer.reset(self._effect_time)
            if _is_resettable(self._fx):
                self._fx.reset(runner)
            self._fx = self._nextfx
            self._nextfx = None

class Halloween(FxLoopProgram):
    @classmethod
    def is_scheduled(cls, when: dt.date):
        return dt.date(when.year, 10, 1) <= when <= dt.date(when.year, 10, 31)

    def _createEffects(self, runner: ProgramRunner):
        n = runner.strip.n
        return [
            fx.color_train(6, 6, 16, [0xbf1500, 0x4b0f6e]),
            fx.breath([0xdf1500, 0x2ccf18], .025),
            fx.wave(1.2, (0.1, 0.8), .15, [0x6611cc]),
            #fx.rotate([0x30aa00, 0xbf1500, 0x4b0f6e, 0x000000], 3, 3),
        ]

class XMas(FxLoopProgram):
    @classmethod
    def is_scheduled(cls, when: dt.date) -> bool:
        return dt.date(when.year, 12, 1) <= when <= dt.date(when.year, 12, 27)

    def _createEffects(self, runner: ProgramRunner):
        n = runner.strip.n
        return [
            fx.twinkle(0x101010, [0x8100db, 0x1e7c20, 0x0037fb, 0xb60000, 0xdf6500]),
            fx.color_train(3, 2, n - 10, rainbow(n - 10, 20)),
            #fx.breath([0xff0000, 0x00ff00], .015),
        ]


class NewYear(FxLoopProgram):
    @classmethod
    def is_scheduled(cls, when: dt.date):
        return dt.date(when.year, 12, 31) <= when <= dt.date(when.year + 1, 1, 2)

    def _createEffects(self, runner: ProgramRunner):
        return [
            fx.firework_explosion(rainbow(28), .5),
            fx.firework_rocket(rainbow(14)),
        ]

class ProgramRunner:
    def __init__(self, strip) -> None:
        self.strip = strip
        self._p = None

    def start(self, p: ProgramBase, *args, **kwargs) -> None:
        if self._p: self._p.end(self)
        self._p = p
        if self._p: self._p.start(self, *args, **kwargs)

    def update(self, dt: float) -> None:
        if self._p:
            self._p.update(self, dt)
            self.strip.show()

    def program_type(self) -> type:
        return type(self._p) if self._p else None

    @classmethod
    def check_schedule(cls, when: dt.datetime) -> type:
        prg_type = None

        night_date, next_check = cls.to_programmed_time(when)
        if night_date:
            for program in cls._special_programs:
                if program.is_scheduled(night_date):
                    prg_type = program

            if prg_type is None:
                prg_type = cls._default_program

        return (prg_type, next_check)

    @classmethod
    def to_programmed_time(cls, when: dt.datetime):
        today = when.date()

        if (when.time() >= cls._start_time):
            tomorrow = today + dt.timedelta(days=1)
            return (today, dt.datetime.combine(tomorrow, cls._end_time))
        elif (when.time() < cls._end_time):
            yesterday = today - dt.timedelta(days=1)
            return (yesterday, dt.datetime.combine(today, cls._end_time))
        else:
            return (None, dt.datetime.combine(today, cls._start_time))

    _start_time = dt.time(16, 30, 0)
    _end_time = dt.time(1, 0, 0)
    _default_program = DefaultProgram
    _special_programs = [Halloween, XMas, NewYear]

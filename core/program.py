from abc import abstractclassmethod
import datetime as dt
from typing import Tuple, List

from .effects import *
from .colors import *
from .utils import EggClockTimer
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
        self._fx = twinkle(0x101010, itt.cycle([0xa0a0f0, 0xa0f6f6, 0xf0a0f0, 0xf0f0a0]))

    def update(self, runner: ProgramRunner, dt: float) -> None:
        self._fx(runner.strip)

class FxLoopProgram(ProgramBase):
    def start(self, runner: ProgramRunner, delay=20) -> None:
        self._gen = itt.cycle(self._createEffects(runner))
        self._timer = EggClockTimer(delay)
        self._fx = next(self._gen)

    def update(self, runner: ProgramRunner, dt: float) -> None:
        can_advance = True
        if _can_transition(self._fx):
            can_advance = self._fx.can_transition()

        if can_advance and self._timer.expired():
            self._fx = next(self._gen)
            if _is_resettable(self._fx):
                self._fx.reset()

        self._fx(runner.strip)
    

class XMas(FxLoopProgram):
    @classmethod
    def is_scheduled(cls, when: dt.date) -> bool:
        return dt.date(when.year, 12, 1) <= when <= dt.date(when.year, 12, 28)

    def _createEffects(self, runner: ProgramRunner) -> None:
        n = runner.strip.n
        return (
            #color_train(3, 2, n - 10, rainbow(n - 10, 20)),
            breath(itt.cycle([0xff0000, 0x00ff00]), .025),
        )


class Halloween(FxLoopProgram):
    @classmethod
    def is_scheduled(cls, when: dt.date):
        return dt.date(when.year, 10, 1) <= when <= dt.date(when.year, 10, 31)

    def _createEffects(self, runner: ProgramRunner) -> None:
        n = runner.strip.n
        return (
            color_train(6, 6, 16, itt.cycle([0xbf1500, 0x4b0f6e])),
            breath(itt.cycle([0xdf1500]), .025),
            #rotate([0x30aa00, 0xbf1500, 0x4b0f6e, 0x000000], 3, 3),
        )


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
    _special_programs = [XMas, Halloween]

from abc import abstractclassmethod
import datetime as dt
from typing import Tuple, List

from .effects import *
from .colors import *
from .utils import EggClockTimer
import itertools as itt

__all__ = ['ProgramRunner', 'TestPrg']
_now = dt.datetime.now

_is_resettable = lambda obj: callable(getattr(obj, 'reset', None))

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
    def is_scheduled(cls, when: dt.datetime) -> bool:
        return True

class XMas(ProgramBase):
    @classmethod
    def is_scheduled(cls, when: dt.datetime) -> bool:
        return dt.date(when.year, 12, 1) <= when.date() <= dt.date(when.year, 12, 28)

    def start(self, runner: ProgramRunner, delay=20) -> None:
        n = runner.strip.n
        self._gen = itt.cycle((
            #color_train(3, 2, n - 10, rainbow(20)),
            breath(itt.cycle([0xff0000, 0x00ff00]), .025),
        ))
        self._timer = EggClockTimer(delay)
        self._fx = next(self._gen)

    def update(self, runner: ProgramRunner, dt: float) -> None:
        if self._timer.expired():
            self._fx = next(self._gen)
            if _is_resettable(self._fx):
                self._fx.reset()

        self._fx(runner.strip)

class Halloween(ProgramBase):
    @classmethod
    def is_scheduled(cls, when: dt.datetime):
        return dt.date(when.year, 10, 1) <= when.date() <= dt.date(when.year, 11, 1)

    def start(self, runner: ProgramRunner, delay=20) -> None:
        n = runner.strip.n
        self._gen = itt.cycle((
            #color_train(3, 2, n - 10, rainbow(20)),
            breath(itt.cycle([0xdf1500]), .025),
        ))
        self._timer = EggClockTimer(delay)
        self._fx = next(self._gen)

    def update(self, runner: ProgramRunner, dt: float) -> None:
        if self._timer.expired():
            self._fx = next(self._gen)
            if _is_resettable(self._fx):
                self._fx.reset()

        self._fx(runner.strip)

class TestPrg(ProgramBase):
    @classmethod
    def is_scheduled(cls, when: dt.datetime) -> bool:
        return dt.date(when.year, 12, 1) <= when.date() <= dt.date(when.year, 12, 28)

    def start(self, runner: ProgramRunner, delay=20) -> None:
        n = runner.strip.n
        self._gen = itt.cycle((
            color_train(3, 2, n - 10, rainbow(n - 10, 20)),
            breath(itt.cycle([0xff0000, 0x00ff00, 0x0000ff]), .25)
        ))
        self._timer = EggClockTimer(delay)
        self._fx = next(self._gen)

    def update(self, runner: ProgramRunner, dt: float) -> None:
        if self._timer.expired():
            self._fx = next(self._gen)
            if _is_resettable(self._fx):
                self._fx.reset()

        self._fx(runner.strip)

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
        night_begin, night_end = cls.night_time()
        if night_begin <= when.time() <= night_end:
            for program in cls.special_programs:
                if program.is_scheduled(when):
                    return program
            return cls.default_program
        return None

    @classmethod
    def night_time(cls) -> Tuple[dt.time, dt.time]:
        return (dt.time(17, 0, 0), dt.time(23, 59, 59))

    special_programs = [XMas, Halloween]
    default_program = DefaultProgram

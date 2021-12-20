from abc import abstractclassmethod
import datetime as dt
from typing import Tuple

from .effects import *
from .colors import *
from .utils import EggClockTimer
import itertools as itt

__all__ = ['ProgramRunner', 'XMas']
_now = dt.datetime.now

_is_resettable = lambda obj: callable(getattr(obj, 'reset', None))

class ProgramBase:
    pass

class ProgramRunner:
    def __init__(self, strip) -> None:
        self.strip = strip
        self._p = None
        self._keep = False

    def start(self, p: ProgramBase, keepalive=False) -> None:
        if self._p: self._p.end(self)
        self._p = p
        self._p.start(self)
        self._keep = keepalive

    def update(self) -> None:
        if self._p:
            self._p.update(self)

            if not self._keep and not self._p.is_active(_now()):
                self._p = None
                self.strip.fill(0)
                self.strip.show()


class ProgramBase:
    @abstractclassmethod
    def schedule(self) -> Tuple[dt.datetime, dt.datetime, dt.time, dt.timedelta]:
        #returns a range of dates + a range of time
        #(start_date, end_date, start_time, timerange)
        pass

    def is_active(self, datetime: dt.datetime) -> bool:
        start_date, end_date, start_time, delay = self.schedule()
        if start_date <= datetime < end_date:
            start = dt.datetime.combine(datetime.date(), start_time)
            end = start + delay
            return start <= datetime < end
        return False
    
    def start(self, runner: ProgramRunner) -> None:
        pass

    def end(self, runner: ProgramRunner) -> None:
        pass

    def update(self, runner: ProgramRunner) -> None:
        pass

class XMas(ProgramBase):
    @classmethod
    def schedule(self) -> Tuple[dt.datetime, dt.datetime, dt.time, dt.timedelta]:
        today = dt.datetime.today()
        return (
            dt.datetime(today.year, 12, 1),
            dt.datetime(today.year, 12, 28, 8),
            dt.time(16),
            dt.timedelta(hours=8)
        )

    def start(self, runner: ProgramRunner) -> None:
        n = runner.strip.n
        self._gen = itt.cycle((
            color_train(3, 2, n - 10, rainbow(20)),
            train(1, 2, lambda x: 0xff0000 if x % 2 == 0 else 0x00ff00, timer=EggClockTimer(1)),
        ))
        self._timer = EggClockTimer(20)
        self._fx = next(self._gen)

    def update(self, runner: ProgramRunner) -> None:
        if self._timer.expired():
            self._fx = next(self._gen)
            if _is_resettable(self._fx):
                self._fx.reset()

        self._fx(runner.strip)
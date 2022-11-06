import datetime as dt
from time import sleep, time

_now = dt.datetime.now

import board
import neopixel

from core import ProgramRunner
from .app_mutex import AppMutex

class App:
    def __init__(self):
        self._last_update = 0
        pass

    def __enter__(self):
        self.leds = neopixel.NeoPixel(board.D18, 30 * 5 - 1, brightness=1, auto_write=False)
        self._runner = ProgramRunner(self.leds)
        self.clear_leds()
        
        now = _now()
        print("Starting LED control at {}".format(now))
        self._update_schedule(now)

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.clear_leds()
        return (exc_type is None)

    def _update_schedule(self, when: dt.datetime):
        program_type, self._next_check = ProgramRunner.check_schedule(when)
        if program_type != self._runner.program_type():
            self.clear_leds()
            self._runner.start(program_type() if program_type is not None else None)
            self._last_update = time()
            print('It is {} ; lauching program type {}'.format(when, program_type))
        print('Next update will be at {}'.format(self._next_check))

    def run(self):
        while True:
            now = _now()
            if now > self._next_check:
                self._update_schedule(now)
            else:
                dtime = time() - self._last_update
                self._last_update = time()

                self._runner.update(dtime)

            sleep(.05)

    def clear_leds(self):
        self.leds.fill(0)
        self.leds.show()

def run():
    with AppMutex() as mutex:
        with App() as app: 
            app.run()

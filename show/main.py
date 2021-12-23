import datetime as dt
from time import sleep, time

_now = dt.datetime.now

import board
import neopixel

from core import ProgramRunner

class App(object):
    def __init__(self):
        pass

    def __enter__(self):
        self.leds = neopixel.NeoPixel(board.D18, 30 * 5, brightness=1, auto_write=False)
        self._runner = ProgramRunner(self.leds)
        self._next_check = dt.datetime.now()
        
        print("Starting LED control at {}".format(_now()))

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.clear_leds()
        return (exc_type is None)

    def run(self):
        while True:
            now = _now()
            if now > self._next_check:
                program_type = ProgramRunner.check_schedule(now)
                if self._runner.program_type() != program_type:
                    self._runner.start(program_type())
                    self._start_time = time()
                    self._last_update = time()
                    print('It is {} ; lauching program type {}'.format(now, program_type))
                    sleep(.05)
                self._next_check = now + dt.timedelta(minutes=15)

            dtime = time() - self._last_update
            self._last_update = time()

            self._runner.update(dtime)
            sleep(.05)

    def clear_leds(self):
        self.leds.fill(0)
        self.leds.show()

def run():
    with App() as app: 
        app.run()
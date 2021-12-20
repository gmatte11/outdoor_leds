from time import sleep
import board
import neopixel

from core import ProgramRunner, XMas

class App(object):
    def __init__(self):
        pass

    def __enter__(self):
        self.leds = neopixel.NeoPixel(board.D18, 30 * 5, brightness=1, auto_write=False)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.clear_leds()
        return (exc_type is None)

    def run(self):
        runner = ProgramRunner(self.leds)
        runner.start(XMas(), True)
        while True:
            runner.update()
            sleep(.05)

    def clear_leds(self):
        self.leds.fill(0)
        self.leds.show()

def run():
    with App() as app: 
        app.run()
import PySimpleGUI as sg
from PySimpleGUI.PySimpleGUI import TIMEOUT_KEY
from .mock_leds import *
from core import ProgramRunner, XMas

LED_COUNT=30

def leds(count):
    return [sg.Canvas(background_color='black', size=(20, 20), key=x) for x in range(count)]

def refresh(wn: sg.Window, strip: Strip):
    for i in range(strip.n):
        wn[i].Widget.configure(background = str(strip[i]))

def run():
    rate=200

    strip = Strip(LED_COUNT)
    runner = ProgramRunner(strip)
    runner.start(XMas(), delay = 3)

    layout = [  [sg.Text("Rate:"), sg.In(key='Rate'), sg.Button('Set', key='SetRate')], 
                leds(LED_COUNT),
                [sg.Button('Ok'), sg.Button('Quit')] ]

    wn = sg.Window("LED Visualizer", layout=layout);

    while True:
        event, values = wn.read(timeout=rate);
        if event == sg.WIN_CLOSED or event == 'Quit':
            break

        if event == 'SetRate':
            try:
                rate = int(values['Rate'])
            except:
                pass

        if event == TIMEOUT_KEY or event == 'Ok':
            refresh(wn, strip)
            runner.update()
            
    pass

import imgui

import OpenGL.GL as gl
import glfw
from imgui.integrations.glfw import GlfwRenderer

import sys
import time
import os

import itertools as itt

from vis.mock_leds import *
from vis.mock_prg import TestPrg
from core import ProgramRunner

LED_COUNT = 60
FRAMERATE = 24

def rgba_from_components(components):
    u32 = components[2] << 16 | components[1] << 8 | components[0]

    if len(components) == 4:
        u32 = u32 | components[3] << 24
    else:
        u32 = u32 | 0xff << 24

    return u32


def rgba(color):
    if type(color) is str:
        str_comps = [color[i:i+2] for i in range(0, len(color), 2)]
        components = tuple((int(c, 16) for c in str_comps))
        return rgba_from_components(components);

    if type(color) is Led:
        return rgba_from_components(color.as_tuple())

    raise 'undefined type'

colors = itt.cycle([rgba('7dac9fff'), rgba('dc7062'), rgba('66a8d4'), rgba('e5b060'), rgba('ff0000'), rgba('0000ff')])

def init_window(name, size, opts):

    if not glfw.init():
        print(glfw.get_error())
        sys.exit(1)
    
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 2)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, gl.GL_TRUE)

    w,h = size
    window = glfw.create_window(w, h, name, None, None)
    glfw.make_context_current(window)

    if not window:
        print(glfw.get_error())
        glfw.terminate()
        sys.exit(1)

    return window

def led_graph(name, leds):
        with imgui.begin_child(name, 20 * len(leds), 200, border=False, flags=imgui.WINDOW_NO_SCROLLBAR):

            dl = imgui.get_window_draw_list()
            wp = imgui.get_window_position()
            wz = imgui.get_window_size()
            st = imgui.get_style()

            pad = st.window_padding

            bw = 16.0
            bh = 50.0

            mouse_pos = imgui.get_mouse_position()
            highlighted_idx = -1

            for i in range(0, len(leds)):
                intensity = float(max(leds[i].as_tuple())) / 255.0

                x = wp.x + pad.x + float(i) * bw + i
                y = wp.y + pad.y
                h = max(intensity * bh, 10.0)

                dl.add_rect_filled(x, y, x + bw, y + h, rgba(leds[i]))

                if x < mouse_pos.x <= x + bw and y < mouse_pos.y <= y + bh:
                    highlighted_idx = i
                    dl.add_rect(x, y, x + bw, y + bh, 0x66ffffff)

            imgui.dummy(0, bh + pad.y)

            if highlighted_idx > -1:
                led = leds[highlighted_idx]
                imgui.text('selected: {}'.format(highlighted_idx + 1))
                intensity = float(max(led.as_tuple())) / 255.0 * 100.0
                imgui.text('intensity: {:.2f}'.format(intensity))
                imgui.text('color: #{:06X}'.format(int(led)))


class ComboBox(object):
    def __init__(self, name, values):
        self.selected = 0
        self._name = name
        self._values = values

    def __call__(self):
        with imgui.begin_combo(self._name, list(self._values)[self.selected]) as combo:
            if combo.opened:
                for i, item in enumerate(self._values):
                    is_selected = i == self.selected
                    if imgui.selectable(item, is_selected)[0]:
                        self.selected = i

                    if is_selected:
                        imgui.set_item_default_focus()

    def get_text(self):
        return list(self._values)[self.selected]

    def get_value(self):
        return self._values.get(self.get_text())



def run():
    window = init_window("TEST", (1200, 300), None)

    imgui.create_context()
    renderer = GlfwRenderer(window)

    strip = Strip(LED_COUNT)
    runner = ProgramRunner(strip)
    current_running_idx = -1

    effects = TestPrg.effects(runner)
    programs = TestPrg.programs(runner)

    effects.update(programs)
    combo = ComboBox('effects', effects)

    freq = glfw.get_timer_frequency()

    while not glfw.window_should_close(window):
        start_ticks = glfw.get_timer_value()

        glfw.poll_events()
        renderer.process_inputs()

        runner.update(float(FRAMERATE) / 1000.0)

        imgui.new_frame()

        imgui.set_next_window_position(0, 0)
        imgui.set_next_window_size(*imgui.get_io().display_size)

        with imgui.begin('WINDOW', flags=imgui.WINDOW_NO_TITLE_BAR | imgui.WINDOW_NO_RESIZE | imgui.WINDOW_NO_MOVE | imgui.WINDOW_MENU_BAR):

            combo()
            led_graph('##leds', strip.items())

        if current_running_idx != combo.selected:
            fx = combo.get_value()
            if type(fx) is type:
                runner.start(fx())
            else:
                runner.start(TestPrg([fx]), delay=20)
            current_running_idx = combo.selected

        gl.glClearColor(0, 0, 0, 1)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

        imgui.render()
        renderer.render(imgui.get_draw_data())
        glfw.swap_buffers(window)

        imgui.end_frame()

        frame_ticks = glfw.get_timer_value() - start_ticks
        while frame_ticks < (freq / FRAMERATE):
            time.sleep(max(float(freq / FRAMERATE - frame_ticks) / float(freq), 0))
            frame_ticks = glfw.get_timer_value() - start_ticks

    renderer.shutdown()
    glfw.terminate()
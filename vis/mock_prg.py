import core.effects as fx
import core.program as prg
import core.colors as clr
import itertools as itt

class TestPrg(prg.FxLoopProgram):

    @classmethod
    def effects(cls, runner: prg.ProgramRunner):
        n = runner.strip.n
        return {
            "breath": (fx.breath, ([0xff0000, 0x00ff00, 0x0000ff], .025)),
            "color_train": (fx.color_train, (3, 2, n - 10, clr.rainbow(n - 10, 20))),
            "firework": (fx.firework, [0xffffff]),
            "twinkle": (fx.twinkle, (0x909090, [0xffffff])),
        }

    def __init__(self, effects):
        self._effects = effects

    def _createEffects(self, runner: prg.ProgramRunner):
        return (fn(*args) for fn, args in self._effects)


import core.effects as fx
import core.program as prg
import core.colors as clr
import itertools as itt

class TestPrg(prg.FxLoopProgram):
    def _createEffects(self, runner: prg.ProgramRunner):
        n = runner.strip.n
        return (
            fx.twinkle(0x909090, itt.cycle([0xffffff])),
            fx.color_train(3, 2, n - 10, clr.rainbow(n - 10, 20)),
            fx.breath(itt.cycle([0xff0000, 0x00ff00, 0x0000ff]), .025),
        )


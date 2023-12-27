from collections.abc import MutableSequence, Sequence, Iterator
from typing import Union
from .utils import recombine

class StripBuffer(Sequence):
    Color = Union[int, tuple[int, int, int]]

    def __init__(self, size: int):
        self._n = size
        self._buf = [0] * size 

    def fill(self, color):
        for i in range(self._n):
            self._buf[i] = color

    @property
    def n(self) -> int:
        return self._n

    def __iter__(self):
        return self._buf.__iter__()

    def __getitem__(self, idx: int) -> Color:
        return self._buf[idx]

    def __setitem__(self, idx: int, val: Color) -> None:
        self._buf[idx] = val

    def __len__(self) -> int:
        return len(self._buf)

    def __contains__(self, val: Color) -> bool:
        for c in self._buf:
            if recombine(c) == recombine(val):
                return True
        return False

def _rainbow_wheel(p):
    if p < 0 or p > 255:
        r = g = b = 0
    elif p < 85:
        r = int(p * 3)
        g = int(255 - p * 3)
        b = 0
    elif p < 170:
        p -= 85
        r = int(255 - p * 3)
        g = 0
        b = int(p * 3)
    else:
        p -= 170
        r = 0
        g = int(p * 3)
        b = int(255 - p * 3)
    return (r, g, b)

class rainbow(Sequence, Iterator):
    def __init__(self, count, mod = 0): 
        self._count = count
        self._mod = mod if mod > 0 else count
        self._i = 0

    def __iter__(self):
        return self

    def __next__(self) -> tuple[int, int, int]:
        i, self._i = self._i, (self._i + 1) % self._count
        return _rainbow_wheel((i * (256 // self._mod)) & 255)

    def __getitem__(self, idx: int) -> tuple[int, int, int]:
        _rainbow_wheel((idx * (256 // self._mod)) & 255)

    def __len__(self) -> int:
        return self._count
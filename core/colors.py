from .utils import wheel

class StripBuffer:
    def __init__(self, size: int):
        self._n = size
        self._buf = [0] * size 

    def fill(self, color):
        for i in range(self._n):
            self._buf[i] = color

    @property
    def n(self) -> int:
        self._n

    def __iter__(self):
        return self._buf.__iter__()

    def __getitem__(self, idx):
        return self._buf[idx]

    def __setitem__(self, idx, val) -> None:
        self._buf[idx] = val

    def __len__(self) -> int:
        return len(self._buf)

class rainbow:
    def __init__(self, count, mod = 0): 
        self._count = count
        self._mod = mod if mod > 0 else count
        self._i = 0

    def __iter__(self): 
        return self

    def __next__(self):
        i, self._i = self._i, (self._i + 1) % self._count
        return wheel((i * (256 // self._mod)) & 255)
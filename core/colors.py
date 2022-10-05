from .utils import wheel

__all__ = ['rainbow']

class rainbow:
    def __init__(self, count, mod): 
        self._count = count
        self._mod = mod
        self._i = 0

    def __iter__(self): 
        return self

    def __next__(self):
        i, self._i = self._i, (self._i + 1) % self._count
        return wheel((i * (256 // self._mod)) & 255)
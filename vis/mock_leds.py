from core.utils import split_color

class Led:
    def __init__(self, idx):
       self.color = 0
       self.idx = idx

    def as_int(self) -> int:
        if type(self.color) is int:
            return self.color
        elif type(self.color) is tuple:
            v = 0
            n = len(self.color)
            for i in range(n):
                v = v | (self.color[i] << ((n - i - 1) * 8)) 
            return v
        else:
            raise TypeError("Unknown type")

    def as_tuple(self):
        if type(self.color) is tuple:
            return self.color
        elif type(self.color) is int:
            return split_color(self.color)

    def __eq__(self, __o: object) -> bool:
        return self.color == __o

    def __int__(self) -> int:
        return self.as_int()

    def __str__(self) -> str:
        return '#{:06X}'.format(self.as_int())

class Strip:
    def __init__(self, count, brightness: float = 1.):
        self._n = count
        self.brightness = brightness
        self._track = [Led(x) for x in range(count)]

    def show(self):
        pass

    def fill(self, color: int) -> None:
        for l in self._track:
            l.color = color
        

    def deinit(self) -> None:
        self.fill(0)

    @property
    def n(self) -> int:
        return self._n

    def __iter__(self):
        return self._track.__iter__()

    def __getitem__(self, idx) -> Led:
        return self._track[idx]

    def __setitem__(self, idx, val) -> None:
        self._track[idx].color = val

    def __len__(self) -> int:
        return len(self._track)



    
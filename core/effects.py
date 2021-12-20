def train(n, repeat: int = 2, colors=lambda x: 0xff0000, off_colors = lambda x: 0, timer = None):
    if type(repeat) is not int: raise AttributeError('repeat must be an integer')
    
    class _:
        def __init__(self):
            self.cart = [1 if x < n else 0 for x in range(repeat)]

        def __call__(self, leds):
            if timer and not timer.expired():
                return

            for i in range(len(leds)):
                leds[i] = colors(i) if self.cart[i % repeat] else off_colors(i)
            self.cart = [self.cart[-1]] + self.cart[:-1]
            leds.show()
            return

    return _()

def color_train(length, gap, count, colors, timer = None):
    class _():
        def __init__(self):
            self.carts = None

        def launch(self, leds):
            size = length + gap
            self.carts = [x * -size for x in range(count)]
            self.colors = [colors(x * (len(leds) // count)) for x in range(count)]

        def reset(self):
            self.carts = None

        def __call__(self, leds):
            if not self.carts:
                self.launch(leds)

            if timer and not timer.expired():
                return

            leds.fill(0)
            for cart, color in zip(self.carts, self.colors):
                if cart >= 0:
                    for i in range(max(0, cart - length), min(cart, len(leds))):
                        leds[i] = color

            for i in range(len(self.carts)):
                pos = self.carts[i] + 1
                self.carts[i] = pos 

            leds.show()

            if self.carts[-1] > len(leds) + length:
                self.launch(leds)


    return _()
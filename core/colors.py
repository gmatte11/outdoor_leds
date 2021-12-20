from .utils import wheel

__all__ = ['rainbow']

def rainbow(mod):
    def _(i):
        return wheel((i * (256 // mod)) & 255)
        
    return _
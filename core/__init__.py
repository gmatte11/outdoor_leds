import importlib as _imp
import pkgutil as _pkg

for mod_info in _pkg.walk_packages(__path__, __name__ + '.'):
    mod = _imp.import_module(mod_info.name)
    names = mod.__dict__.get('__all__')
    if not names:
        names = [k for k in mod.__dict__ if not k.startswith('_')]
    globals().update({k: getattr(mod, k) for k in names})
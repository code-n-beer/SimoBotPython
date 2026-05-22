__all__ = []

import pkgutil
import inspect

for loader, name, is_pkg in pkgutil.walk_packages(__path__):
    try:
        module = loader.find_module(name).load_module(name)
    except Exception as e:
        print("Skipping feature module {}: {}".format(name, e))
        continue

    for name, value in inspect.getmembers(module):
        if name.endswith('Feature'):
            globals()[name] = value
            __all__.append(name)

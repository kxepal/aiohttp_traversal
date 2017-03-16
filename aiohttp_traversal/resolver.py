import inspect
from functools import wraps


def resolve(name, module=None):
    name = name.split('.')
    if not name[0]:
        if module is None:
            raise ValueError("relative name without base module")
        module = module.split('.')
        name.pop(0)
        while not name[0]:
            module.pop()
            name.pop(0)
        name = module + name

    used = name.pop(0)
    found = __import__(used)
    for n in name:
        used += '.' + n
        try:
            found = getattr(found, n)
        except AttributeError:
            __import__(used)
            found = getattr(found, n)

    return found


def resolver(*for_resolve, attr_package='__package_for_resolve_deco__'):
    """ Resolve dotted names in function arguments

    Usage:

        >>> @resolver('obj')
        >>> def func(param, obj):
        >>>     assert isinstance(param, str)
        >>>     assert not isinstance(obj, str)
        >>>
        >>> func('os.path', 'sys.exit')
    """
    def decorator(func):
        spec = inspect.getargspec(func).args
        if set(for_resolve) - set(spec):
            raise ValueError('bad arguments')

        @wraps(func)
        def wrapper(*args, **kwargs):
            args = list(args)

            if args and attr_package:
                package = getattr(args[0], attr_package, None)
            else:
                package = None

            for item in for_resolve:
                n = spec.index(item)
                if n >= len(args):
                    continue

                if n is not None and isinstance(args[n], str):
                    args[n] = resolve(args[n], package)

            for kw, value in kwargs.copy().items():
                if kw in for_resolve and isinstance(value, str):
                    kwargs[kw] = resolve(value, package)

            return func(*args, **kwargs)

        return wrapper

    return decorator

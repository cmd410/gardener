from functools import wraps
from types import SimpleNamespace

from gevent import spawn


def ignore_exc(*exc, msg=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = None
            try:
                result = func(*args, **kwargs)
            except exc as error:
                if msg is not None:
                    print(msg)
            return result
        return wrapper
    return decorator


def greenlet(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return spawn(func, *args, **kwargs)
    return wrapper


def get_from(ns: SimpleNamespace, name):
    if name in ns.__dict__:
        return getattr(ns, name)
    return None

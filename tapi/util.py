from functools import wraps
from contextlib import suppress
from types import SimpleNamespace

from gevent import spawn


def ignore_exc(*exc):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with suppress(*exc):
                result = func(*args, **kwargs)
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

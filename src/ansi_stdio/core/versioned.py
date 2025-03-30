import threading
from functools import wraps


class Versioned:
    """
    Inherit this class to store a version number on each change.
    """

    def __init__(self):
        self._version = 0
        self._lock = threading.RLock()

    def mark_dirty(self):
        with self._lock:
            self._version += 1

    @property
    def version(self):
        return self._version


def changes(method):
    """
    Decorate methods with this if they make changes to the object
    """

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        with self._lock:
            result = method(self, *args, **kwargs)
            self._version += 1
        return result

    return wrapper


def waits(method):
    """
    Decorate methods with this if they need to wait for changes to m
    """

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        with self._lock:
            result = method(self, *args, **kwargs)
        return result

    return wrapper

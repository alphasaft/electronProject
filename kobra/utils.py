import sys
from typing import *


T = TypeVar("T")
OutI = TypeVar("out I", covariant=True)


def inheritFromBoth(primary, secondary):
    class _Subclass(primary, secondary):
        def __init__(self, *args, **kwargs):
            primary.__init__(self, *args, **kwargs)
            secondary.__init__(self)

    _Subclass.__name__ = primary.__name__
    _Subclass.__module__ = primary.__module__
    return _Subclass


def warn(message, *formatArguments):
    print("Warning : " + message % formatArguments, file=sys.stderr)


def checkNotEmpty(__l: Sized, errorMessage: str):
    if len(__l) == 0:
        raise ValueError(errorMessage)
    return __l


def checkSize(__l: Sized, expected: int, errorMessage: str):
    if len(__l) != expected:
        raise ValueError(errorMessage)
    return __l


def flatten(iterable: Iterable[Iterable[T]]) -> Iterable[T]:
    result = []
    for sub in iterable:
        result += sub
    return result


def getattrOrIdentity(self, attr):
    return getattr(self, attr, lambda: self)

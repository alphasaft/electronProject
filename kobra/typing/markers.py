from typing import Any

from ..annotations import Annotation, Decorator
from ..__settings__ import PROJECT_TYPE_CHECKER


class Stub(Annotation):
    """
    Annotates this method as a stub method, i.e. a method whose implementation belong to a super class, but whose
    type hints are declared there.
    """
    def __init__(self, function):
        super().__init__(function)


def CheckMethodTypes(function):
    def wrapper(self, *args, **kwargs):
        ret = function(self, *args, **kwargs)
        
        PROJECT_TYPE_CHECKER.checkFunctionCallArguments(
            {"self": type(self), **function.__annotations__},
            {tv: t for tv, t in zip(self.__parameters__, self.__args__)},
            self,
            *args,
            **kwargs
            )
        return ret

    wrapper.__name__ = function.__name__
    wrapper.__annotations__ = function.__annotations__
    wrapper.__doc__ = function.__doc__
    return wrapper


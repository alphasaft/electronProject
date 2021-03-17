from typing import *


I = TypeVar("I")
OutI = TypeVar("I", covariant=True)
InI = TypeVar("I", contravariant=True)
T = TypeVar("T")
InK = TypeVar("K", contravariant=True)
OutV = TypeVar("V", covariant=True)
P = TypeVar("P", contravariant=True)
R = TypeVar("R", covariant=True)

Predicate = Callable[[P], bool]
Function = Callable[..., R]

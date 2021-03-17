"""
Package that allows you to statically type your programs.
Functions typing is done through the built-in typing syntax, while variables are typed through flags (see module `flags`
for more info).
"""

from .annotations import *
from .contracts import *
from .inheritance import *
from kobra.typing.type_aliases import *
from kobra.typing._core import *

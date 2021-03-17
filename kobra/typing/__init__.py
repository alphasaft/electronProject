"""
--- Why not use mypy ? ---
 - First, mypy is at compile time and takes lots of time.
 - It checks everything including things you actually don't need to check
 - Weird metaclass tricks (but you're absolutely sure it works) trigger unexpected errors
 - It seems that mypy needs a full knowledge of every type, while you mostly want to check function in- and outputs

--- Some ideas ---
 - Disable and enable type checking easily though annotations (yes but not now because it shines useless)
 - Warnings in order to point out type inconsistencies that seem dangerous (to do !!)
"""

from ._core import *
from .checks import *

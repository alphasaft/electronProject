import re
import traceback

from .utils import inheritFromBoth
from .annotations import Decorator


class _PackageInternal:
    def __init__(self, internalCalls):
        self._package = self.__getSurroundingPackage(internalCalls+1)
        self._subpackages = re.compile(self._package + "/.+")

    @staticmethod
    def __getSurroundingPackage(internalCalls):
        return "/".join(traceback.extract_stack()[-(internalCalls+2)].filename.split("/")[:-1])

    def _checkPackage(self, internalCalls, errorMsg):
        package = self.__getSurroundingPackage(internalCalls+1)
        if not (package == self._package or self._subpackages.match(package)):
            raise RuntimeError(errorMsg % self._package)


class _PackageInternalClass(_PackageInternal):
    def __init__(self):
        self._checkPackage(2, f"Class {type(self).__name__} is internal in package %s and cannot be used from the outside")

    def __init_subclass__(cls, **kwargs):
        _PackageInternal.__init__(cls, internalCalls=4)


class _PackageInternalFunction(Decorator, _PackageInternal):
    def __init__(self, functionOrClass):
        _PackageInternal.__init__(self, 1)
        Decorator.__init__(self, functionOrClass)

    def __call__(self, *args, **kwargs):
        self._checkPackage(1, f"Function {self._function.__name__} was declared internal in package %s and cannot be used from the outside")
        return self._function(*args, **kwargs)


def PackageInternal(functionOrClass):
    """ Marks the declaration as internal, and raise a RuntimeException whenever called outside of their initial package """
    if isinstance(functionOrClass, type):
        return inheritFromBoth(functionOrClass, _PackageInternalClass)
    elif hasattr(functionOrClass, "__call__"):
        return _PackageInternalFunction(functionOrClass)
    else:
        raise TypeError("Can only decorate classes or functions")

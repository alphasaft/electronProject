import inspect

from .annotations import *
from .access import PackageInternal
from .utils import inheritFromBoth


def Final(functionOrClass):
    """ Indicates that this method or class is final and can't be overridden/subclassed """

    if isinstance(functionOrClass, type):
        def _initSubclassDummy():
            raise RuntimeError(f"Class {functionOrClass.__name__} is final and cannot be subclassed")

        functionOrClass.__init_subclass__ = _initSubclassDummy

    functionOrClass.__final__ = True
    return functionOrClass


def NotInstantiable(cls):
    """ Raises a RuntimeError if someone tries to init an instance of the marked class """

    def _initDummy(self, *args, **kwargs):
        raise RuntimeError(f"Class '{self.__class__.__name__}' can't be instantiated")

    cls.__init__ = _initDummy
    return cls


class _Singleton:
    """ Indicates that this class is a singleton. Singleton contract is that __init__ takes no additional parameter.
    In return, only one instance of the class is created, then returned every time a new instance should be created.
    This implies that given class A(Singleton): ..., A() is A(), and that instances variables are shared between
    all the instances """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if args or kwargs: raise TypeError("No args or kwargs are expected to initialize a singleton")
        if not cls._instance:
            cls._instance = object.__new__(cls)
        return cls._instance


def Singleton(cls):
    return Final(inheritFromBoth(cls, _Singleton))


class _Sealed:
    """ Indicates that this in class is sealed, and can't be inherited by classes that lie outside of the declaring
    module and of the extraPermittedFiles """

    __sealed__ = True
    _permittedFiles = ()

    def __init_subclass__(cls, **kwargs):
        def _initSubclassCheck():
            if cls.__module__ not in cls._permittedFiles:
                raise PermissionError(
                    "Class %s is sealed and can't be inherited from non-permitted classes" % cls.__name__)

        cls.__init_subclass__ = _initSubclassCheck
        return super(cls).__init_subclass__()


def Sealed(cls):
    return inheritFromBoth(cls, _Sealed)


class Override(CustomisableDecorator, OnlyOnce, Annotation, abc.ABC):
    """Declares the method as overriding that of superClass. Raises if the method doesn't yet exist in that object,
    if it doesn't owner the *exact* same signature and checkSignature isn't disabled, or if it was declared final using
    `@final`"""

    @staticmethod
    def _isFinal(method):
        return getattr(method, "__final__", False)

    @staticmethod
    def _searchInMro(cls, method):
        for superClass in cls.mro():
            methodImpl = getattr(superClass, method, None)
            if hasattr(methodImpl, "__call__"):
                return superClass, methodImpl

        raise NameError("'%s' overrides nothing" % method)

    @staticmethod
    def _canOverride(overrider, overridden):
        overriderSignature = inspect.signature(overrider)
        overriddenSignature = inspect.signature(overridden)

        if len(overriderSignature.parameters) != len(overriddenSignature.parameters):
            return False

        for new, old in zip(overriderSignature.parameters.values(),
                            overriddenSignature.parameters.values()):
            if not (new.name == old.name and
                    (new.kind == old.kind or old.kind in (0, 3) and new.kind == 1) and
                    new.annotation == old.annotation and
                    new.default == old.default):
                return False

        return True

    def __init_decorator__(self, function, superClass=object, checkSignature=True):
        CustomisableDecorator.__init_decorator__(self, function)
        implementer, overridden = self._searchInMro(superClass, function.__name__)

        if self._isFinal(overridden):
            raise PermissionError("Method %s is final in class %s and cannot be overridden" %
                                  (overridden.__name__, implementer.__name__))

        if checkSignature and not self._canOverride(function, overridden):
            raise TypeError("Function %s doesn't conform to the overridden signature %s" % (
                function.__name__, inspect.signature(overridden)))

        self.__overrides__ = implementer


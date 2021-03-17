import abc


class Decorator(abc.ABC):
    """ Indicates that this class is a decorator. __init__ mocks all attributes of the function by copying them into
    the Decorator, except for the methods. If it has no side effect, use `@Annotation` instead """

    __function_attributes = set(dir(lambda: None)) - {"__class__", "__dict__"}

    def _alignAttributesWithFunction(self, function):
        for attribute in dir(function):
            if attribute in self.__function_attributes and not hasattr(getattr(function, attribute), "__call__"):
                setattr(self, attribute, getattr(function, attribute))

    def _setDefaultAttributes(self, **attributes):
        for name, attr in attributes.items():
            if not hasattr(self, name):
                setattr(self, name, attributes)

    def __init__(self, function):
        if not hasattr(function, "__call__"):
            raise TypeError("Expected a function or a callable, got %s" % function)

        self._function = function
        self._alignAttributesWithFunction(function)

    @abc.abstractmethod
    def __call__(self, *args, **kwargs):
        ...


class Annotation(Decorator, abc.ABC):
    """ Indicates that this decorator does not perform any check whenever called using __call__ """
    def __call__(self, *args, **kwargs):
        return self._function(*args, **kwargs)


class CustomisableDecorator(Decorator, abc.ABC):
    """ Indicates that this class is a customisable decorator (i.e a decorator that takes arguments).
    Instead of overriding __init__, implement __init_decorator__ in order to initialize the decorator.
    Don't forget to add the call to CustomisableDecorator.__init_decorator__ in that implementation. """

    def __new__(cls, *args, **kwargs):
        class _SemiInitializedDecorator:
            def __init__(self, dargs, dkwargs):
                self._dargs = dargs
                self._dkwargs = dkwargs

            def __call__(self, function):
                new = object.__new__(cls)
                new.__init_decorator__(function, *self._dargs, **self._dkwargs)
                return new

        return _SemiInitializedDecorator(args, kwargs)

    def __init_decorator__(self, function, *args, **kwargs):
        Decorator.__init__(self, function)

    def __init__(self, *args, **kwargs):
        """Real signature unknown"""
        # Does nothing on purpose to fool the IDEs about the __init__ signature
        pass


class OnlyOnce(Decorator, abc.ABC):
    """ Indicates that this decorator can only be applied once per function/class """

    def __init__(self, function):
        Decorator.__init__(self, function)
        self._checkApplyIsLegalOn(function)

    def _checkApplyIsLegalOn(self, obj):
            decoratorFullName = f"{type(self).__module__}.{type(self).__name__}"
            if not hasattr(obj, "__decorators__"): obj.__decorators__ = []
            obj.__decorators__ = obj.__decorators__.copy()
            if decoratorFullName in obj.__decorators__: raise RuntimeError(
                "The decorator '%s' is meant to be used only once per object" % decoratorFullName)
            obj.__decorators__.append(decoratorFullName)


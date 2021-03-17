from kobra.utils import checkSize


class WrapperMeta(type):
    def __new__(mcs, name, bases, namespace, wrapped=None):
        cls = type.__new__(mcs, name, bases, namespace)

        if wrapped:
            for attribute in dir(wrapped):
                if not hasattr(cls, attribute):
                    setattr(cls, attribute, getattr(wrapped, attribute))

        return cls

    def fromWrapped(cls, obj):
        self = cls.__from_wrapped__(obj)
        self.__wrapped__ = obj
        return self

    def __from_wrapped__(cls, obj): ...
    

def renderType(_type):
    if type(_type).__repr__ is not type.__repr__:
        return repr(_type)
    else:
        return _type.__name__


def getUnParametrized(_type):
    while getattr(_type, "__origin__", None):
        _type = _type.__origin__
    return _type
    

def isParametrised(_type):
    return getattr(_type, "__parameters__", None) is not None


def genericTypeParametersOf(_type):
    return getattr(_type, "__parameters__", ())


def getTypeArgumentsOf(obj, forType, default):
    genericTypeParametersCount = len(genericTypeParametersOf(forType))

    if hasattr(obj, "__get_type_arguments_for__"):
        typeArguments = getattr(obj, "__get_type_arguments_for__")(forType)

        if typeArguments is NotImplemented:
            return default

        if isinstance(typeArguments, type):
            typeArguments = (typeArguments,)

        return checkSize(typeArguments, genericTypeParametersCount,
                         "When calling %s.__get_type_arguments_for__(%s) : expected %s type arguments, got %s" % (
                             obj,
                             renderType(forType),
                             genericTypeParametersCount,
                             len(typeArguments)))
    else:
        return default


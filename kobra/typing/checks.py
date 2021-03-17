from abc import ABC, abstractmethod
from typing import *

from ._special import KAny
from .utils import *
from ..inheritance import Singleton


class TypeChecker(ABC):
    @abstractmethod
    def checkType(self, value: Any, _type: type): ...
    @abstractmethod
    def checkCast(self, _type, castType, *, value=None): ...


@Singleton
class DefaultTypeChecker(TypeChecker):
    @staticmethod
    def _getUnParametrized(_type):
        while getattr(_type, "__origin__", None):
            _type = _type.__origin__

        return _type

    @staticmethod
    def _isParametrised(_type):
        return getattr(_type, "__parameters__", None) is not None

    @staticmethod
    def _genericTypeParametersOf(_type):
        return getattr(_type, "__parameters__", ())

    def checkType(self, value: Any, _type: Any):
        self.checkCast(type(value), _type, value=value)

    def checkCast(self, _type, castType, *, value=None):
        typeOrigin = getUnParametrized(_type)
        castTypeOrigin = getUnParametrized(castType)

        if not type.__subclasscheck__(castTypeOrigin, typeOrigin):
            raise TypeError("Expected %s, got %s" % (renderType(castType), renderType(_type)))

        if isParametrised(_type) and isParametrised(castType):
            typeParameters = _type.__parameters__
            typeArguments = getTypeArgumentsOf(value, forType=_type, default=_type.__args__)
            castTypeArguments = castType.__args__

            zipped = zip(typeParameters, typeArguments, castTypeArguments)

            for typeParameter, originalTypeArg, castTypeArg in zipped:
                if KAny in (originalTypeArg, castTypeArg):
                    pass

                elif typeParameter.__covariant__:
                    if not issubclass(originalTypeArg, castTypeArg):
                        raise TypeError("Can't cast %s into %s : For type parameter %s : %s isn't a superclass of %s"
                                        % tuple(renderType(t) for t in (_type, castType, typeParameter, castTypeArg, originalTypeArg)))

                elif typeParameter.__contravariant__:
                    if not issubclass(castTypeArg, originalTypeArg):
                        raise TypeError("Can't cast %s into %s : For type parameter %s : %s isn't a subclass of %s"
                                        % tuple(renderType(t) for t in (_type, castType, typeParameter, castTypeArg, originalTypeArg)))
                else:
                    if not originalTypeArg is castTypeArg:
                        raise TypeError("Can't cast %s into %s : For type parameter %s : expected %s, got %s" % tuple(
                            renderType(t) for t in (_type, castType, typeParameter, originalTypeArg, castTypeArg)))

    def handleTypeVars(self, annnotations, typeVars):
        ...
    
    def checkFunctionCallArguments(
            self,
            annotations: Dict[str, Any],
            typeVars: Dict[object, type],
            *args,
            **kwargs):

        toDeduce = {}
        positionalAnnotations = [*annotations.values()]

        for i, positionalArg in enumerate(args):
            annotation = positionalAnnotations[i]

            if isinstance(annotation, TypeVar):
                if annotation in typeVars:
                    annotations[i] = typeVars[annotation]
                else:
                    if annotation in toDeduce:
                        toDeduce[annotation].append(positionalArg)
                    else:
                        toDeduce[annotation] = [positionalArg]

        for name, keywordArg in kwargs.items():

            if isinstance(annotation):
                if isinstance(annotation, TypeVar):
                    if annotation in typeVars:
                        pass


class NoChecks(TypeChecker):
    def checkType(self, value: Any, _type: type):
        pass

    def checkCast(self, _type, castType, *, value=None):
        pass

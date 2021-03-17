from typing import Callable, Any, Generic
from inspect import signature

from .typing.type_aliases import Predicate, T, Function
from .annotations import Annotation, OnlyOnce, CustomisableDecorator


class Pure(OnlyOnce, Annotation):
    """ Indicates that the function is pure (has no side effect) """

    def __init__(self, function: Callable[..., Any]):
        OnlyOnce.__init__(self, function)
        self.__pure__ = True


class Constraint(CustomisableDecorator, Generic[T]):
    """ Sets a specification on the given parameter. If not respected, the decorator will raise a RuntimeException. """

    @staticmethod
    def _getParamNo(param, functionSignature):
        for paramNo, paramName in enumerate(functionSignature.parameters.keys()):
            if paramName == param:
                return paramNo

    @staticmethod
    def _elaborateConstraint(constraintObject):
        objType = type(constraintObject)
        if objType is type(lambda: None): return constraintObject
        elif objType is range or objType is tuple: return lambda x: x in constraintObject
        else: return lambda x: x == constraintObject

    def _isConstraintFilled(self, args, kwargs):
        filled = True
        if self._paramName in kwargs:
            if not self._constraint(kwargs[self._paramName]):
                filled = False
        else:
            if not self._constraint(args[self._paramNo]):
                filled = False

        return filled

    def __call__(self, *args, **kwargs):
        if not self._isConstraintFilled(args, kwargs):
            raise ValueError("Constraint posed on parameter %s wasn't filled" % self._paramName)

        return self._function(*args, **kwargs)

    def __init_decorator__(self, function: Function, param: str, constraint: Any):
        CustomisableDecorator.__init_decorator__(self, function)
        self._paramName = param
        self._paramNo = self._getParamNo(param, signature(function))
        self._constraint = self._elaborateConstraint(constraint)


def HasAttr(attr: str) -> Predicate[Any]: return lambda x: hasattr(x, attr)
def AttributeIs(attr: str, expected: Any) -> Predicate[Any]: return lambda x: getattr(x, attr) == expected
def MethodReturns(method: str, *args, expected: Any) -> Predicate[Any]: return lambda x: getattr(x, method)(*args) == expected
def CallReturns(function: Callable[[T], Any], expected: Any) -> Predicate[T]: return lambda x: function(x) == expected
def All(*constraints: Predicate[T]) -> Predicate[T]: return lambda x: all(c(x) for c in constraints)

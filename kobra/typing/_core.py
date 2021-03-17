import inspect
from typing import TypeVar, Type, ClassVar

from .markers import Stub, CheckMethodTypes
from ..__settings__ import PROJECT_TYPE_CHECKER
from ..utils import flatten
from .utils import WrapperMeta, renderType, getUnParametrized, isParametrised
from ..typing.checks import TypeChecker
from ._special import KAny


# ----------------------
# TODO : Ajouter Tim en ami !!!
# ----------------------

# TODO : Rewrite docs
# TODO : Remove typing support to write it cleaner when everything is ready


T = TypeVar("T")


class KWrapperMeta(WrapperMeta):
	def __new__(mcs,
				name,
				bases,
				namespace,
				origin=None,
				typeArguments=None,
				wrapped=None,
				nullable=False,
				**type_parameters):
		
		fullBases = bases if not wrapped else bases + (wrapped,)
		namespace = mcs._replaceStubsWithImplementation(fullBases, namespace)
		
		cls = super().__new__(mcs, name, fullBases, namespace, wrapped=wrapped)
		
		cls.__wrapped_type__ = getattr(origin, "__wrapped__", wrapped)
		cls.__named_parameters__ = type_parameters or getattr(origin, "__named_parameters__", {})
		cls.__nullable__ = nullable or getattr(origin, "__nullable__", False)
		
		cls.__parameters__ = [*cls.__named_parameters__.values()]
		cls.__origin__ = origin
		cls.__args__ = []
		cls.__typed__ = True
		
		for p, a in zip(cls.__named_parameters__.keys(), typeArguments or [KAny] * len(cls.__parameters__)):
			setattr(cls, f"__{p}__", a)
			cls.__args__.append(a)

		cls.__new__ = mcs._newDummy(cls.__new__)
		return cls
	
	@staticmethod
	def _newDummy(function):
		def _newWrapper(cls, *args, _fromCore=False, **kwargs):
			if not _fromCore:
				raise RuntimeError(f"{cls} isn't meant to be instatiated that way. Try the typing syntax {cls} instead")
			try:
				return function(cls, *args, _fromCore=_fromCore, **kwargs)
			except TypeError as e:
				if str(e).endswith("got an unexpected keyword argument '_fromCore'"):
					return function(cls, *args, **kwargs)
				raise
		return _newWrapper

	@staticmethod
	def _searchMethodImplInMro(bases, methodName):
		for supertype in flatten(cls.__mro__ for cls in bases):
			mcsMembers = [m[1] for m in inspect.getmembers(type(supertype))]
			for name, attr in inspect.getmembers(supertype):
				if attr not in mcsMembers and hasattr(attr, "__call__") and name == methodName and not isinstance(attr, Stub):
					return attr

		raise NameError("Could not find implementation for stub method %s" % methodName)
	
	@staticmethod
	def _checkSignatureIsComplete(method, annotations):
		...

	@classmethod
	def _replaceStubsWithImplementation(mcs, bases, namespace):
		def withStubAnnotations(function, annotations):
			def wrapper(self, *args, **kwargs):
				return function(self, *args, **kwargs)
			wrapper.__name__ = function.__name__
			wrapper.__annotations__ = annotations
			return CheckMethodTypes(wrapper)

		for name, attribute in namespace.items():
			if isinstance(attribute, Stub):
				mcs._checkSignatureIsComplete(attribute, inspect.signature(attribute))
				namespace[name] = withStubAnnotations(mcs._searchMethodImplInMro(bases, name), attribute.__annotations__.copy())

		return namespace

	def __invert__(cls: T) -> T:
		return type(cls).__new__(
			type(cls),
			cls.__name__,
			(cls,),
			cls.__dict__.copy(),
			origin=cls,
			typeArguments=cls.__args__,
			nullable=True
		)

	def __getitem__(cls: T, typeArguments) -> T:
		if not isinstance(typeArguments, tuple):
			typeArguments = (typeArguments,)

		if any(t is KAny for t in typeArguments):
			raise TypeError("Can't specify 'KAny' as a type parameter. Use either the untyped class, or another type")

		if len(typeArguments) != len(cls.__parameters__):
			raise ValueError("An improper number of type arguments was passed to %s (expected %s)" % (
			cls.__name__, len(cls.__parameters__)))

		return type(cls).__new__(
			type(cls),
			cls.__name__,
			(cls,),
			cls.__dict__.copy(),
			origin=cls,
			typeArguments=typeArguments
		)

	def __subclasscheck__(cls, subclass):
		if subclass is KAny:
			return True
		
		if not type.__subclasscheck__(KWrapper, subclass):
			if cls.__wrapped_type__ and issubclass(subclass, cls.__wrapped_type__):
				return True
			return type.__subclasscheck__(cls, subclass)

		if not isParametrised(cls) and not isParametrised(subclass):
			return type.__subclasscheck__(cls, subclass)

		try:
			PROJECT_TYPE_CHECKER.checkCast(subclass, cls)
		except TypeError:
			return False
		else:
			return True

	def __instancecheck__(cls, instance):
		try:
			cls& instance
		except TypeError:
			return False
		else:
			return True
	
	def _handleNone(cls):
		if not cls.__nullable__:
			raise TypeError("Can't cast nullable type into non-null type %s" % cls)
		return None
		
	def __and__(cls, obj) -> T:
		if obj is None:
			return type(cls)._handleNone(cls)
		
		if type.__subclasscheck__(type(obj), KWrapper):
			raise TypeError(f"{obj} was already statically typed as {renderType(type(obj))}. Use the cast syntax K[...] | x instead")
		
		return cls(obj, _fromCore=True)

	def __or__(cls: Type[T], obj) -> T:
		if issubclass(type(obj), KWrapper):
			obj = obj.untyped()
		return cls& obj

	def __repr__(cls):
		isParametrised = cls.__args__ and any(t is not KAny for t in cls.__args__)
		return cls.__name__ + \
			   ("[" + ", ".join(renderType(a) for a in cls.__args__) + "]" if isParametrised else "") + \
			   ("?" if cls.__nullable__ else "")
	

	def check(cls, obj):
		PROJECT_TYPE_CHECKER.checkType(obj, cls)
		return obj

	def __from_wrapped__(cls, obj): return cls


class KWrapper(metaclass=KWrapperMeta):
	@classmethod
	def __from_wrapped__(cls, unwrapped): ...
	def __new__(cls, *args, checked=True): ...
	def untyped(self): ...
	def __get_type_arguments_for__(self, _type): return NotImplemented
	def __and__(self, other):
		return type(self) & other


class KMeta(type):
	_type_checker: ClassVar[TypeChecker] = PROJECT_TYPE_CHECKER

	def __new__(mcs, name, bases, namespace):
		cls = type.__new__(mcs, name, bases, namespace)
		return cls

	def __getitem__(cls, _type):
		if not isinstance(_type, type):
			raise ValueError("K[...] must be parametrised with only one type argument")

		class Wrapper(KWrapper, wrapped=_type):
			__wrapped__ = None

			def __new__(cls, checked=False):
				return object.__new__(cls)

			@classmethod
			def __from_wrapped__(cls, obj):
				PROJECT_TYPE_CHECKER.checkType(obj, _type)
				self = Wrapper.__new__(cls, checked=False)

				for attribute in dir(_type):
					if not hasattr(self, attribute):
						setattr(self, attribute, getattr(obj, attribute))

				self.__wrapped__ = obj
				return self

			def untyped(self):
				return self.__wrapped__

			def __get_type_arguments_for__(self, aType):
				if aType is _type:
					return self.__args__
				return NotImplemented

		Wrapper.__name__ = "K[" + _type.__name__ + "]"
		return Wrapper


class K(metaclass=KMeta):
	pass

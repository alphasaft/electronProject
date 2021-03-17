class _KAnyMeta(type):
	def __and__(cls, other):
		return other
	
	def __or__(cls, other):
		return other
	
	def __subclasscheck__(cls, subclass):
		return True


class KAny(metaclass=_KAnyMeta):
	def __new__(cls):
		raise TypeError("Can't init KAny")

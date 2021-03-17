from typing import *

from .type_aliases import I, InK, OutV, OutI, T
from ._special import KAny
from ._core import K, KWrapper
from ..__settings__ import PROJECT_TYPE_CHECKER
from ..utils import getattrOrIdentity
from .markers import Stub


class KInt(KWrapper, wrapped=int):
    def __new__(cls, _int):
        self = int.__new__(cls, _int)
        return self

    def untyped(self):
        return int(self)


class KFloat(KWrapper, wrapped=float):
    def __new__(cls, _float):
        self = float.__new__(cls, _float)
        return self

    def untyped(self):
        return float(self)


class KStr(KWrapper, wrapped=str):
    def __new__(cls, _str):
        self = str.__new__(cls, _str)
        return self

    def untyped(self):
        return str(self)


class KTuple(KWrapper, wrapped=tuple, itemType=OutI):
    __itemType__ = Any

    def __new__(cls, _tuple):
        if _tuple:
            inferredItemType = typedClassOf(_tuple[0])
            inferred = KTuple[inferredItemType]
            PROJECT_TYPE_CHECKER.checkCast(inferred, cls)

            inferredItemTypeIsMoreAccurate = getattrOrIdentity(inferredItemType, "unParametrized")() == cls.__itemType__
            itemType = cls.__itemType__ if cls.__itemType__ is not KAny and not inferredItemTypeIsMoreAccurate else typedClassOf(_tuple[0])

            self = tuple.__new__(KTuple[itemType], _tuple)
        else:
            self = tuple.__new__(cls, _tuple)
        return self

    def __get_type_arguments_for__(self, _type):
        if not issubclass(_type, Iterable):
            return NotImplemented

        return self.__itemType__

    @classmethod
    def __from_wrapped__(cls, _tuple):
        return cls(_tuple)

    def untyped(self):
        return tuple(self)


class KList(KWrapper, wrapped=list, itemType=I):
    __itemType__ = Any

    def __new__(cls, *_list):
        if _list:
            inferredItemType = typedClassOf(_list[0])
            inferred = KList[inferredItemType]
            PROJECT_TYPE_CHECKER.checkCast(inferred, cls)

            inferredItemTypeIsMoreAccurate = getattrOrIdentity(inferredItemType, "unParametrized")() == cls.__itemType__
            itemType = cls.__itemType__ if cls.__itemType__ is not Any and not inferredItemTypeIsMoreAccurate else inferredItemType

            self = list.__new__(KList[itemType], _list)
        else:
            self = list.__new__(cls, _list)

        return self

    def __get_type_arguments_for__(self, _type):
        if not issubclass(_type, Iterable):
            return NotImplemented

        return self.__itemType__

    @classmethod
    def __from_wrapped__(cls, _list):
        return cls(_list)

    def untyped(self):
        return list(self)


class KSet(KWrapper, wrapped=set, itemType=I):
    __itemType__ = Any

    def __new__(cls, _set):
        if _set:

            inferredItemType = typedClassOf(list(_set)[0])
            inferred = KSet[inferredItemType]
            PROJECT_TYPE_CHECKER.checkCast(inferred, cls)

            inferredItemTypeIsMoreAccurate = getattrOrIdentity(inferredItemType, "unParametrized")() == cls.__itemType__
            itemType = cls.__itemType__ if cls.__itemType__ is not Any and not inferredItemTypeIsMoreAccurate else inferredItemType

            self = set.__new__(KSet[itemType], _set)
        else:
            self = set.__new__(cls, _set)

        return self

    def __get_type_arguments_for__(self, _type):
        if not issubclass(_type, Iterable):
            return NotImplemented

        return self.__itemType__

    def untyped(self):
        return set(self)


class KDict(KWrapper, wrapped=dict, keyType=InK, valueType=OutV):
    __keyType__ = Any
    __valueType__ = Any

    def __new__(cls, dct):
        if dct:
            key0 = list(dct.keys())[0]
            value0 = list(dct.values())[0]
            
            inferred = KDict[typedClassOf(key0), typedClassOf(value0)]
            PROJECT_TYPE_CHECKER.checkCast(inferred, cls)

            keyType = cls.__keyType__ if cls.__keyType__ is not KAny else typedClassOf(key0)
            valueType = cls.__valueType__ if cls.__valueType__ is not KAny else typedClassOf(value0)

            self = dict.__new__(cls[keyType, valueType], dct)
        else:
            self = dict.__new__(cls, dct)

        return self

    def __get_type_arguments_for__(self, _type):
        if issubclass(_type, dict):
            return self.__keyType__, self.__valueType__
        elif issubclass(_type, Iterable):
            return self.__keyType__
        else:
            return NotImplemented

    def untyped(self):
        return dict(self)

    @Stub
    def __getitem__(self, key: InK) -> OutV: ...
    @Stub
    def get(self, key: InK) -> Optional[OutV]: ...


__builtins = {
    int: KInt,
    float: KFloat,
    str: KStr,
    tuple: KTuple,
    list: KList,
    dict: KDict,
}


def typedClassOf(obj):
    objType = type(obj)
    
    if issubclass(objType, KWrapper):
        return objType
    
    if any(issubclass(objType, b) for b in __builtins):
        typedClass =  __builtins[objType]
    else:
        typedClass = K[objType]

    return type(typedClass(obj, _fromCore=True))


def typed(obj):
    return typedClassOf(obj)(obj)

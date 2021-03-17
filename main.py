from kobra.typing.builtins import *


def myFunction(a: KTuple[str]):
    if not isinstance(a, KTuple[str]):
        raise TypeError()


class A(str):
    pass


def main() -> None:
    a = KDict[KTuple[int], str]& {("",): ""}
    print(type(a))


if __name__ == '__main__':
    main()

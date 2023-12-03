import sys


def add(x: int, y: int) -> int:
    return x + y


def multiply(x: int, y: int) -> int:
    return x * y


def str_concat(s1: str, s2: str) -> str:
    return s1 + s2


def times2(x: float) -> float:
    return x * 2


def printpath() -> list[str]:
    return sys.path

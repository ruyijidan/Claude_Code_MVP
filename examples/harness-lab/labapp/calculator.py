"""Tiny calculator module used by the harness learning lab."""


def add(left: float, right: float) -> float:
    return left + right


def divide(left: float, right: float) -> float:
    if right == 0:
        return 0
    return left / right

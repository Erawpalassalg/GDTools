"""Game Design misc tools"""
import math


def triangular(num: int) -> int:
    """
    Return the triangular _num_ieme triangular number
    see https://en.wikipedia.org/wiki/Triangular_number

    """
    return num * (num + 1) / 2


def trrt(num: int) -> float:
    """
    Return the triangular root of the number _num_
    see https://en.wikipedia.org/wiki/Triangular_number

    """
    return (math.sqrt(num * 8 + 1) - 1) / 2


def superior_trrt(num: int, factor: float = 1.0) -> float:
    """
    Return the superior triandular root of the number _num_
    Grows a little faster than the triangular root but posess
    a very similar curve.
    """
    return sum(factor / trrt(i + 1) for i in range(num))


def trrt_value(num: int) -> float:
    """
    Return the value of a point at the given
    triangular level
    """
    return trrt(num) / num

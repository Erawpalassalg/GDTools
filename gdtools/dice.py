"""Object oriented dice manipulation"""
from __future__ import annotations
import itertools
import random
from collections import Counter

from typing import Union, Callable, Tuple


def normalize_rng(value: Union[Dice, range]) -> Tuple[range, int]:
    """
    Normalize to a dice-like range and a modificator.
    All ranges will end up going from 1 to X and the extra numbers
    will be put in the modificator.

    For example, `range(4, 10)` will end up as `(range(1, 7), 3)`, which is
    `1d6 + 3`

    """
    rng = value.rng if isinstance(value, Dice) else value
    mod = rng.start - 1
    return (range(rng.start - mod, rng.stop - mod), mod)


class Dice:
    """
    An object representing a dice such as `d6` or `d13`

    Make for easy manipulations of such objects, enabling additions and
    substractions with other Dice, int and DicePool objects.

    Also posess some interresting functions such as `rgt(threshold)` to
    get the odds of this dice range having a result greater than the threshold.

    A Dice should be seen as an immutable object.

    Can be build with:
        d6 = Dice(6)
        d4_12 = Dice(4, 12)

    Since this object is range based, a dice such as `Dice(4, 12)` can exists,
    bus is basically the same thing as a `d9 + 3`
    """

    def __init__(self, p1: int, p2: int = None):
        if not isinstance(p1, int) or (p2 is not None and not isinstance(p2, int)):
            raise ValueError("Dice faces should be integer")

        if p2 is None:
            self.rng = range(1, p1 + 1)
        else:
            self.rng = range(p1, p2 + 1)
        self.avg = sum(self.rng) / (self.rng.stop - 1)
        self.min = self.rng.start
        self.max = self.rng.stop - 1
        self.sides = self.max

    def __str__(self):
        mod = self.rng.start - 1
        expr = f"d{self.rng.stop - mod - 1}"
        if mod != 0:
            if mod > 0:
                expr += " + "
            else:
                expr += " - "
            expr += str(abs(mod))
        return expr

    def __repr__(self):
        return self.__str__()

    def __gt__(self, other: Dice) -> bool:
        if not isinstance(other, Dice):
            return NotImplemented
        return self.avg > other.avg

    def __lt__(self, other: Dice) -> bool:
        if not isinstance(other, Dice):
            return NotImplemented
        return self.avg < other.avg

    def __ge__(self, other: Dice) -> bool:
        if not isinstance(other, Dice):
            return NotImplemented
        return self.avg >= other.avg

    def __le__(self, other: Dice) -> bool:
        if not isinstance(other, Dice):
            return NotImplemented
        return self.avg <= other.avg

    def __add__(self, other: Union[DicePool, Dice, int]) -> DicePool:
        if isinstance(other, (int, Dice)):
            return DicePool(self, other)
        return NotImplemented

    def __radd__(self, other: Union[DicePool, Dice, int]) -> DicePool:
        return self.__add__(other)

    def __mul__(self, other: int) -> DicePool:
        if isinstance(other, int):
            return DicePool(*[Dice(self.min, self.max) for _ in range(other)])
        return NotImplemented

    def __rmul__(self, other: int) -> DicePool:
        return self.__mul__(other)

    def _chances(self, threshold: int, comparator: Callable) -> float:
        """
        Comparator should be a lambda such as `lambda a, b: a > b`

        Return the rate with which this dice compare its possible
        results with the threshold favorably.

        Result is 1.0 >= rate >= 0.0, multiply it by 100 get percents.

        """
        total_chances = self.rng.stop - self.rng.start
        chances_to_pass = len(
            result for result in self.rng if comparator(result, threshold)
        )
        return chances_to_pass / total_chances

    def rgt(self, threshold: int) -> float:
        """
        Return the chances of this dice having a roll greater
        than the threshold

        """
        if not isinstance(threshold, int):
            raise NotImplementedError("Only supports int for now")
        return len(list(filter(lambda i: i > threshold, self.rng))) / self.max

    def rge(self, threshold: int) -> float:
        """
        Return the chances of this dice having a roll greater
        than or equal to the threshold

        """
        if not isinstance(threshold, int):
            raise NotImplementedError("Only supports int for now")
        return self._chances(threshold, lambda a, b: a >= b)

    def rlt(self, threshold: int) -> float:
        """
        Return the chances of this dice having a roll lower
        than the threshold

        """
        if not isinstance(threshold, int):
            raise NotImplementedError("Only supports int for now")
        return self._chances(threshold, lambda a, b: a < b)

    def rle(self, threshold: int) -> float:
        """
        Return the chances of this dice having a roll lower
        than or equal to the threshold

        """
        if not isinstance(threshold, int):
            raise NotImplementedError("Only supports int for now")
        return self._chances(threshold, lambda a, b: a <= b)

    def roll(self):
        """
        Roll the dice, get its result.

        """
        return random.randrange(self.rng.start, self.rng.stop)


class DicePool:
    """
    An object representing a dice pool such as `1d6 + 3d5 + 1d4 - 3`

    Makes for easy manipulations of such objects, enabling additions and
    substractions with other Dice, int and DicePool objects.

    A DicePool should be seen as an immutable object.

    DicePool can be instanciated by additionning Dice objects,
    int and other DicePools:
    ````
        my_dice_pool = Dice(6) + Dice(10)
        my_other_dice_pool = my_dice_pool + Dice(12) + 3
    ````

    Otherwise, pass them to the constructor:
    ````
        my_dice_pool = DicePool(Dice(6), Dice(10), 3, Dice(12), -5)

    ````

    Also work with ranges:
    ````
        my_dice_pool = DicePool(range(1, 7), range(1, 11), 3, range(1, 13), -5)
    ````

    """

    def __init__(self, *args):
        rngs, self.mod = list(), 0
        for arg in args:
            if isinstance(arg, int):
                self.mod += arg
            elif isinstance(arg, (Dice, range)):
                nrm = normalize_rng(arg)
                rngs.append(nrm[0])
                self.mod += nrm[1]
        self.rngs = tuple(rngs)

        self.dist = Counter(
            sum(result) + self.mod for result in itertools.product(*self.rngs)
        )
        self.min = next(iter(self.dist))
        self.max = list(self.dist)[-1]

        values = list(self.dist.keys())
        self.range = range(values[0], values[-1])

    def __str__(self):
        pool = {}
        for rng in self.rngs:
            pool[rng] = pool.get(rng, 0) + 1
        expr = " + ".join(f"{num}d{rng.stop - 1}" for rng, num in pool.items())
        if self.mod != 0:
            if self.mod > 0:
                expr += " + "
            else:
                expr += " - "
            expr += str(abs(self.mod))
        return expr

    def __repr__(self):
        return self.__str__()

    def __gt__(self, other: DicePool):
        return NotImplemented

    def __lt__(self, other: DicePool):
        return NotImplemented

    def __ge__(self, other: DicePool):
        return NotImplemented

    def __le__(self, other: DicePool):
        return NotImplemented

    def __eq__(self, other: Union[Dice, DicePool]):
        if isinstance(other, Dice):
            rng, mod = normalize_rng(other)
            return self.rngs == tuple(rng) and self.mod == mod
        if isinstance(other, DicePool):
            return self.dist == other.dist and self.mod == other.mod
        return NotImplemented

    def __ne__(self, other: Union[Dice, DicePool]):
        if isinstance(other, Dice):
            return self.rngs != tuple(other.rng)
        if isinstance(other, DicePool):
            return self.dist != other.dist or self.mod != other.mod
        return NotImplemented

    def __add__(self, other: Union[DicePool, Dice, int]) -> DicePool:
        if isinstance(other, int):
            return DicePool(*self.rngs, self.mod + other)
        if isinstance(other, Dice):
            return DicePool(*self.rngs, other.rng, self.mod)
        return DicePool(*(self.rngs + other.rngs), self.mod + other.mod)

    def __sub__(self, other: Union[Dice, int]) -> DicePool:
        if isinstance(other, int):
            return DicePool(*self.rngs, self.mod - other)
        if isinstance(other, Dice):
            rng, mod = normalize_rng(other)
            if rng in self.rngs:
                rngs = list(self.rngs)
                rngs.remove(rng)
                return DicePool(*rngs, self.mod - mod)
            raise ValueError(f"This range does not contain a {str(other)}")
        return NotImplemented

    def _chances(self, threshold: int, comparator: Callable) -> float:
        """
        Comparator should be a lambda such as `lambda a, b: a > b`

        Return the rate with which this dice pool compare its possible
        results with the threshold favorably.

        Result is 1.0 >= rate >= 0.0, multiply it by 100 get percents.

        """
        total_chances = sum(self.dist.values())
        chances_to_pass = sum(
            [
                chances
                for result, chances in self.dist.items()
                if comparator(result, threshold)
            ]
        )
        return chances_to_pass / total_chances

    def show(self) -> None:
        """
        Print the dice pool distribution on several lines.
        Useful to take a quick look at how tiny distributions look like.

        """
        for key, value in self.dist.items():
            print(f"{key}\t{'. '*value}")

    def average(self) -> float:
        """
        Return the dice pool average number.
        """
        return float(
            sum([key * value for key, value in self.dist.items()])
            / sum(self.dist.values())
        )

    def rgt(self, threshold: int) -> float:
        """
        Return the chances of this dice pool having a roll greater
        than the threshold

        """
        if not isinstance(threshold, int):
            raise NotImplementedError("Only supports int for now")
        return self._chances(threshold, lambda a, b: a > b)

    def rge(self, threshold: int) -> float:
        """
        Return the chances of this dice pool having a roll greater
        than or equal to the threshold

        """
        if not isinstance(threshold, int):
            raise NotImplementedError("Only supports int for now")
        return self._chances(threshold, lambda a, b: a >= b)

    def rlt(self, threshold: int) -> float:
        """
        Return the chances of this dice pool having a roll lower
        than the threshold

        """
        if not isinstance(threshold, int):
            raise NotImplementedError("Only supports int for now")
        return self._chances(threshold, lambda a, b: a < b)

    def rle(self, threshold: int) -> float:
        """
        Return the chances of this dice pool having a roll lower
        than or equal to the threshold

        """
        if not isinstance(threshold, int):
            raise NotImplementedError("Only supports int for now")
        return self._chances(threshold, lambda a, b: a <= b)

    def roll(self):
        """
        Roll the dice pool, get its result.
        """
        product = list(itertools.product(*self.rngs))
        return sum(product[random.randrange(len(product) - 1)])

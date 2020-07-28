# GDTools

A game design utilities library for Python 3.7+

## dice.py

This lib aims to easily simulate dices.

You can create and roll all kinds of dices

```
>>> from gdtools.dice import Dice
>>> d6 = Dice(6)
>>> d6.roll()
5   

```


It simplifies weird dices for you

```
>>> d2_14 = Dice(2, 14)
>>> print(d2_14)
1d13 + 1

```


You can combine dices in a dice pool

```
>>> pool = d6 + d2_14
>>> print(pool)
1d6 + 1d13 + 1
>>> pool.roll()
7

```


And the pool supports basic operations, on dices or on the modificator

```
>>> pool -= 5
>>> print(pool)
1d6 + 1d13 - 4
>>> print(d6 * 5)
5d6
>>> print(d6 * 5 - d6)
4d6
```



Finally, there are some utilities on both the `Dice` and `DicePool` classes:

```
>>> _2d6 = d6 * 2
>>> _2d6.average()
7
>>> _2d6.rge(7) # stands for "chances to roll for greater or equal to"
0.5833333333333334 

```

For now only `rge`, `rgt`, `rle` and `rlt` are supported

## gdtools.py

It aims to be a collection of utilities for game design

For now, it only supports [triangular number](https://simple.wikipedia.org/wiki/Triangular_number) operations

from datetime import timedelta
from copy import deepcopy
from utils.helpers import isint


def duration(t):
    return timedelta(minutes=t) if t < 10 or not isint(t) else timedelta(seconds=t)


class Resource:

    def __init__(self, name, prod_time, cost: 'Resource' = 0, amount=1):

        self.Name = name
        self.N = amount
        self.ProdTime = duration(prod_time)
        self.Cost = cost
        self.Value = None

    def __add__(self, other):
        v = deepcopy(self)
        return v.update(self.N + other)

    def __sub__(self, other):
        return self.__add__(-other)

    def __mul__(self, other):
        v = deepcopy(self)
        return v.update(self.N * other)

    def __str__(self):
        return self.Name.title()

    def __repr__(self):
        n = f'{self.N} ' if self.N > 1 else ""
        return f'{n}{self}'

    @property
    def prod_time(self):
        return self.ProdTime * self.N

    @property
    def cost(self):
        return self.Cost * self.N

    def update(self, n):
        self.N = n
        return self


Pinewood = Resource('pinewood', 90)

Coal = Resource('coal', 3, Pinewood * 2)

CopperOre = Resource('copper ore', 3)
IronOre = Resource('iron ore', 6)
GoldOre = Resource('gold ore', 12.)



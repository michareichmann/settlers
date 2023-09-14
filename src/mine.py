from src.resource import *
from datetime import datetime
from typing import List


def now():
    return datetime.now().replace(microsecond=0)


class Mine:

    def __init__(self, resource: Resource, dep_size: int, extra_time, prod_time=None, lvl=1):

        self.Resource = resource * dep_size
        self.ExtraTime = duration(extra_time)
        self._ProdTime = resource.ProdTime if prod_time is None else duration(prod_time)
        self.ProdTime = self._ProdTime + self.ExtraTime
        self.Level = lvl

        self.T = now()
        self.EndOfLife = self.end_of_life

    def set_deposit(self, s):
        self.T = now()
        self.Resource.update(s)
        self.EndOfLife = self.end_of_life

    def __repr__(self):
        return f'{self.__class__.__name__}{self.dep_str()}'

    def dep_str(self):
        return f' containing {self.Resource!r}' if self.Resource.N > 1 else ''

    @property
    def end_of_life(self):
        return (self.T + self.Resource.N / self.Level * self.ProdTime).replace(microsecond=0)

    @property
    def time_left(self):
        return self.EndOfLife - now()


class Mines:

    def __init__(self):
        self.L = self.load()

    def load(self) -> List:
        ...

    def save(self):
        ...

    def add(self):
        ...


class CoalMine(Mine):

    def __init__(self, dep_size, extra_time, lvl=1):
        super().__init__(Coal, dep_size, extra_time, prod_time=90, lvl=lvl)


class CopperMine(Mine):

    def __init__(self, dep_size, extra_time, lvl=1):
        super().__init__(CopperOre, dep_size, extra_time, lvl=lvl)


class IronMine(Mine):

    def __init__(self, dep_size, extra_time, lvl=1):
        super().__init__(IronOre, dep_size, extra_time, lvl=lvl)


class GoldMine(Mine):

    def __init__(self, dep_size, extra_time, lvl=1):
        super().__init__(GoldOre, dep_size, extra_time, lvl=lvl)



import pickle
from datetime import datetime
from typing import List

from src.resource import *
from utils.helpers import Dir, load_pickle


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

    DataDir = Dir.joinpath('data')
    FileName = DataDir.joinpath('mines.pickle')

    def __init__(self):
        self.L = self.load()

    def __getitem__(self, item):
        return self.L[item]

    def __repr__(self):
        mine_str = '\n'.join(f'  {mine}' for mine in self)
        return f'Registered mines ({self.size}): \n{mine_str}'

    @property
    def size(self):
        return len(self.L)

    @staticmethod
    def load() -> List:
        return load_pickle(Mines.FileName) if Mines.FileName.exists() else []

    def save(self):
        with open(self.FileName, 'wb') as f:
            pickle.dump(self.L, f)

    def register(self, mine: Mine):
        self.L.append(mine)
        self.save()

    def remove(self, i):
        print(f'removed {self.L.pop(i)} from the mines')
        self.save()


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



import pickle
from datetime import datetime
from functools import partial
from typing import List

import numpy as np

from src.resource import *
from utils.helpers import Dir, load_pickle, print_table, info


def now():
    return datetime.now().replace(microsecond=0)


class Mine:

    def __init__(self, resource: Resource, dep_size: int, extra_time, prod_time=None, lvl=1, paused=False, speed=1):

        # FEATURES
        self.Resource = resource * int(dep_size)
        self.ExtraTime = duration(extra_time)
        self._ProdTime = resource.ProdTime if prod_time is None else duration(prod_time)
        self.Speed = speed
        self.ProdTime = self._ProdTime * speed + self.ExtraTime
        self.Level = int(lvl)
        self.Paused = bool(paused)

        self.T = now()

    def __str__(self):
        return f'{self.Resource} mine'

    def __repr__(self):
        return f'Lvl {self.Level} {self} containing {self.Resource!r}'

    def __lt__(self, other: 'Mine'):
        return other.Paused if self.Paused != other.Paused else self.time_left < other.time_left

    def update(self):
        tdiff = now() - self.T
        self.T += tdiff
        if not self.Paused:
            n_cycles = int(tdiff / self.ProdTime)
            self.Resource -= n_cycles * self.Level

    @property
    def time_left(self):
        return np.ceil(self.Resource.N / self.Level) * self.ProdTime

    @property
    def time_left_str(self):
        return f'({self.time_left})' if self.Paused else str(self.time_left)
    
    def extra_time(self, n):
        rest = self.Resource.N % self.Level
        cycles = int((rest + n) / self.Level)
        print(rest, n, cycles)
        return cycles * self.ProdTime

    def set_lvl(self, lvl):
        self.Level = lvl

    def upgrade(self):
        self.set_lvl(self.Level + 1)

    def set_deposit(self, s):
        self.T = now()
        self.Resource.update(s)

    def add_deposit(self, n):
        self.Resource += n
        info(f'You added {self.extra_time(n)} of life time')

    def set_status(self, status: bool):
        self.Paused = status
    pause = partial(set_status, True)
    activate = partial(set_status, False)

    def change_status(self):
        self.set_status(not self.Paused)

    @property
    def data(self):
        return [self.Resource, self.Level, self.Resource.N, self.time_left_str, ['ON', 'OFF'][self.Paused]]


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

    def __add__(self, other: Mine):
        self.L.append(other)
        self.L = sorted(self.L)
        self.save()

    @property
    def size(self):
        return len(self.L)

    @staticmethod
    def load() -> List:
        return load_pickle(Mines.FileName) if Mines.FileName.exists() else []

    def save(self):
        with open(self.FileName, 'wb') as f:
            pickle.dump(sorted(self.L), f)

    def reload(self):
        self.save()
        self.L = self.load()

    def register(self, mine: Mine):
        self.L.append(mine)

    def remove(self, i):
        print(f'removed {self.L.pop(i)} from the mines')

    def update(self):
        for mine in self:
            mine.update()

    def print(self):
        rows = [[i, m.Resource, m.Level, m.Resource.N, str(m.time_left)] for i, m in enumerate(self.L)]
        print_table(rows, header=['Index', 'Type', 'Lvl', 'Deposit', 'Time left'])

    def add_deposit(self, i, n):
        self[i].add_deposit(n)


class CoalMine(Mine):

    def __init__(self, dep_size, extra_time, lvl=1, paused=False, speed=1):
        super().__init__(Coal, dep_size, extra_time, prod_time=90, lvl=lvl, paused=paused, speed=speed)


class CopperMine(Mine):

    def __init__(self, dep_size, extra_time, lvl=1, paused=False, speed=1):
        super().__init__(CopperOre, dep_size, extra_time, lvl=lvl, paused=paused, speed=speed)


class IronMine(Mine):

    def __init__(self, dep_size, extra_time, lvl=1, paused=False, speed=1):
        super().__init__(IronOre, dep_size, extra_time, lvl=lvl, paused=paused, speed=speed)


class GoldMine(Mine):

    def __init__(self, dep_size, extra_time, lvl=1, paused=False, speed=1):
        super().__init__(GoldOre, dep_size, extra_time, lvl=lvl, paused=paused, speed=speed)


def mine_from_str(s, dep_size, extra_time, lvl=1, paused=False, speed=1):
    classes = [CopperMine, IronMine, CoalMine, GoldMine]
    return next(cls(dep_size, extra_time, lvl, paused, speed) for cls in classes if s.split('-')[0].lower() in cls.__name__.lower())



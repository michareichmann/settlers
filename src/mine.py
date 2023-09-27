import pickle
from datetime import datetime
from functools import partial
from typing import List

import numpy as np

from src.resource import *
from utils.helpers import Dir, load_pickle, print_table, info, say


def now():
    return datetime.now().replace(microsecond=0)


class Mine:

    Resource: Resource = None

    def __init__(self, dep_size: int, extra_time, lvl=1, speed=1, paused=False):

        # FEATURES
        self.Deposit = dep_size
        self.ExtraTime = duration(extra_time)
        self._ProdTime = self.Resource.ProdTime
        self.Speed = speed
        self.ProdTime = self._ProdTime / speed + self.ExtraTime
        self.Level = int(lvl)
        self.Paused = bool(paused)

        self.LastProduced = now()

        self.Warnings = {t: True for t in [60, 30, 10, 1, 0]}

    def __str__(self):
        return f'{self.Resource} mine'

    def __repr__(self):
        return f'Lvl {self.Level} {self} containing {self.Resource!r}'

    def __lt__(self, other: 'Mine'):
        return other.Paused if self.Paused != other.Paused else self.time_left < other.time_left

    def update(self):
        tdiff = now() - self.LastProduced
        if not self.Paused:
            n_cycles = int(tdiff / self.ProdTime)
            if n_cycles > 0:
                self.LastProduced += n_cycles * self.ProdTime
                self.Deposit -= n_cycles * self.Level
        self.warn()

    def warn(self):
        t0 = self.time_left
        for t, b in self.Warnings.items():
            if t0.total_seconds() < t * 60 and b:
                say(f'{t} min left for {self}' if t > 0 else f'Your {self} was destroyed')
                self.Warnings[t] = False

    @property
    def time_left(self):
        time_till_next_production = timedelta(0) if self.Paused else self.ProdTime - (now() - self.LastProduced)
        return np.ceil(self.Deposit / self.Level) * self.ProdTime + time_till_next_production

    @property
    def time_left_str(self):
        t = self.time_left
        return f'({t})' if self.Paused else str(t) if t.total_seconds() > 0 else 'Destroyed'
    
    def extra_time(self, n):
        rest = self.Deposit % self.Level
        cycles = int((rest + n) / self.Level)
        return cycles * self.ProdTime

    def set_lvl(self, lvl):
        self.Level = lvl

    def upgrade(self):
        self.set_lvl(self.Level + 1)

    def set_deposit(self, s):
        self.Deposit = s

    def add_deposit(self, n):
        self.Deposit += n
        info(f'You added {self.extra_time(n)} of life time')

    def set_status(self, status: bool):
        self.Paused = status
    pause = partial(set_status, True)
    activate = partial(set_status, False)

    def change_status(self):
        self.set_status(not self.Paused)

    @property
    def status(self):
        return ['ON', 'OFF'][self.Paused]

    @property
    def data(self):
        return [self.Level, self.Deposit, self.time_left_str]


class Mines:

    DataDir = Dir.joinpath('data')

    def __init__(self, file_name):
        self.FileName = Mines.DataDir.joinpath(f'{file_name}.pickle')
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

    def __iter__(self):
        return iter(self.L)

    @property
    def size(self):
        return len(self.L)

    def load(self) -> List:
        return load_pickle(self.FileName) if self.FileName.exists() else []

    def save(self):
        with open(self.FileName, 'wb') as f:
            pickle.dump(self.L, f)

    def clear(self):
        self.L = []
        self.save()

    def reload(self):
        self.save()
        self.L = self.load()

    def reload_classes(self):
        for mine in self:
            for k, v in mine.__class__(0, 0).__dict__.items():
                if k not in mine.__dict__:
                    mine.__dict__[k] = v
            mine.__class__ = eval(mine.__class__.__name__)

    def register(self, mine: Mine):
        self.L.append(mine)

    def remove(self, i):
        print(f'removed {self.L.pop(i)} from the mines')

    def update(self):
        for mine in self:
            mine.update()

    def print(self):
        rows = [[i, m.Resource, m.Level, m.Deposit, str(m.time_left)] for i, m in enumerate(self.L)]
        print_table(rows, header=['Index', 'Type', 'Lvl', 'Deposit', 'Time left'])

    def add_deposit(self, i, n):
        self[i].add_deposit(n)


class CopperMine(Mine):
    Resource = CopperOre


class CoalMine(Mine):

    Resource = Coal

    def __init__(self, dep_size, extra_time, lvl=1, speed=1, paused=False):
        super().__init__(dep_size, extra_time, lvl, speed * 2, paused)


class IronMine(Mine):
    Resource = IronOre


class GoldMine(Mine):
    Resource = GoldOre


def mine_classes():
    return [CopperMine, IronMine, CoalMine, GoldMine]


def mine_from_str(s, dep_size, extra_time, lvl=1, speed=1, paused=False):
    return next(cls(dep_size, extra_time, lvl, speed, paused) for cls in mine_classes() if s.split('-')[0].lower() in cls.__name__.lower())



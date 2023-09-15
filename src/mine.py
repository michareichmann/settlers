import pickle
from datetime import datetime
from typing import List

from src.resource import *
from utils.helpers import Dir, load_pickle, print_table, info
from threading import Timer


class RepeatTimer(Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)


def now():
    return datetime.now().replace(microsecond=0)


class Mine:

    def __init__(self, resource: Resource, dep_size: int, extra_time, prod_time=None, lvl=1, paused=False):

        self.Resource = resource * dep_size
        self.ExtraTime = duration(extra_time)
        self._ProdTime = resource.ProdTime if prod_time is None else duration(prod_time)
        self.ProdTime = self._ProdTime + self.ExtraTime
        self.Level = lvl

        self.T = now()
        self.EndOfLife = self.end_of_life

        self.Paused = paused

    def __repr__(self):
        return f'{self.Resource} mine containing {self.Resource!r}'

    def __lt__(self, other: 'Mine'):
        return self.EndOfLife < other.EndOfLife

    def set_lvl(self, lvl):
        self.Level = lvl
        self.EndOfLife = self.end_of_life

    def set_deposit(self, s):
        self.T = now()
        self.Resource.update(s)
        self.EndOfLife = self.end_of_life

    def add_deposit(self, n):
        self.Resource += n
        new_eol = self.end_of_life
        info(f'You added {new_eol - self.EndOfLife} of life time')
        self.EndOfLife = new_eol

    @property
    def end_of_life(self):
        return (self.T + self.Resource.N / self.Level * self.ProdTime).replace(microsecond=0)

    @property
    def time_left(self):
        return None if self.Paused else self.EndOfLife - now()

    def update(self):
        tdiff = now() - self.T
        n_cycles = int(tdiff / self.ProdTime)
        self.T += n_cycles * self.ProdTime
        if not self.Paused:
            self.Resource -= n_cycles * self.Level

    def pause(self):
        self.Paused = True

    def activate(self):
        self.Paused = False


class Mines:

    DataDir = Dir.joinpath('data')
    FileName = DataDir.joinpath('mines.pickle')

    def __init__(self):
        self.L = self.load()

        self.Timer = RepeatTimer(5, self.update)
        self.Timer.start()

    def __getitem__(self, item):
        return self.L[item]

    def __repr__(self):
        mine_str = '\n'.join(f'  {mine}' for mine in self)
        return f'Registered mines ({self.size}): \n{mine_str}'

    def __del__(self):
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

    def register(self, mine: Mine):
        self.L.append(mine)

    def remove(self, i):
        print(f'removed {self.L.pop(i)} from the mines')

    def update(self):
        for mine in self:
            mine.update()

    def print(self):
        rows = [[m.Resource, m.Level, m.Resource.N, str(m.time_left)] for m in self.L]
        print_table(rows, header=['Type', 'Lvl', 'Deposit', 'Time left'])


class CoalMine(Mine):

    def __init__(self, dep_size, extra_time, lvl=1, paused=False):
        super().__init__(Coal, dep_size, extra_time, prod_time=90, lvl=lvl, paused=paused)


class CopperMine(Mine):

    def __init__(self, dep_size, extra_time, lvl=1, paused=False):
        super().__init__(CopperOre, dep_size, extra_time, lvl=lvl, paused=paused)


class IronMine(Mine):

    def __init__(self, dep_size, extra_time, lvl=1, paused=False):
        super().__init__(IronOre, dep_size, extra_time, lvl=lvl, paused=paused)


class GoldMine(Mine):

    def __init__(self, dep_size, extra_time, lvl=1, paused=False):
        super().__init__(GoldOre, dep_size, extra_time, lvl=lvl, paused=paused)



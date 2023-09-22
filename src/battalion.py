from src.units import Unit
from copy import deepcopy
from utils.helpers import info

import numpy as np
import numpy.random as rnd


class Battalion:

    def __init__(self, n: int, unit: Unit):

        self.N = n
        self.Unit = unit
        self.Units = [deepcopy(unit) for _ in range(n)]
        self.HP = np.sum([unit.HP for unit in self])

        self.NAttacks = 0
        self.NDefeated = 0

    def __repr__(self):
        return f'{self.Unit.Name} Batallion ({self.alive_str})\n'

    def __getitem__(self, item):
        return self.Units[item]

    @property
    def alive_str(self):
        return f'{self.n_alive}/{self.N}'

    @property
    def n_alive(self):
        return np.count_nonzero([not u.Dead for u in self.Units])

    @property
    def can_attack(self):
        return self.n_can_attack > 0

    @property
    def n_can_attack(self):
        return self.N - self.NDefeated - self.NAttacks

    @property
    def dead(self):
        return self.Units[-1].Dead

    @property
    def alive(self):
        return not self.dead

    @property
    def next(self):
        return next(unit for unit in self.Units if not unit.Dead)

    @property
    def dmg(self):
        return sum(u.dmg for u in self)

    def update_n_defeated(self):
        self.NDefeated = self.N - self.n_alive

    def revive(self):
        for unit in self.Units:
            unit.revive()
        self.reset()

    def reset(self):
        self.NAttacks = 0
        self.NDefeated = 0

    def splash(self, n):
        return rnd.random(n) < self.Unit.Splash if 0 < self.Unit.Splash < 1 else np.full(n, bool(self.Unit.Splash))

    def _dmg(self, n):
        return np.array([self.Unit.DmgMin, self.Unit.DmgMax])[np.array(rnd.random(n) < self.Unit.Accuracy, dtype='i')]

    def _attack(self, battalion: 'Battalion'):
        n = self.n_can_attack
        splash = self.splash(n)
        dmg = self._dmg(n)
        for i, unit in enumerate(self.Units[-n:]):  # last n can attack
            try:
                if splash[i]:
                    if unit.CurrentDmg is None:
                        unit.CurrentDmg = dmg[i]
                    while unit.CurrentDmg > 0:
                        unit.splash_attack(battalion.next)
                    unit.reset_current_dmg()  # only gets called if the unit runs out of damage
                else:
                    unit.attack(battalion.next, dmg[i])
                self.NAttacks += 1
            except StopIteration:
                break

    def print_attack(self, battalion: 'Battalion'):
        if battalion is not None:
            n0, n1 = self.n_can_attack, battalion.n_alive
            self._attack(battalion)
            info(f'{n0} {self.Unit.Name} killed {n1 - battalion.n_alive} {battalion.Unit.Name} ({battalion.alive_str})')

    def sim_attack(self, battallion: 'Battalion', s=10000):
        n = self.n_can_attack
        first_kill = self.Unit.DmgMax > battallion.Unit.HP
        p = self.Unit.Accuracy
        r = rnd.random(n * s)
        kills = rnd.random(n * s) < 1 - p + p * p
        # return kills
        kills[::n] = r[::n] < p
        kills = np.array_split(kills, s)
        n_kills = np.sum(kills, axis=1)
        return n_kills

import numpy as np
import numpy.random as rnd

from src.army import Army
from src.battalion import Battalion
from utils.helpers import warning


class FightSimulation:

    Speeds = [2, 1, 0]

    def __init__(self, attacker: Army, defender: Army):

        self.Attacker = attacker
        self.Defender = defender

    def __getitem__(self, item):
        return (list(self.Attacker) + list(self.Defender))[item]

    def reset_battalions(self, n):
        for bat in self:
            bat.NAlive = np.full(int(n), bat.N)
            bat.NDefeated = np.zeros(int(n), 'i')
        self.reset_attacks(n)

    def reset_attacks(self, n):
        for bat in self:
            bat.NAttacks = np.zeros(int(n), 'i')
            bat.ExcessDmg = 0

    def update_n_alive(self):
        for bat in self:
            bat.NAlive = bat.N - bat.NDefeated

    @staticmethod
    def splash_attack(a: Battalion, d: Battalion, dmg=0):
        """ :returns the amount of killed units and the excess damage"""
        if type(a.ExcessDmg) != np.ndarray:  # this is the attack on the first enemy battalion, add excess dmg from earlier attacking unit
            n_high = rnd.binomial(a.n_can_attack, a.P)
            dmg += (n_high * a.Unit.DmgMax + (a.n_can_attack - n_high) * a.Unit.DmgMin)
        else:  # if there is dmg from the battalion attacked previously just continue with this dmg
            dmg = a.ExcessDmg
        n_killed = dmg // d.Unit.HP
        cut = d.NAlive < n_killed
        n_killed[cut] = d.NAlive[cut]
        excess_dmg = dmg - n_killed * d.Unit.HP
        d.NDefeated += n_killed
        a.ExcessDmg = excess_dmg
        return excess_dmg

    @staticmethod
    def attack(a: Battalion, d: Battalion, dmg=0):
        if a.Unit.Splash == 1:
            return FightSimulation.splash_attack(a, d, dmg)
        warning(f'{a} attacking {d} is not implemented yet...')

    @staticmethod
    def round(speed, attacker: Army, defender: Army):
        """ simulate one round of a batallion attack"""
        for a in attacker.speed_batallions(speed):
            ind = iter(defender.indices(a.Unit.Flanking))
            while a.can_attack and not defender.defeated:
                try:
                    i = next(ind)
                except StopIteration:
                    break
                attacker.ExcessDmg = FightSimulation.attack(a, defender[i], attacker.ExcessDmg)
            a.reset_attacks()

    def run(self, n):
        self.reset_battalions(n)
        for speed in self.Speeds:
            self.round(speed, self.Attacker, self.Defender)
            self.round(speed, self.Defender, self.Attacker)
            self.update_n_alive()

from utils.helpers import *
from src.units import *

Verbose = False

SpeedDict = {0: 'Slow',
             1: 'Normal',
             2: 'Fast'}


def set_verbose(status=ON):
    global Verbose
    old_verbose = Verbose
    Verbose = status
    return old_verbose


class Battalion:

    def __init__(self, n: int, unit: Unit):

        self.N = n
        self.Unit = unit
        self.Units = [deepcopy(unit) for _ in range(n)]
        self.HP = np.sum([unit.HP for unit in self])
        self.NAttacks = 0
        self.NDefeated = 0

    def __repr__(self):
        return f'{self.Unit.Name} Batallion with {self.n_alive}/{self.N} units\n'

    def __getitem__(self, item):
        return self.Units[item]

    @property
    def n_alive(self):
        return np.count_nonzero([not u.Dead for u in self.Units])

    @property
    def can_attack(self):
        return self.NAttacks + self.NDefeated < self.N

    @property
    def dead(self):
        return self.Units[-1].Dead

    @property
    def alive(self):
        return not self.dead

    @property
    def next(self):
        return next(unit for unit in self.Units if not unit.Dead)

    def update_n_defeated(self):
        self.NDefeated = self.N - self.n_alive

    def revive(self):
        for unit in self.Units:
            unit.revive()
        self.NAttacks = 0
        self.NDefeated = 0

    def normal_attack(self, battalion: 'Battalion'):
        for unit in self.Units[self.NAttacks + self.NDefeated:]:
            try:
                unit.attack(battalion.next)
                self.NAttacks += 1
            except StopIteration:
                pass
        return 1

    def splash_attack(self, battalion: 'Battalion'):
        dmg = 1
        for unit in self.Units[self.NAttacks + self.NDefeated:]:
            dmg = 0
            try:
                dmg = unit.dmg
                while dmg > 0:
                    enemy = battalion.next
                    dmg = unit.attack(enemy, dmg)  # returns remaining dmg
            except StopIteration:
                return dmg
        return dmg

    def attack(self, battalion: 'Battalion'):
        info(f'attacking with {self.N - self.NAttacks - self.NDefeated} {self.Unit.Name}s', prnt=Verbose)
        splash = np.random.random() < self.Unit.Splash
        dmg = self.splash_attack(battalion) if splash else self.normal_attack(battalion)
        info(battalion, prnt=Verbose)
        return dmg


class Army:
    Units = []

    def __init__(self, *n_units):

        self.Batallions = [Battalion(n, u) for n, u in zip(n_units, self.Units) if n]
        self.Speeds = np.array([bat.Unit.Speed for bat in self])
        self.N = len(self.Batallions)
        self.NUnits = np.sum(bat.N for bat in self)
        self.IHP = self.hp_indices()  # indices sorted by HP

        self.HasAttacked = [False, False, False]

    def __getitem__(self, item):
        return self.Batallions[item]

    def __add__(self, other: Battalion):
        self.Batallions.append(other)
        self.N += 1
        self.IHP = self.hp_indices()
        self.Speeds = np.append(self.Speeds, other.Unit.Speed)
        return self

    def __repr__(self):
        bat_str = '  '.join([f'{bat!r}' for bat in self.Batallions])
        return f'{self.__class__.__name__}:\n  {bat_str}'

    def hp_indices(self):
        hp = [bat.Unit.HP for bat in self]
        return np.append(np.argsort(hp[:-1]), self.N - 1) if self[-1].Unit.Name == 'General' else np.argsort(hp)

    @property
    def size(self):
        return np.sum([bat.n_alive for bat in self if bat.Unit.Name != 'General'])

    def has_speed_units(self, speed):
        return any(self[i].alive for i in np.where(self.Speeds == speed)[0])

    @property
    def defeated(self):
        return np.all([bat.dead for bat in self])

    def revive(self):
        for bat in self:
            bat.revive()

    def speed_batallions(self, speed):
        return filter(lambda x: x.Unit.Speed == speed, self.Batallions)

    def update_n_defeated(self):
        for bat in self:
            bat.update_n_defeated()

    def _attack(self, army: 'Army', speed):
        for bat in self.speed_batallions(speed):
            dmg = 1
            for i in army.IHP if speed == 2 else range(army.N):
                if not bat.can_attack or army[i].dead or dmg <= 0:
                    continue
                dmg = bat.attack(army[i])
            bat.NAttacks = 0
        self.HasAttacked[speed] = True
        if not army.HasAttacked[speed] and army.has_speed_units(speed):
            info('Enemy attacking!', color='red', prnt=Verbose)
            army._attack(self, speed)
        self.update_n_defeated()
        army.update_n_defeated()
        self.HasAttacked[speed] = False

    def attack(self, army: 'Army'):
        n = 0
        while not self.defeated and not army.defeated:
            if Verbose:
                print_banner(f'ROUND {n}', color='yellow')
            for speed in [2, 1, 0]:
                if self.has_speed_units(speed) or army.has_speed_units(speed):
                    if Verbose:
                        print_small_banner(f'{SpeedDict[speed]} units', color='yellow')
                    self._attack(army, speed)  # fast units
            n += 1
        if Verbose:
            print_banner(f'End after {n} round{"s" if n > 1 else ""}', color='red')
        return n


class OwnArmy(Army):
    Units = [Recruit, Militia, Soldier, Cavalry, Bowman, LongBowman, General]

    def __init__(self, recruits=0, militia=0, soldiers=0, cavalry=0, bowmen=0, longbowmen=0):
        super().__init__(recruits, militia, soldiers, cavalry, bowmen, longbowmen, 1)


class EnemyArmy(Army):
    Units = [Scavenger, Thug, GuardDog, Roughneck, Stonethrower, Ranger]

    def __init__(self, scavengers=0, thugs=0, guard_dogs=0, roughnecks=0, stonethrowers=0, ranger=0):
        super().__init__(scavengers, thugs, guard_dogs, roughnecks, stonethrowers, ranger)

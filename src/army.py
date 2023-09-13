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
        self.CurrentDmg = 1

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
        return self.NAttacks + self.NDefeated < self.N and self.CurrentDmg > 0

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
        self.CurrentDmg = 1

    def revive(self):
        for unit in self.Units:
            unit.revive()
        self.NAttacks = 0
        self.NDefeated = 0
        self.CurrentDmg = 1

    def normal_attack(self, battalion: 'Battalion'):
        for unit in self.Units[self.NAttacks + self.NDefeated:]:
            try:
                unit.attack(battalion.next)
                self.NAttacks += 1
            except StopIteration:
                break

    def splash_attack(self, battalion: 'Battalion'):
        for unit in self.Units[self.NAttacks + self.NDefeated:]:
            try:
                self.CurrentDmg = unit.dmg
                while self.CurrentDmg > 0:
                    enemy = battalion.next
                    self.CurrentDmg = unit.attack(enemy, self.CurrentDmg)  # returns remaining dmg
            except StopIteration:
                break

    def attack(self, battalion: 'Battalion'):
        if battalion is not None:
            n0, n1 = self.N - self.NAttacks - self.NDefeated, battalion.n_alive
            splash = np.random.random() < self.Unit.Splash if 0 < self.Unit.Splash < 1 else self.Unit.Splash
            self.splash_attack(battalion) if splash else self.normal_attack(battalion)
            info(f'{n0} {self.Unit.Name} killed {n1 - battalion.n_alive} {battalion.Unit.Name} ({battalion.alive_str})', prnt=Verbose)


class Army:
    Units = []

    def __init__(self, *n_units, max_units=200):

        self.Batallions = [Battalion(n, u) for n, u in zip(n_units, self.Units) if n]
        self.Speeds = np.array([bat.Unit.Speed for bat in self])
        self.N = len(self.Batallions)

        self.MaxUnits = max_units
        self.NUnits = self.init_n_units()  # total number of units
        self.IHP = self.hp_indices()  # indices sorted by HP

        self.NRounds = 0

    def __getitem__(self, item):
        return self.Batallions[item]

    def __add__(self, other):
        return self.add(other)

    def __str__(self):
        return self.__class__.__name__

    def __repr__(self):
        bat_str = '  '.join([f'{bat!r}' for bat in self.Batallions])
        return f'{self.__class__.__name__} with {self.NUnits} units:\n  {bat_str}'

    def init_n_units(self):
        n = sum(bat.N for bat in self if bat.Unit.Name != 'General')
        warning(f'{self} has too many units ({n}/{self.MaxUnits})', prnt=n > self.MaxUnits)
        return n

    def add(self, other: Battalion, pos=None):
        pos = choose(pos, self.N)
        self.Batallions.insert(pos, other)
        self.N += 1
        self.NUnits += other.N
        self.IHP = self.hp_indices()
        self.Speeds = np.insert(self.Speeds, pos, other.Unit.Speed)
        return self

    def hp_indices(self):
        hp = [bat.Unit.HP for bat in self]
        return np.append(np.argsort(hp[:-1]), self.N - 1) if self[-1].Unit.Name == 'General' else np.argsort(hp)

    @property
    def data(self):
        return np.append([bat.NDefeated for bat in self], self.NRounds)

    @property
    def size(self):
        return np.sum([bat.n_alive for bat in self if bat.Unit.Name != 'General'])

    def indices(self, speed):
        return [i for i in (self.IHP if speed == 2 else range(self.N)) if self[i].alive]

    def has_speed_units(self, speed):
        return any(self[i].alive for i in np.where(self.Speeds == speed)[0])

    @property
    def defeated(self):
        return np.all([bat.dead for bat in self])

    def revive(self):
        for bat in self:
            bat.revive()
        self.NRounds = 0

    def speed_batallions(self, speed):
        return filter(lambda x: x.Unit.Speed == speed, self.Batallions)

    def update_n_defeated(self):
        for bat in self:
            bat.update_n_defeated()

    def _attack(self, army: 'Army', speed):
        for bat in self.speed_batallions(speed):
            indices = iter(army.indices(speed))
            while bat.can_attack and not army.defeated:
                bat.attack(army[next(indices)])
            bat.NAttacks = 0

    def attack(self, army: 'Army'):
        while not self.defeated and not army.defeated:
            print_banner(f'ROUND {self.NRounds}', color='yellow', prnt=Verbose)
            for speed in [s for s in [2, 1, 0] if self.has_speed_units(s) or army.has_speed_units(s)]:
                print_small_banner(f'{SpeedDict[speed]} units', color='yellow', prnt=Verbose)
                self._attack(army, speed)  # bath attacks happen in parallel
                info('Enemy attacking!', color='red', blank_lines=1, prnt=Verbose)
                army._attack(self, speed)
                self.update_n_defeated()
                army.update_n_defeated()
            self.NRounds += 1
        loser = self if self.defeated else army
        print_banner(f'{loser} was defeated after {self.NRounds} round{"s" if self.NRounds > 1 else ""}', color='red', prnt=Verbose)


class OwnArmy(Army):
    Units = [Recruit, Militia, Soldier, Cavalry, Bowman, LongBowman, General]

    def __init__(self, recruits=0, militia=0, soldiers=0, cavalry=0, bowmen=0, longbowmen=0):
        super().__init__(recruits, militia, soldiers, cavalry, bowmen, longbowmen, 1)


class EnemyArmy(Army):
    Units = [Scavenger, Thug, GuardDog, Roughneck, Stonethrower, Ranger]

    def __init__(self, scavengers=0, thugs=0, guard_dogs=0, roughnecks=0, stonethrowers=0, ranger=0):
        super().__init__(scavengers, thugs, guard_dogs, roughnecks, stonethrowers, ranger)

    @property
    def data(self):
        return np.array([bat.NDefeated for bat in self])

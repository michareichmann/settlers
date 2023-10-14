from utils.helpers import *
from src.units import *
from src.battalion import Battalion

Verbose = False

SpeedDict = {0: 'Slow',
             1: 'Normal',
             2: 'Fast'}


def set_verbose(status=ON):
    global Verbose
    old_verbose = Verbose
    Verbose = status
    return old_verbose


class Army:
    Units = []

    def __init__(self, *n_units, max_units=200):

        self.Batallions = [Battalion(n, u) for n, u in zip(n_units, self.Units) if n]
        self.Speeds = np.array([bat.Unit.Speed for bat in self])
        self.N = len(self.Batallions)

        self.MaxUnits = max_units
        self.NUnits = self.init_n_units()  # total number of units
        self.IHP = self.hp_indices()  # indices sorted by HP

        self.ExcessDmg = 0
        self.NRounds = 0

    def __getitem__(self, item):
        return self.Batallions[item]

    def __iter__(self):
        return iter(self.Batallions)

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
        return np.append(np.argsort(hp[:-1]), self.N - 1) if self.N and self[-1].Unit.Name == 'General' else np.argsort(hp)

    @property
    def data(self):
        return np.append([bat.NDefeated for bat in self], self.NRounds)

    @property
    def size(self):
        return np.sum([bat.n_alive for bat in self if bat.Unit.Name != 'General'])

    def indices(self, flanking):
        return [i for i in (self.IHP if flanking else range(self.N)) if self[i].alive]

    def has_speed_units(self, speed):
        return any(self[i].alive for i in np.where(self.Speeds == speed)[0])

    @property
    def defeated(self):
        return np.all([bat.defeated for bat in self])

    @property
    def defeated_(self):
        return np.all([bat.defeated_ for bat in self])

    def revive(self):
        for bat in self:
            bat.revive()
        self.NRounds = 0

    def speed_batallions(self, speed):
        return filter(lambda x: x.Unit.Speed == speed, self.Batallions)

    def update_n_defeated(self):
        for bat in self:
            bat.update_n_defeated()

    def _attack(self, army: 'Army', speed, prnt=False):
        for bat in self.speed_batallions(speed):
            indices = iter(army.indices(bat.Unit.Flanking))
            while bat.can_attack and not army.defeated_:
                (bat.print_attack if prnt else bat._attack)(army[next(indices)])
            bat.NAttacks = 0

    def attack(self, army: 'Army', prnt=False):
        while not self.defeated and not army.defeated:
            print_banner(f'ROUND {self.NRounds}', color='yellow', prnt=Verbose)
            for speed in [s for s in [2, 1, 0] if self.has_speed_units(s) or army.has_speed_units(s)]:
                print_small_banner(f'{SpeedDict[speed]} units', color='yellow', prnt=Verbose)
                self._attack(army, speed, prnt)  # bath attacks happen in parallel
                info('Enemy attacking!', color='red', blank_lines=1, prnt=Verbose)
                army._attack(self, speed, prnt)
                self.update_n_defeated()
                army.update_n_defeated()
            self.NRounds += 1
        loser = self if self.defeated else army
        print_banner(f'{loser} was defeated after {self.NRounds} round{"s" if self.NRounds > 1 else ""}', color='red', prnt=Verbose)


class OwnArmy(Army):
    Units = [Recruit, Militia, Soldier, Cavalry, Bowman, Longbowman, Crossbowman, General]

    def __init__(self, recruits=0, militia=0, soldiers=0, cavalry=0, bowmen=0, longbowmen=0, crossbowmen=0, general=1):
        super().__init__(recruits, militia, soldiers, cavalry, bowmen, longbowmen, crossbowmen, general)


class EnemyArmy(Army):
    Units = [Scavenger, Thug, GuardDog, Roughneck, Stonethrower, Ranger]

    def __init__(self, scavengers=0, thugs=0, guard_dogs=0, roughnecks=0, stonethrowers=0, ranger=0):
        super().__init__(scavengers, thugs, guard_dogs, roughnecks, stonethrowers, ranger)

    @property
    def data(self):
        return np.array([bat.NDefeated for bat in self])


class DeserterArmy(Army):
    Units = deepcopy([Recruit, Militia, Cavalry, Soldier, EliteSoldier, Bowman, Longbowman, Cannoneer])
    Accuracy = [.6, .6, .6, .65, .7, .6, .6, .7]

    def __init__(self, recruits=0, militia=0, cavalry=0, soldiers=0, elite_soldiers=0, bowmen=0, longbowmen=0, cannoneers=0):

        self.set_accuracies()
        super().__init__(recruits, militia, cavalry, soldiers, elite_soldiers, bowmen, longbowmen, cannoneers)

    def set_accuracies(self):
        for i, acc in enumerate(self.Accuracy):
            self.Units[i].set_accuracy(acc)

    @property
    def data(self):
        return np.array([bat.NDefeated for bat in self])

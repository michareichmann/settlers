from utils.helpers import choose
import numpy.random as rnd


class Unit:

    def __init__(self, name, hp, dmg_min, dmg_max, accuracy, speed, splash=None):
        self.Name = name
        self.HP = hp
        self.DmgMin = dmg_min
        self.DmgMax = dmg_max
        self.Accuracy = accuracy
        self.Speed = speed
        self.Splash = choose(splash, 1 if speed == 0 else 0)

        self.CurrentHP = hp
        self.Hits = 0
        self.Dead = False

    def __repr__(self):
        return (f'{self.Name} unit\n'
                f'  HP: {self.CurrentHP}/{self.HP} {f"({self.Hits} Hits)" if self.Hits else ""}\n'
                f'  Damage: {self.DmgMin}-{self.DmgMax}\n'
                f'  Accuracy: {self.Accuracy:.0%}\n'
                f'  Dead: {self.Dead}')

    @property
    def dmg(self):
        return self.DmgMax if rnd.random() < self.Accuracy else self.DmgMin

    def kill(self):
        self.CurrentHP = 0
        self.Hits += 1
        self.Dead = True

    def revive(self):
        self.CurrentHP = self.HP
        self.Dead = False
        self.Hits = 0

    def attack(self, unit: 'Unit', dmg=None):
        unit.CurrentHP -= choose(dmg, self.dmg)
        unit.Dead = unit.CurrentHP <= 0
        unit.Hits += 1
        return -unit.CurrentHP  # remaining dmg


# Own Units
Recruit = Unit('Recruit', 40, 15, 30, .8, 1)
Militia = Unit('Militia', 60, 20, 40, .8, 1)
Soldier = Unit('Soldier', 90, 20, 40, .85, 1)
Bowman = Unit('Bowman', 10, 20, 40, .8, 1)
LongBowman = Unit('LongBowman', 10, 30, 60, .8, 1)
Cavalry = Unit('Cavalry', 5, 5, 10, .8, 2)
General = Unit('General', 1, 180, 180, .8, 1, splash=1)

# Enemy Units
Scavenger = Unit('Scavenger', 40, 15, 30, .6, 1)
Thug = Unit('Thug', 60, 20, 40, .6, 1)
Roughneck = Unit('Roughneck', 90, 20, 40, .6, 1)
Stonethrower = Unit('Stonethrower', 10, 20, 40, .6, 1)
Ranger = Unit('Ranger', 10, 30, 60, .6, 1)
GuardDog = Unit('Guard Dog', 5, 5, 10, .6, 2)

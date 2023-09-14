from src.army import Battalion, Unit, Army


class Boss(Battalion):

    def __init__(self,  name: str, hp, dmg_min, dmg_max, accuracy=.5, speed=0):
        super().__init__(1, Unit(name, hp, dmg_min, dmg_max, accuracy, speed))

        self.Name = name
        self.Unit = self[0]

    def __repr__(self):
        return f'Boss {self.Name} ({self.alive_str})\n'

    def __add__(self, other: Army):
        return other.add(self, pos=0)

    @property
    def alive_str(self):
        return f'{self.Unit.CurrentHP}/{self.Unit.HP} HP'


Skunk = Boss('Skunk', 5000, 1, 100, .5, 0)
OneEyedBert = Boss('One-Eyed Bert', 6000, 300, 500, .5, 0)
MetalTooth = Boss('Metal Tooth', 11000, 250, 500, .5, 0)
Chuck = Boss('Chuck', 9000, 2000, 2500, .5, 0)

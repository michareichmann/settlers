from src.army import *
from src.boss import *
from plotting.save import SaveDraw, hist_xy
from utils.classes import PBAR


d = SaveDraw()


# me = OwnArmy(80, 11, 0, 0, 50, 59)
# me = OwnArmy(150, 0, 0, 10, 50, 0)
me = OwnArmy(111, 0, 0, 0, 0, 89)
# enemy = EnemyArmy(0, 180, 20, 0, 0)
# enemy = EnemyArmy(0, 180, 20, 0, 149) + MetalTooth
enemy = EnemyArmy(15, 0, 0, 0, 0)


def sim(n=100, r=False, show=True):
    PBAR.start(n)
    losses = []
    rounds = []
    for _ in range(n):
        me.revive()
        enemy.revive()
        rounds.append(me.attack(enemy))
        losses.append(me[0].NDefeated)
        PBAR.update()
    a = None
    if np.any(losses):
        a = d.distribution(np.array(losses), w=1, q=.002, rf=1, lf=1, normalise=True, gridy=True, show=show and not r, x_tit=f'Lost {me[0].Unit.Name}s')
        info(f'{me[0].Unit.Name} losses: ')
        for x, y in zip(*hist_xy(a, raw=True)):
            if y > 0.005:
                print(f'  {x:.0f}: {y:4.1%}')
    else:
        info('No losses :-)')
    b = d.distribution(np.array(rounds), w=1, q=.002, rf=1, lf=1, normalise=True, gridy=True, show=show and r, x_tit='Number of Rounds')
    info(f'Number of Rounds: ')
    for x, y in zip(*hist_xy(b, raw=True)):
        if y > 0.005:
            print(f'  {x:.0f}: {y:4.1%}')
    return b if r else a


def print_attack():
    old_verbose = set_verbose(ON)
    me.revive()
    enemy.revive()
    me.attack(enemy)
    set_verbose(old_verbose)


if __name__ == '__main__':
    pass

from src.army import *
from src.boss import *
from plotting.save import SaveDraw, hist_xy
from utils.classes import PBAR


d = SaveDraw()

recruits = OwnArmy(150)


# me = OwnArmy(80, 11, 0, 0, 50, 59)
me = OwnArmy(40, 0, 0, 50, 0, 110)
# enemy = EnemyArmy(0, 180, 20, 0, 0)
enemy = EnemyArmy(0, 0, 0, 50, 0, 149) + MetalTooth


def sim(*armies, n=1000, r=False, show=True):
    losses = []
    rounds = []
    armies = armies if len(armies) else [me]
    PBAR.start(n * len(armies))
    for _ in range(n):
        enemy.revive()
        for army in armies:
            army.revive()
            army.attack(enemy)
            PBAR.update()
        rounds.append(armies[-1].NRounds)
        losses.append(sum(army[0].NDefeated for army in armies))
    a = None
    if np.any(losses):
        a = d.distribution(np.array(losses), w=1, q=.002, rf=1, lf=1, normalise=True, gridy=True, show=show and not r, x_tit=f'Lost {armies[-1][0].Unit.Name}s')
        info(f'{armies[-1][0].Unit.Name} losses: ')
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


def print_attack(*armies):
    old_verbose = set_verbose(ON)
    armies = armies if len(armies) else [me]
    enemy.revive()
    for army in armies:
        army.revive()
        army.attack(enemy)
    set_verbose(old_verbose)


if __name__ == '__main__':
    pass

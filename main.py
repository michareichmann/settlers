from src.army import *
from src.boss import *
from plotting.save import SaveDraw, hist_xy, mean_sigma
# from utils.classes import PBAR
from functools import partial
from src.mine import *


# TODO: add mine timer
# TODO: add gui
# TODO: add fixed General in Own Army
# 32772

d = SaveDraw()

recruits = OwnArmy(200)
bm = OwnArmy(bowmen=200)
lb = OwnArmy(longbowmen=200)

me = OwnArmy(1, 0, 0, 165, 0, 0)
# enemy = EnemyArmy(0, 150, 30, 0, 0, 20)  # camp 1
# enemy = EnemyArmy(0, 0, 0, 0, 0, 129)
enemy = Chuck + EnemyArmy(0, 0, 50, 100, 0, 49)


def _sim_1r(attacker: Battalion, defender: Battalion):
    defender.revive()
    attacker.attack(defender)
    return defender.N - defender.n_alive


def sim_1r(attacker: Battalion, defender: Battalion, n=1000):
    return np.array(parallelise(_sim_1r, [[attacker, defender]] * n))


def show_1r(attacker: Battalion = None, defender: Battalion = None, n=1000):
    x, y = choose(attacker, me[0]), choose(defender, enemy[0])
    return d.distribution(sim_1r(x, y, n), w=1, q=.002, rf=1, lf=1, normalise=True, gridy=True, x_tit=f'Lost {y.Unit.Name}s')


def _sim(*armies):
    enemy.revive()
    for army in armies:
        army.revive()
        army.attack(enemy)
    return np.append(np.concatenate([army.data for army in armies]), enemy.data)


def sim(*armies, n=1000):
    f = partial(_sim, *armies)
    return np.array(parallelise(f, [[]] * n))


def minimise(i_unit=0, xmin=20, xmax=100, s=1, n=100):
    x = np.arange(xmin, xmax, s)
    y = np.array([[mean_sigma(x)[0] for x in sim(OwnArmy(1, cavalry=i, soldiers=1), n=n).T] for i in x]).T
    y = np.sum(y[i_unit], axis=0) if is_iter(i_unit) else y[i_unit]
    return d.graph(x, y)


def show(*armies, i=0, n=1000):
    armies = armies if len(armies) else [me]
    data = sim(*armies, n=n).T
    a = data[i]
    if np.any(a):
        a = d.distribution(np.array(a), w=1, q=.002, rf=1, lf=1, normalise=True, gridy=True, x_tit=f'Lost {armies[-1][0].Unit.Name}s')
        info(f'{armies[-1][0].Unit.Name} losses: ')
        for x, y in zip(*hist_xy(a, raw=True)):
            if y > 0.005:
                print(f'  {x:.0f}: {y:4.1%}')
    else:
        info('No losses :-)')
    i_last_rnd = sum(army.N + 1 for army in armies) - 1
    b = d.distribution(np.array(data[i_last_rnd]), w=1, q=.002, rf=1, lf=1, normalise=True, gridy=True, show=False, x_tit='Number of Rounds')
    info(f'Number of Rounds: ')
    for x, y in zip(*hist_xy(b, raw=True)):
        if y > 0.005:
            print(f'  {x:.0f}: {y:4.1%}')


def print_attack(*armies):
    old_verbose = set_verbose(ON)
    armies = armies if len(armies) else [me]
    enemy.revive()
    for army in armies:
        army.revive()
        army.attack(enemy)
    set_verbose(old_verbose)


pa = print_attack
m = minimise


if __name__ == '__main__':
    cm = CoalMine(8814, 16, lvl=2)
    im = IronMine(3636, 32, lvl=3)

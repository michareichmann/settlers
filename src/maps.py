#!/usr/bin/env python

import re
from copy import deepcopy
from pathlib import Path
from xml.etree import ElementTree

import numpy as np

from utils.helpers import isint, remove_letters, remove_digits, print_table, choose

UnitDict = {u: [] for u in ['R', 'M', 'S', 'ES', 'C', 'B', 'L', 'CB']}


class Attack(list):

    ColorKilled = '#800000'
    ColorUnits = '#000000'
    MaxUnits = 215

    def __init__(self, number: int, *e: ElementTree.Element):
        super().__init__(list(e))
        self.Number = number

    def __lt__(self, other: 'Attack'):
        return self.Number < other.Number

    @property
    def words(self):
        return [e[0].text.strip() for e in self]

    def prepare_words(self, killed=False):
        color = Attack.ColorKilled if killed else Attack.ColorUnits
        words = [e[0].text.strip() for e in self if len(self) and f'fill:{color}' in e.get('style') and 'bold' not in e.get('style') and 'bold' not in e[0].get('style')]
        return [word.split(',') for word in words]

    @property
    def lost_units(self):
        u = deepcopy(UnitDict)
        for lst in self.prepare_words(killed=True):
            for arr in [re.split('-|\(|\)|\⟨|\⟩', word) if '-' in word else [word[:-1]] * 3 + [word[-1]] for word in lst]:  # noqa
                u[arr[-1]].append(arr[:-1])
        return {key: np.sum(np.array(value, 'i'), axis=0) for key, value in u.items() if len(value)}

    @staticmethod
    def remove_times(*words):
        ps = [w.find('(') for w in words]
        return [(w if pos == -1 else w[w.find(')') + 1:] if pos < 2 else w[:pos]).strip() for w, pos in zip(words, ps)]

    @property
    def units(self):
        units = {key: 0 for key in UnitDict}
        for lst in self.prepare_words():
            lst = self.remove_times(*lst)
            total_units = sum(int(remove_letters(word)) for word in lst if remove_letters(word))
            for word in lst:
                unit, n = remove_digits(word).strip(), remove_letters(word)
                units[unit] += int(n) if isint(n) else Attack.MaxUnits - total_units
        return {key: val for key, val in units.items() if val > 0}


class MapAttacks(list):

    Dir = Path(__file__).resolve().parent.parent.joinpath('maps')

    def __init__(self, file_name: str):
        super().__init__()
        self.Root = ElementTree.parse(MapAttacks.Dir.joinpath(file_name)).getroot()
        self.Groups = self.find_groups()
        self.find()

    def __repr__(self):
        return f'Tactic Map with {len(self)} attacks'

    def find_groups(self):
        return [list(el.iter('{http://www.w3.org/2000/svg}text')) for el in self.Root[-1] if 'text' not in el.tag]

    def find(self):
        for i, nr in enumerate([int(remove_letters(e[0].text)) for group in self.Groups for e in group if 'bold' in e.get('style') or 'bold' in e[0].get('style')]):  # attack numbers
            self.add(nr, *self.Groups[i])

    @property
    def numbers(self):
        return [att.Number for att in self]

    def lost_units(self, start=0, end=None):
        u = {key: np.zeros(3, 'i') for key in UnitDict}
        for att in self[start:choose(end, len(self))]:
            for key, value in att.lost_units.items():
                u[key] += value
        return {key: value for key, value in u.items() if value[-1] > 0}

    def required_units(self, start=0, end=None):
        u = {key: [] for key in UnitDict}
        for att in self[start:choose(end, len(self))]:
            for key, value in att.units.items():
                u[key].append(value)
        for key, arr in self.lost_units(start, end).items():
            u[key].append(arr[1])  # maximum losses
        return {key: max(lst) for key, lst in u.items() if lst}

    def print_packlist(self):
        ru, lu = self.required_units(), self.lost_units()
        rows = []
        for key, value in ru.items():
            rows.append([f'{value}{key}', '[{}-{} ⟨{}⟩]'.format(*lu[key]) if key in lu else ''])
        footer = [sum(ru.values()), '[{}-{} ⟨{}⟩]'.format(*np.sum(list(lu.values()), axis=0))]
        print_table(rows, form='rr', header=['Packlist', 'Losses'], footer=footer)

    def add(self, nr: int, *e):
        nrs = self.numbers
        if nr in nrs:
            self[nrs.index(nr)] += list(e)
        else:
            self.append(Attack(nr, *e))
            self.sort()


if __name__ == '__main__':

    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('file', type=str)
    args = parser.parse_args()

    m = MapAttacks(args.file)
    m.print_packlist()

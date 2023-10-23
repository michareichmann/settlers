from PyQt5.QtWidgets import QGridLayout, QInputDialog

from gui.group_box import GroupBox
from gui.utils import *
from src.mine import Mines, Mine
from utils.classes import Config
from utils.helpers import Dir


class MineBox(GroupBox):

    Config = Config(Dir.joinpath('config', 'mines.ini'))
    Header = ['P', 'Lvl', 'N', 'Time Left', 'Status']
    Status = ['ON', 'OFF']
    FigPath = Dir.joinpath('figures')
    Height = 22

    def __init__(self, cls):

        self.MineCls = cls
        self.Title = f'{cls.Resource} Mines'

        self.DefaultValues = self.load_default(cls)
        self.Mines = self.load_mines()
        super().__init__()

        self.Speed = check_box()
        self.Layout = self.create_layout()
        self.create_widgets()

    def __getitem__(self, item):
        return self.Mines[item]

    def update(self):
        self.Mines.update()
        self.setTitle(f'{self.Title}  ({self.Mines.current_production}*/hr)')
        for mine, row in zip(self.Mines, self.Labels):
            for lbl, txt in zip(row[1:], mine.data):
                lbl[0].setText(str(txt))
            self.format(mine)

    def format(self, mine: Mine):
        color, bold = ('white', True) if mine.destroyed else ('red', False)
        for lbl in self.Labels[self.index(mine)]:
            format_widget(lbl, color=color, bold=bold)

    @staticmethod
    def load_default(cls: Mine):
        MineBox.Config.set_section(str(cls.Resource))
        t = MineBox.Config.get_value('extra time')
        d = MineBox.Config.get_value('deposit')
        d = ([int(d)] * len(t)) if type(d) is str else d
        lvl = MineBox.Config.get_value('level', default=1)
        return [(i, j, lvl) for i, j in zip(d, t)]

    def reset(self, mine: Mine):
        i = self.index(mine)
        mine.set_lvl(self.DefaultValues[i][2])
        mine.set_deposit(self.DefaultValues[i][0])
        mine.set_double_speed(self.Speed.isChecked())
        mine.reset_warnings()
        self.Speed.setChecked(False)

    def load_mines(self):
        mines = Mines(self.MineCls.__name__)
        if not mines.FileName.exists():
            for v in self.DefaultValues:
                mines + self.MineCls(*v)
        for i, mine in enumerate(mines):
            mine.set_position(i)
        return mines

    @property
    def range(self):
        return range(self.Mines.size)

    def adjust_height(self):
        self.setFixedHeight(self.Height * (self.Mines.size + 2))

    def configure(self):
        super().configure()
        self.adjust_height()

    def index(self, mine: Mine):
        return self.Mines.L.index(mine)

    def pop_widgets(self, mine: Mine = None):
        i = -1 if mine is None else self.index(mine)
        return sum([con.pop(i) for con in self.used_containers], start=[])

    def set_deposit(self, mine):
        value, ok = QInputDialog().getInt(self, 'Change Deposit', 'Value:', QLineEdit.Normal)
        if ok and value:
            mine.set_deposit(value)
            mine.set_double_speed(self.Speed.isChecked())
            self.Speed.setChecked(False)

    # ----------------------------------
    # region LAYOUT & WIDGETS
    def create_layout(self) -> QGridLayout:
        self.setLayout(QGridLayout(self))
        self.layout().setContentsMargins(4, 4, 4, 4)
        return self.layout()  # noqa

    def create_widgets(self):
        self.create_header()
        self.create_labels()
        self.create_buttons()

    def create_header(self):
        for i, name in enumerate(MineBox.Header):
            self.Layout.addWidget(label(name, bold=True), 0, i, CEN)
        i = len(self.Header)
        self.Layout.addWidget(label('2x speed:'), 0, i, 1, 2, RIGHT)
        self.Layout.addWidget(self.Speed, 0, i + 2, LEFT)

    def create_labels(self):
        align = [CEN, CEN, RIGHT, RIGHT, CEN]
        pos = range(4)
        for i, mine in enumerate(self.Mines, 1):
            self.Labels.append([label(txt, align=align[j], xpos=pos[j]) for j, txt in enumerate([i] + mine.data)])
            for lbl in self.Labels[-1]:
                self.Layout.addWidget(lbl, i, lbl.XPos, lbl.Align)

    def create_buttons(self):
        pos = range(4, 8)
        for i, mine in enumerate(self.Mines, 1):
            self.Buttons.append([OnOffButton(mine.change_status, mine.Paused, self.FigPath.joinpath('on.svg'), self.FigPath.joinpath('off.svg'), align=CEN, xpos=pos[0]),
                                 SvgButton(mine.upgrade, self.FigPath.joinpath('upgrade.svg'), xpos=pos[1]),
                                 button('Set', partial(self.set_deposit, mine), size=40, height=16, align=CEN, xpos=pos[2]),
                                 SvgButton(partial(self.reset, mine), Dir.joinpath('figures', 'reload.svg'), xpos=pos[3])])
            for w in self.Buttons[-1]:
                self.Layout.addWidget(w, i, w.XPos, w.Align)

    def insert_mine(self, i: int, mine: Mine):
        mine.set_double_speed(self.Speed.isChecked())
        self.Mines.insert(i, mine)
        self.DefaultValues = self.load_default(self.MineCls)
        self.remove_widgets()
        self.create_widgets()
        self.adjust_height()

    # endregion
    # ----------------------------------

from PyQt5.QtWidgets import QGridLayout

from gui.group_box import GroupBox
from gui.utils import *
from src.mine import Mines, Mine
from utils.classes import Config
from utils.helpers import Dir, is_iter


class MineBox(GroupBox):

    Config = Config(Dir.joinpath('config', 'mines.ini'))
    Header = ['P', 'Lvl', 'N', 'Time Left', 'Status']
    Status = ['ON', 'OFF']
    FigPath = Dir.joinpath('figures')

    def __init__(self, cls):

        self.MineCls = cls
        self.Title = f'{cls.Resource} Mines'

        self.DefaultValues = self.load_default()
        self.Mines = self.load_mines()
        super().__init__()

        self.Layout = self.create_layout()
        self.create_header()
        self.create_labels()
        self.create_buttons()

    def __getitem__(self, item):
        return self.Mines[item]

    def update(self):
        self.Mines.update()
        for mine, row in zip(self.Mines, self.Labels):
            for lbl, txt in zip(row[1:], mine.data):
                lbl[0].setText(str(txt))

    def load_default(self):
        MineBox.Config.set_section(str(self.MineCls.Resource))
        t = MineBox.Config.get_value('extra time')
        d = MineBox.Config.get_value('deposit')
        d = d if is_iter(int(d)) else ([int(d)] * len(t))
        lvl = MineBox.Config.get_value('level', default=1)
        return [(i, j, lvl) for i, j in zip(d, t)]

    def reload(self, mine: Mine):
        i = self.index(mine)
        mine.set_lvl(self.DefaultValues[i][2])
        mine.set_deposit(self.DefaultValues[i][0])

    def load_mines(self):
        m = Mines(self.MineCls.__name__)
        if not m.FileName.exists():
            for v in self.DefaultValues:
                m + self.MineCls(*v)
        return m

    @property
    def range(self):
        return range(self.Mines.size)

    def adjust_height(self):
        self.setFixedHeight(self.Height * (self.Mines.size + 1))

    def configure(self):
        super().configure()
        self.adjust_height()

    def index(self, mine: Mine):
        return self.Mines.L.index(mine)

    def pop_widgets(self, mine: Mine = None):
        i = -1 if mine is None else self.index(mine)
        return sum([con.pop(i) for con in self.used_containers], start=[])

    # ----------------------------------
    # region LAYOUT & WIDGETS
    def create_layout(self) -> QGridLayout:
        self.setLayout(QGridLayout(self))
        self.layout().setContentsMargins(4, 4, 4, 4)
        return self.layout()  # noqa

    def create_header(self):
        for i, name in enumerate(MineBox.Header):
            self.Layout.addWidget(label(name, bold=True), 0, i, CEN)

    def create_labels(self):
        align = [CEN, CEN, RIGHT, RIGHT, CEN]
        pos = range(4)
        for i, mine in enumerate(self.Mines, 1):
            self.Labels.append([label(txt, align=align[j], xpos=pos[j]) for j, txt in enumerate([i] + mine.data)])
            for lbl in self.Labels[-1]:
                self.Layout.addWidget(lbl, i, lbl.XPos, lbl.Align)

    def create_buttons(self):
        pos = [4, 5, 6]
        for i, mine in enumerate(self.Mines, 1):
            self.Buttons.append([OnOffButton(mine.change_status, mine.Paused, self.FigPath.joinpath('on.png'), self.FigPath.joinpath('off.png'), align=CEN, xpos=pos[0]),
                                 PicButton(mine.upgrade, self.FigPath.joinpath('upgrade.png'), align=CEN, xpos=pos[1]),
                                 PicButton(partial(self.reload, mine), Dir.joinpath('figures', 'reload.png'), align=CEN, xpos=pos[2])])
            for w in self.Buttons[-1]:
                self.Layout.addWidget(w, i, w.XPos, w.Align)

    # endregion
    # ----------------------------------

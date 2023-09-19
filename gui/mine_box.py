from PyQt5.QtWidgets import QGridLayout
from functools import partial

from gui.group_box import GroupBox
from gui.utils import *
from src.mine import Mines, Mine
from utils.helpers import Dir


class _MineBox(GroupBox):

    def __init__(self, mines: Mines):

        self.Mines = mines
        super().__init__()

    def __getitem__(self, item):
        return self.Mines[item]

    @property
    def range(self):
        return range(self.Mines.size)

    @property
    def _layout(self) -> QGridLayout:
        return self.layout()  # noqa

    def adjust_height(self):
        self.setFixedHeight(self.Height * (self.Mines.size + 1))

    def configure(self):
        super().configure()
        self.adjust_height()

    def index(self, mine: Mine):
        return self.Mines.L.index(mine)

    def _remove_mine(self):
        """ remove last mine row from the layout """
        n_rows = self._layout.rowCount()
        for col in range(self._layout.columnCount()):
            self._layout.removeItem(self._layout.itemAtPosition(n_rows - 1, col))
        self.adjust_height()


class MineBox(_MineBox):

    Header = ['Type', 'Level', 'Deposit', 'Time Left', 'Status']
    Status = ['ON', 'OFF']
    Title = 'Mines'

    def __init__(self, mines: Mines):

        super().__init__(mines)
        self.Pos = list(range(5))
        self.Labels = self.create_label()

        self.make()

    def update(self):
        self.Mines.update()
        if self.Mines.size < len(self.Labels):
            self._remove_mine()
        for mine, row in zip(self.Mines.L, self.Labels):
            for lbl, txt in zip(row, mine.data):
                lbl[0].setText(str(txt))

    def create_label(self):
        align = [RIGHT, CEN, CEN, RIGHT, CEN]
        return [[[label(txt), self.Pos[i], align[i]] for i, txt in enumerate(mine.data)] for mine in self]

    def add_mine(self, mine):
        self.Mines + mine
        self.Labels = self.create_label()
        self.make()

    def make(self):
        layout = QGridLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        for i, name in enumerate(MineBox.Header):
            layout.addWidget(label(name, bold=True), 0, i, Qt.AlignCenter)

        for i in self.range:
            for lbl, il, al in self.Labels[i]:
                layout.addWidget(lbl, i + 1, il, al)

        # for widget in self.children():
        #     try:
        #         format_widget(widget, font='ubuntu', color='grey', font_size=FontSize, bold=False)
        #     except AttributeError:  # catch the widgets that can't be formatted by a stylesheet
        #         pass
        #     except Exception as err:
        #         print(err, type(err))
        #         pass
        self.setLayout(layout)


class ControlBox(_MineBox):

    Title = 'Controls'
    ButtonPos = [0, 1, 3, 4]
    InputPos = [2]

    def __init__(self, mines: Mines):

        super().__init__(mines)
        self.Buttons, self.LineEdits = [], []
        self.create_widgets()
        self.make()

    def delete_mine(self, mine):
        self.Mines.remove(self.index(mine))
        self._remove_mine()

    def _add_mine(self, mine: Mine):
        self.Buttons.append([PicButton(mine.upgrade, Dir.joinpath('figures', 'upgrade.png'), align=CEN, xpos=self.ButtonPos[0]),
                             button('Add', partial(self.add_deposit, mine), align=CEN, xpos=self.ButtonPos[1]),
                             button(['Pause', 'Activate'][mine.Paused], partial(self.set_status, mine), size=55, align=CEN, xpos=self.ButtonPos[2]),
                             PicButton(partial(self.delete_mine, mine), Dir.joinpath('figures', 'delete.png'), align=CEN, xpos=self.ButtonPos[3])])
        self.LineEdits.append([line_edit(1, align=CEN, xpos=self.InputPos[0])])

    def create_widgets(self):
        for mine in self:
            self._add_mine(mine)

    def add_deposit(self, mine: Mine):
        mine.add_deposit(int(self.LineEdits[self.Mines.L.index(mine)][0].text()))

    def set_status(self, mine: Mine):
        if hasattr(self, 'Buttons'):
            self.Buttons[self.index(mine)][-1].setText(['Activate', 'Pause'][mine.Paused])
        mine.change_status()

    def make(self):
        layout = QGridLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        layout.addWidget(label('Actions', bold=True), 0, 0, 1, 4, CEN)

        for widgets in [self.Buttons, self.LineEdits]:
            for i, lst in enumerate(widgets, 1):
                for w in lst:
                    layout.addWidget(w, i, w.XPos, w.Align)

        self.setLayout(layout)

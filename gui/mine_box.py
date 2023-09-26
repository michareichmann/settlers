from functools import partial

import numpy as np
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QGridLayout, QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLayout

from gui.group_box import GroupBox
from gui.utils import *
from src.mine import Mines, Mine, mine_from_str, mine_classes
from utils.helpers import Dir, warning


class _MineBox(GroupBox):

    def __init__(self, mines: Mines):

        self.Mines = mines
        super().__init__()

        self.Layout = self.create_layout()
        self.create_header()
        self.create_widgets()

    def __getitem__(self, item):
        return self.Mines[item]

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
        self.Layout.addWidget(label('Default', bold=True), 0, 0, CEN)

    def create_widgets(self):
        for mine in self:
            self._add_mine(mine)

    def reload_widgets(self):
        self.remove_widgets()
        self.create_widgets()

    def remove_widgets(self):
        for _ in self.range:
            self._remove_mine()

    def _add_mine(self, mine: Mine):
        pass

    def _remove_mine(self, mine: Mine = None):
        """ remove last mine row from the layout """
        for w in self.pop_widgets(mine):
            self.layout().removeWidget(w)
        self.adjust_height()
    # endregion
    # ----------------------------------

    def make(self):
        pass
        # for widget in self.children():
        #     try:
        #         format_widget(widget, font='ubuntu', color='grey', font_size=FontSize, bold=False)
        #     except AttributeError:  # catch the widgets that can't be formatted by a stylesheet
        #         pass
        #     except Exception as err:
        #         print(err, type(err))
        #         pass


class MineBox(_MineBox):

    Header = ['Type', 'Level', 'Deposit', 'Time Left', 'Status']
    Status = ['ON', 'OFF']
    Title = 'Mines'
    Pos = list(range(5))

    def create_header(self):
        for i, name in enumerate(MineBox.Header):
            self.Layout.addWidget(label(name, bold=True), 0, i, CEN)

    def update(self):
        self.Mines.update()
        if self.Mines.size < len(self.Labels):
            self._remove_mine()
        if self.Mines.size > len(self.Labels):
            self._add_mine(self[-1])
            self.adjust_height()
        for mine, row in zip(self.Mines.L, self.Labels):
            for lbl, txt in zip(row, mine.data):
                lbl[0].setText(str(txt))

    def _add_mine(self, mine: Mine):
        align = [RIGHT, CEN, CEN, RIGHT, CEN]
        self.Labels.append([label(txt, align=align[i], xpos=self.Pos[i]) for i, txt in enumerate(mine.data)])
        for lbl in self.Labels[-1]:
            self.Layout.addWidget(lbl, len(self.Labels) + 1, lbl.XPos, lbl.Align)


class ControlBox(_MineBox):

    Title = 'Controls'
    ButtonPos = [0, 1, 3, 4]
    InputPos = [2]

    def create_header(self):
        self.Layout.addWidget(label('Action', bold=True), 0, 0, 1, 4, CEN)

    def delete_mine(self, mine):
        self._remove_mine(mine)
        self.Mines.remove(self.index(mine))
        self.adjust_height()

    def add_mine(self, mine):
        self.Mines + mine
        self.reload_widgets()

    def _add_mine(self, mine: Mine):
        self.Buttons.append([PicButton(mine.upgrade, Dir.joinpath('figures', 'upgrade.png'), align=CEN, xpos=self.ButtonPos[0]),
                             button('Add', partial(self.add_deposit, mine), align=CEN, xpos=self.ButtonPos[1]),
                             button(['Pause', 'Activate'][mine.Paused], partial(self.set_status, mine), size=55, align=CEN, xpos=self.ButtonPos[2]),
                             PicButton(partial(self.delete_mine, mine), Dir.joinpath('figures', 'delete.png'), align=CEN, xpos=self.ButtonPos[3])])
        self.LineEdits.append([line_edit(500, align=CEN, xpos=self.InputPos[0])])
        for w in self.Buttons[-1] + self.LineEdits[-1]:
            self.Layout.addWidget(w, len(self.Buttons) + 1, w.XPos, w.Align)

    def add_deposit(self, mine: Mine):
        mine.add_deposit(int(self.LineEdits[self.Mines.L.index(mine)][0].text()))

    def set_status(self, mine: Mine):
        if hasattr(self, 'Buttons'):
            self.Buttons[self.index(mine)][-2].setText(['Activate', 'Pause'][mine.Paused])
        mine.change_status()


# todo: play sound when mine is going down

class MineDialogue(QDialog):

    FigPath = Dir.joinpath('figures')

    def __init__(self, control_box: ControlBox):
        super().__init__()

        self.setWindowTitle('Add Mine')

        self.ControlBox = control_box

        # Mine figures for selection
        self.PicLayout = self.create_pic_layout()
        self.Mines = [cls(0, 0) for cls in mine_classes()]

        # Value selection
        self.ValueLayout = self.create_value_layout()

        self.Layout = self.create_layout()

    @staticmethod
    def get_widgets(layout: QLayout):
        return np.array([layout.itemAt(i).widget() for i in range(layout.count())])

    @property
    def values(self):
        w = self.get_widgets(self.ValueLayout)[1::2]  # there is always a pair of label and widget
        return w[1].text(), int(w[0].text()), w[2].text(), w[3].isChecked(), [1, 2][w[4].isChecked()]  # noqa

    def set_default_values(self, mine):
        ws = self.get_widgets(self.ValueLayout)
        ws[3].setText(str(mine.DefaultDeposit))
        ws[5].setText(str(mine.DefaultLevel))

    def select_mine(self, i):
        buttons = self.get_widgets(self.PicLayout)
        for but in buttons:
            but.set_clicked(False)
        buttons[i].set_clicked(True)
        self.set_default_values(self.Mines[i])

    def confirm(self):
        for w in self.get_widgets(self.PicLayout):
            if w.Clicked:
                self.ControlBox.add_mine(mine_from_str(w.PicName, *self.values))
                self.done(QDialog.Accepted)
        warning('No mine was selected')

    def run(self):
        self.move(QCursor.pos())
        if self.exec() == QDialog.Accepted:
            return

    # ----------------------------------------
    # region LAYOUT
    def create_pic_layout(self):
        layout = QHBoxLayout()
        for but in [PicButOpacity(partial(self.select_mine, i), pic) for i, pic in enumerate([MineDialogue.FigPath.joinpath(f'{m}-mine.png') for m in ['cop', 'iro', 'coa', 'gol']])]:
            layout.addWidget(but, alignment=CEN)
        return layout

    @staticmethod
    def create_value_layout():
        layout = QFormLayout()
        layout.setFormAlignment(CEN | Qt.AlignTop)
        layout.setLabelAlignment(RIGHT)

        labels = ['Extra Time [s]:', 'Deposit:', 'Level:', 'Paused:', 'Double speed:']
        widgets = [line_edit(16, 50), line_edit(500, 50), line_edit(1, 50), check_box(), check_box()]
        for lbl, w in zip(labels, widgets):
            layout.addRow(lbl, w)
        return layout

    def create_layout(self):
        layout = QVBoxLayout()
        layout.addLayout(self.PicLayout)
        layout.addLayout(self.ValueLayout)
        layout.addWidget(button('Confirm', self.confirm))
        self.setLayout(layout)
        return layout
    # endregion LAYOUT
    # ----------------------------------------


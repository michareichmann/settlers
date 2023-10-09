import numpy as np
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLayout

from gui.mine_box import MineBox
from gui.utils import *
from src.mine import MineClasses
from utils.helpers import Dir, warning
from typing import List


class MineDialogue(QDialog):

    FigPath = Dir.joinpath('figures')

    def __init__(self, mine_boxes: List[MineBox]):
        super().__init__()

        self.MineBoxes = mine_boxes

        self.setWindowTitle('Add Mine')

        self.PicLayout = self.create_pic_layout()  # Mine figures for selection
        self.ValueLayout = self.create_value_layout()  # Value selection

        self.Layout = self.create_layout()

        self.SelectedMine = None

    @staticmethod
    def get_widgets(layout: QLayout):
        return np.array([layout.itemAt(i).widget() for i in range(layout.count())])

    @property
    def values_pos(self):
        x = [int(w.text()) for w in self.get_widgets(self.ValueLayout)[1::2]]  # there is always a pair of label and widget
        return [x[1], x[0], x[2]], 99 if x[-1] == -1 else x[-1]

    def set_default_values(self):
        ws = self.get_widgets(self.ValueLayout)[1::2]
        for i, v in zip([1, 0, 2], MineBox.load_default(self.SelectedMine)[0]):  # take the default values from the first mine
            ws[i].setText(str(v))

    def select_mine(self, i):
        buttons = self.get_widgets(self.PicLayout)
        for but in buttons:
            but.set_clicked(False)
        buttons[i].set_clicked(True)
        self.SelectedMine = MineClasses[i]
        self.set_default_values()

    def add_mine2cfg(self):
        cfg = MineBox.Config
        cfg.set_section(str(self.SelectedMine.Resource))
        options = ['deposit', 'extra time', 'level']
        values, pos = self.values_pos
        n_mines = len(cfg.get_value('extra time'))
        for v, o in zip(values, options):
            if o in cfg[cfg.Section]:
                old_val = cfg.get_value(o)
                new_val = str(v)
                if type(old_val) is list:
                    old_val.insert(pos, v)
                    new_val = old_val
                elif old_val != new_val:
                    new_val = [int(old_val)] * n_mines
                    new_val.insert(pos, v)
                cfg.set_value(str(new_val), o)
        cfg.write()

    def confirm(self):
        if self.SelectedMine is not None:
            self.add_mine2cfg()
            values, pos = self.values_pos
            i = MineClasses.index(self.SelectedMine)
            self.MineBoxes[i].insert_mine(pos, self.SelectedMine(*values))
            self.done(QDialog.Accepted)
        else:
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

        labels = ['Extra Time [s]:', 'Deposit:', 'Level:', 'Position:']
        widgets = [line_edit('', 50), line_edit('', 50), line_edit('', 50), line_edit(-1, 50)]
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


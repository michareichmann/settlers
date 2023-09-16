from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtCore import Qt
from gui.group_box import GroupBox
from gui.utils import *
from src.mine import Mines


class MineBox(GroupBox):

    HEIGHT = 20

    def __init__(self, mines: Mines):

        super().__init__()
        self.Mines = mines

        self.L = [label(str(m), bold=True) for m in self]

        self.make()

    def __getitem__(self, item):
        return self.Mines[item]

    def update(self):
        self.Mines.update()

    def make(self):
        layout = QGridLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        for i, mine in enumerate(self.Mines.L):
            layout.addWidget(label(str(mine), bold=True), i, 0, Qt.AlignLeft)

        for widget in self.children():
            try:
                format_widget(widget, font='ubuntu', color='grey', font_size=FontSize, bold=False)
            except AttributeError:  # catch the widgets that can't be formatted by a stylesheet
                pass
            except Exception as err:
                print(err, type(err))
                pass
        self.setLayout(layout)

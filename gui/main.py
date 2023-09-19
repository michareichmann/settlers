#!/usr/bin/env python
# -*- coding: utf-8 -*-
# --------------------------------------------------------
#       GUI for the ETH High Voltage Client
# created on June 29th 2018 by M. Reichmann (remichae@phys.ethz.ch)
# --------------------------------------------------------

import sys

from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QFont, QCursor
from PyQt5.QtWidgets import QMainWindow, QAction, QFontDialog, QWidget, QDialog, QVBoxLayout, QHBoxLayout, QGridLayout

from gui.mine_box import MineBox, ControlBox
from gui.utils import *
from src.mine import Mines, mine_from_str
from utils.helpers import Dir, info

# todo: move layout to fields


class Gui(QMainWindow):

    Width = 500
    Height = 200
    BUTTON_HEIGHT = 50
    Version = 0.0
    Title = f'Settlers Online Gui V{Version}'

    def __init__(self):
        super(Gui, self).__init__()

        self.MainBox = QVBoxLayout()
        self.configure()

        self.Mines = Mines()
        self.MineBox = MineBox(self.Mines)
        self.ControlBox = ControlBox(self.Mines)

        self.MenuBar = MenuBar(self, True)

        self.make()

        self.MainBox.addStretch()

        self.timer = QTimer()  # updates the plot
        self.timer.timeout.connect(self.update)  # noqa
        self.timer.start(1000)

        self.show()

    def closeEvent(self, event):
        self.MineBox.Mines.save()
        self.MenuBar.close_app()

    def update(self):
        self.MineBox.update()

    def make(self):
        layout = QHBoxLayout()
        layout.addWidget(self.MineBox)
        layout.addWidget(self.ControlBox)
        self.MainBox.addLayout(layout)

    def configure(self):
        self.setGeometry(1000, 500, Gui.Width, Gui.Height)
        self.setWindowTitle(Gui.Title)
        self.setWindowIcon(QIcon(str(Dir.joinpath('figures', 'favicon.ico'))))
        self.setCentralWidget(QWidget())
        self.centralWidget().setLayout(self.MainBox)

    def mine_dialogue(self):
        q = QDialog()
        q.setWindowTitle('Add Mine')

        main_layout = QVBoxLayout()
        pic_layout = QHBoxLayout()
        for i, pic in enumerate([Dir.joinpath('figures', f'{name}-mine.png') for name in ['cop', 'iro', 'coa', 'gol']]):
            pic_layout.addWidget(PicButOpacity(do_nothing, pic), alignment=CEN)

        value_layout = QGridLayout()
        value_layout.setContentsMargins(4, 4, 4, 4)
        extra_time = [(label('Extra Time:')), line_edit(10), label('s')]
        deposit = [label('Deposit:'), line_edit(500)]
        level = [label('Level:'), line_edit(1)]
        paused = [label('Paused:'), check_box()]
        align = [RIGHT, CEN, LEFT]
        for i, row in enumerate([extra_time, deposit, level]):
            for j, widget in enumerate(row):
                value_layout.addWidget(widget, i, j, align[j])

        def done():
            for k in range(pic_layout.count()):
                w = pic_layout.itemAt(k).widget()
                if w.Clicked:  # noqa
                    self.ControlBox.add_mine(mine_from_str(w.PicName, deposit[1].text(), int(extra_time[1].text()), level[1].text(), paused[1].isChecked()))  # noqa
                    break
            print(self.Mines, self.MineBox.Mines)
            q.done(QDialog.Accepted)

        main_layout.addLayout(pic_layout)
        main_layout.addLayout(value_layout)
        main_layout.addWidget(button('Confirm', done))

        q.setLayout(main_layout)
        q.move(QCursor.pos())
        if q.exec() == QDialog.Accepted:
            return


class MenuBar(object):
    def __init__(self, gui, display=False):
        self.Window = gui
        self.Menus = {}
        self.Display = display
        self.load()

    def load(self):
        self.add_menu('File')
        self.add_menu_entry('File', 'Exit', 'Ctrl+Q', self.close_app, 'Close the Application')
        self.add_menu_entry('File', 'Font', 'Ctrl+F', self.font_choice, 'Open font dialog')
        self.add_menu_entry('File', 'Add Mine', 'Ctrl+M', self.Window.mine_dialogue, 'Add new mine')

    def add_menu(self, name):
        self.Window.statusBar()
        main_menu = self.Window.menuBar()
        self.Menus[name] = main_menu.addMenu('&{n}'.format(n=name))

    def add_menu_entry(self, menu, name, shortcut, func, tip=''):
        action = QAction('&{n}'.format(n=name), self.Window)
        action.setShortcut(shortcut)
        action.setStatusTip(tip)
        action.triggered.connect(func)  # noqa
        self.Menus[menu].addAction(action)

    def font_choice(self):
        font, valid = QFontDialog.getFont(self.Window)
        if valid:
            for box in self.Window.DeviceBoxes:
                header_font = QFont(font)
                header_font.setPointSize(font.pointSize() * 1.4)
                box.setFont(header_font)
                box.set_fonts(font)

    @staticmethod
    def close_app():
        info('Closing application')
        sys.exit(2)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# --------------------------------------------------------
#       GUI for the ETH High Voltage Client
# created on June 29th 2018 by M. Reichmann (remichae@phys.ethz.ch)
# --------------------------------------------------------

import sys

from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import QMainWindow, QAction, QFontDialog, QWidget, QVBoxLayout, QHBoxLayout

from gui.mine_box import MineBox
from gui.mine_dialogue import MineDialogue
from gui.utils import *
from src.mine import *
from utils.helpers import Dir, info


class MineGui(QMainWindow):

    Width = 500
    Height = 200
    BUTTON_HEIGHT = 50
    Version = 1.0
    Title = f'Settlers Online - Mines V{Version}'
    T_UPDATE = 500

    def __init__(self):
        super(MineGui, self).__init__()

        self.Layout = self.create_layout()

        # SUBLAYOUTS
        self.MineBoxes = self.create_boxes()
        self.MineDialogue = MineDialogue(self.MineBoxes)
        self.MenuBar = MenuBar(self, True)

        self.adjustSize()

        self.Timer = self.create_timer()
        self.show()

    def create_layout(self) -> QVBoxLayout:
        self.configure()
        layout = QVBoxLayout()
        self.setCentralWidget(QWidget())
        self.centralWidget().setLayout(layout)
        return layout  # noqa

    def create_boxes(self):
        boxes = [MineBox(cls) for cls in MineClasses]
        layout = QVBoxLayout()
        for box in boxes:
            layout.addWidget(box)
        self.Layout.addLayout(layout)
        return boxes

    def create_timer(self) -> QTimer:
        t = QTimer()
        t.timeout.connect(self.update)  # noqa
        t.start(MineGui.T_UPDATE)
        return t

    def closeEvent(self, event):
        for box in self.MineBoxes:
            box.Mines.save()
        self.MenuBar.close_app()

    def update(self):
        for box in self.MineBoxes:
            box.update()
            box.Mines.save()

    def configure(self):
        self.setGeometry(1000, 500, MineGui.Width, MineGui.Height)
        self.setWindowTitle(MineGui.Title)
        self.setWindowIcon(QIcon(str(Dir.joinpath('figures', 'favicon.ico'))))
        self.setWindowFlags(Qt.WindowStaysOnTopHint)


class MenuBar(object):
    def __init__(self, gui: MineGui, display=False):
        self.Window = gui
        self.Menus = {}
        self.Display = display
        self.load()

    def load(self):
        self.add_menu('File')
        self.add_menu_entry('File', 'Exit', 'Ctrl+Q', self.close_app, 'Close the Application')
        self.add_menu_entry('File', 'Font', 'Ctrl+F', self.font_choice, 'Open font dialog')
        self.add_menu_entry('File', 'Add Mine', 'Ctrl+M', self.Window.MineDialogue.run, 'Add new mine')

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
            for box in self.Window.MineBoxes:
                header_font = QFont(font)
                header_font.setPointSize(int(font.pointSize() * 1.2))
                box.setFont(header_font)
                box.adjustSize()
                # box.set_fonts(font)

    @staticmethod
    def close_app():
        info('Closing application')
        sys.exit(2)


class TestGui(QMainWindow):

    Width = 500
    Height = 200
    BUTTON_HEIGHT = 50
    Version = 0.0
    Title = f'TEST'
    T_UPDATE = 500

    def __init__(self):
        super(TestGui, self).__init__()

        self.Layout = self.create_layout()

        self.adjustSize()

        self.Timer = self.create_timer()
        self.show()

    def create_layout(self) -> QHBoxLayout:
        self.configure()
        layout = QHBoxLayout()
        self.setCentralWidget(QWidget())
        self.centralWidget().setLayout(layout)
        return layout  # noqa

    def create_timer(self) -> QTimer:
        t = QTimer()
        t.timeout.connect(self.update)  # noqa
        t.start(MineGui.T_UPDATE)
        return t

    def configure(self):
        self.setGeometry(1000, 500, MineGui.Width, MineGui.Height)
        self.setWindowTitle(MineGui.Title)
        self.setWindowIcon(QIcon(str(Dir.joinpath('figures', 'favicon.ico'))))

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# --------------------------------------------------------
#       GUI for the ETH High Voltage Client
# created on June 29th 2018 by M. Reichmann (remichae@phys.ethz.ch)
# --------------------------------------------------------

from sys import exit as end
from numpy import ceil, where
from utils.helpers import Dir, info, choose

from PyQt5.QtCore import QTimer, QPoint, Qt
from PyQt5.QtGui import QIcon, QFont, QCursor
from PyQt5.QtWidgets import QMainWindow, QAction, QFontDialog, QVBoxLayout, QWidget, QHBoxLayout, QInputDialog, QLabel, QDialog, QGridLayout

from gui.mine_box import MineBox, Mines

# from src.display_box import DisplayBox
# from src.hv_box import HVBox
# from src.device_reader import get_devices, get_logging_devices, get_dummies
# from src.utils import *
# from src.live_monitor import LiveMonitor
# from src.config import Config
#
# from src.device_box import make_line_edit, make_button, make_check_box


class Gui(QMainWindow):

    Width = 500
    Height = 500
    BUTTON_HEIGHT = 50
    Version = 0.0
    Title = f'Settlers Online Gui V{Version}'

    def __init__(self):
        super(Gui, self).__init__()

        self.MainBox = QHBoxLayout()
        self.configure()
        self.MenuBar = MenuBar(self, True)

        self.MainBox.addWidget(MineBox(Mines()))

        self.timer = QTimer()  # updates the plot
        self.timer.timeout.connect(self.update)
        self.timer.start(1000)

        self.show()

    def closeEvent(self, event):
        self.MenuBar.close_app()

    def update(self):
        pass

    def configure(self):
        self.setGeometry(2000, 300, Gui.Width, Gui.Height)
        self.setWindowTitle(Gui.Title)
        self.setWindowIcon(QIcon(str(Dir.joinpath('figures', 'favicon.ico'))))
        self.setCentralWidget(QWidget())
        self.centralWidget().setLayout(self.MainBox)

    def start_threads(self, from_logs):
        for device in self.Devices:
            device.FromLogs = from_logs
            device.start()

    def make_device_boxes(self):
        boxes = []
        vboxes = [QVBoxLayout() for _ in range(ceil(self.NDevices / 3).astype('u2'))]
        i = 0
        for device in self.Devices:
            for channel in device.ActiveChannels:
                box = HVBox(device, channel) if not self.FromLogs else DisplayBox(device, channel)
                vboxes[i // 3].addWidget(box)
                boxes.append(box)
                i += 1
        while i % 3 != 0 and i > 3:
            box = HVBox() if not self.FromLogs else DisplayBox()
            vboxes[-1].addWidget(box)
            boxes.append(box)
            i += 1
        for box in vboxes:
            self.MainBox.addLayout(box)
        return boxes

    def reset_titles(self):
        for box in self.DeviceBoxes:
            if box.Device is not None:
                box.set_title()

    @staticmethod
    def query_devices(config):
        config = Config(config)
        labels = ['{} - {}'.format(key, value) for key, value in config.get_sections().items()]
        values = query_list('Choose Active Devices', labels, [i in config.get_active_devices() for i in range(len(labels))], checks=True)
        if values is not None:
            config.set_active_devices(str(list(where(array(values))[0])))

    @staticmethod
    def query_channels(config):
        config = Config(config)
        sections = config.get_sections(active=True)
        xlabels = ['{} - {}'.format(key, value) for key, value in sections.items() if config.get_value('number of channels', int, key, 1) > 1]
        if not len(xlabels):
            return
        ylabels = ['CH{}'.format(i) for i in range(max(config.get_value('number of channels', int, section, 1) for section in sections))]
        init_values = [[i in config.get_active_channels(section) for i in range(len(ylabels))] for section in sections]
        values = query_table_checks('Choose Active Channels', xlabels, ylabels, init_values)
        if values is not None:
            for section, value in zip(sections, values):
                config.set_active_channels(section, str(list(where(array(value))[0])))

    def set_device_names(self):
        labels = ['{} - {}'.format(key, value) for key, value in self.Devices[0].Config.get_sections(active=True).items()]
        values = query_list('Device Names', labels, [dev.get_id() for dev in self.Devices])
        if values is not None:
            for dev, value in zip(self.Devices, values):
                dev.Config.set_id(value)
            self.reset_titles()

    def set_dut_names(self):
        names = ['{} - CH{}'.format(dev.get_id(), ch) for dev in self.Devices for ch in dev.ActiveChannels]
        values = query_list('DUT Names', names, [name for dev in self.Devices for name in dev.Config.get_dut_names(active=True)])
        if values is not None:
            i = 0
            for dev in self.Devices:
                for ch in dev.ActiveChannels:
                    dev.Config.set_dut_name(values[i], ch)
                    i += 1
            self.reset_titles()


def query(title, label, init_value='', pos: QPoint = None):
    q = QInputDialog()
    q.setWindowTitle(title)
    q.setLabelText(label)
    q.setTextValue(str(init_value))
    q.move(choose(pos, QCursor.pos()))
    if q.exec() == QDialog.Accepted:
        return q.textValue()


def query_list(title, label_names, init_values=None, pos: QPoint = None, checks=False):
    q = QDialog()

    def done():
        q.done(QDialog.Accepted)
    q.setWindowTitle(title)
    layout = QGridLayout()
    layout.setContentsMargins(4, 4, 4, 4)
    widgets = []
    for i, (name, init_value) in enumerate(zip(label_names, choose(init_values, [''] * len(label_names)))):
        layout.addWidget(QLabel(name), i, 0, Qt.AlignRight)
        widgets.append(make_line_edit(str(init_value)) if not checks else make_check_box(bool(init_value), size=40))
        layout.addWidget(widgets[i], i, 1, Qt.AlignLeft)
    layout.addWidget(make_button('Done', done), len(label_names) + 1, 1)
    q.setLayout(layout)
    q.move(choose(pos, QCursor.pos()))
    if q.exec() == QDialog.Accepted:
        return [widget.isChecked() if checks else widget.text() for widget in widgets]


def query_table_checks(title, x_labels, y_labels, init_values=None, pos: QPoint = None):
    q = QDialog()

    def done():
        q.done(QDialog.Accepted)
    q.setWindowTitle(title)
    layout = QGridLayout()
    layout.setContentsMargins(4, 4, 4, 4)
    widgets = zeros((len(x_labels), len(y_labels)), dtype=object)
    init_values = choose(init_values, zeros((len(x_labels), len(y_labels)), dtype=bool))
    for i, xname in enumerate(x_labels, 0):
        layout.addWidget(QLabel(xname), i + 1, 0, Qt.AlignRight)
        for j, yname in enumerate(y_labels):
            if not i:
                layout.addWidget(QLabel(yname), 0, j + 1, Qt.AlignCenter)
            widgets[i, j] = make_check_box(bool(array(init_values)[i, j]), size=40)
            layout.addWidget(widgets[i, j], i + 1, j + 1, Qt.AlignCenter)
    layout.addWidget(make_button('Done', done), widgets.shape[0] + 1, widgets.shape[1])
    q.setLayout(layout)
    q.move(choose(pos, QCursor.pos()))
    if q.exec() == QDialog.Accepted:
        return [[widget.isChecked() for widget in col] for col in widgets]


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
        # if self.Display:
        #     self.add_menu('Settings')
        #     self.add_menu_entry('Settings', 'Marker Size', 'Ctrl+M', self.set_ms, 'Open marker size dialog')
        #     self.add_menu_entry('Settings', 'Line Width', 'Ctrl+L', self.set_lw, 'Open line width dialog')
        self.add_menu('Config')
        self.add_menu_entry('Config', 'Set Device Names', 'Ctrl+N', self.Window.set_device_names, 'Change the names of the HV devices')
        self.add_menu_entry('Config', 'Set DUT Names', 'Ctrl+D', self.Window.set_dut_names, 'Change the names of DUTs')

    def add_menu(self, name):
        self.Window.statusBar()
        main_menu = self.Window.menuBar()
        self.Menus[name] = main_menu.addMenu('&{n}'.format(n=name))

    def add_menu_entry(self, menu, name, shortcut, func, tip=''):
        action = QAction('&{n}'.format(n=name), self.Window)
        action.setShortcut(shortcut)
        action.setStatusTip(tip)
        action.triggered.connect(func)
        self.Menus[menu].addAction(action)

    def font_choice(self):
        font, valid = QFontDialog.getFont(self.Window)
        if valid:
            for box in self.Window.DeviceBoxes:
                header_font = QFont(font)
                header_font.setPointSize(font.pointSize() * 1.4)
                box.setFont(header_font)
                box.set_fonts(font)
            # LiveMonitor.FD = {'family': font.family(), 'size': font.pointSize() * 1.4}

    def close_app(self):
        info('Closing application')
        end(2)

    # def set_ms(self):
    #     value, valid = QInputDialog.getInt(self.Window, 'Marker Size', 'Marker Size:')
    #     if valid:
    #         LiveMonitor.MS = value
    #
    # def set_lw(self):
    #     value, valid = QInputDialog.getInt(self.Window, 'Line Width', 'Line Width:')
    #     if valid:
    #         LiveMonitor.LW = value


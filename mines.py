#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from gui.main_window import *
from PyQt5.QtWidgets import QApplication
from warnings import filterwarnings
import qdarkstyle
import signal
from argparse import ArgumentParser


if __name__ == '__main__':

    parser = ArgumentParser()
    parser.add_argument('--gui', '-g', action='store_true')
    args = parser.parse_args()

    os.system('/bin/bash -c "source /home/micha/.bashrc"')  # required for the launcher

    if args.gui:

        signal.signal(signal.SIGINT, signal.SIG_DFL)

        app = QApplication([Gui.Title])
        app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
        filterwarnings('ignore')

        g = Gui()

        sys.exit(app.exec_())

    else:
        app = QApplication(['bla'])

        from gui.mine_dialogue import MineDialogue

        a = MineBox(CoalMine)



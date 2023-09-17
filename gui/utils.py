from PyQt5.QtWidgets import QLabel, QLineEdit, QPushButton, QSpinBox, QComboBox, QCheckBox, QPlainTextEdit
from PyQt5.QtCore import Qt
from plotting.utils import do, do_nothing


FontSize = 13
ButtonHeight = 50

LEFT = Qt.AlignLeft
RIGHT = Qt.AlignRight
CEN = Qt.AlignCenter


def combobox(lst, ind=0):
    b = QComboBox()
    b.addItems(lst)
    b.setCurrentIndex(ind)
    return b


def spinbox(low, high, value, step=1):
    b = QSpinBox()
    b.setRange(low, high)
    b.setValue(value)
    b.setSingleStep(step)
    return b


def line_edit(txt='', length=None):
    le = QLineEdit()
    le.setText(txt)
    do(le.setMaximumWidth, length)
    return le


def text_edit(txt='', length=None, min_height=None):
    t = QPlainTextEdit()
    t.setPlainText(txt)
    do(t.setMaximumWidth, length)
    do(t.setMinimumHeight, min_height)
    return t


def button(txt, f=do_nothing, size=None, height=ButtonHeight):
    but = QPushButton()
    but.setText(txt)
    do(but.setFixedWidth, size)
    do(but.setMaximumHeight, height)
    but.clicked.connect(f)  # noqa
    return but


def check_box(value=False, size=None):
    b = QCheckBox()
    b.setChecked(value)
    if size is not None:
        b.setStyleSheet('QCheckBox::indicator {{width: {0}px; height: {0}px;}}'.format(size))
    return b


def label(txt, color=None, bold=False, font=None, font_size=FontSize * 1.5, bg_col=None):
    lb = QLabel(str(txt))
    format_widget(lb, color, bold, font_size, font, bg_col)
    return lb


def format_widget(widget, color=None, bold=None, font_size=None, font=None, bg_col=None):
    dic = {'color': color, 'font-weight': 'bold' if bold else None, 'font-size': '{}px'.format(font_size) if font_size is not None else None, 'font-family': font, 'background-color':
           bg_col if bg_col is not None else None}
    widget.setStyleSheet(style_sheet(dic))


def style_sheet(dic):
    return '; '.join(f'{k}: {v}' for k, v in dic.items() if v is not None)

from PyQt5.QtWidgets import QLabel, QLineEdit, QPushButton, QSpinBox, QComboBox, QCheckBox, QPlainTextEdit, QAbstractButton
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPainter, QIcon, QPixmap
from plotting.utils import do, do_nothing, Path


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
    le.setText(str(txt))
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


def pix_map(p: Path):
    return QIcon("filepath.svg").pixmap(QSize()) if p.stem == 'svg' else QPixmap(str(p))


def format_widget(widget, color=None, bold=None, font_size=None, font=None, bg_col=None):
    dic = {'color': color, 'font-weight': 'bold' if bold else None, 'font-size': '{}px'.format(font_size) if font_size is not None else None, 'font-family': font, 'background-color':
           bg_col if bg_col is not None else None}
    widget.setStyleSheet(style_sheet(dic))


def style_sheet(dic):
    return '; '.join(f'{k}: {v}' for k, v in dic.items() if v is not None)


class PicButton(QAbstractButton):
    def __init__(self, f, pic: Path, pic_hover: Path, pic_pressed: Path, fr=None, parent=None):
        super(PicButton, self).__init__(parent)
        self.PicName = pic.name
        self.PixMap = pix_map(pic)
        self.PixMapHover = pix_map(pic_hover)
        self.PixMapPressed = pix_map(pic_pressed)

        self.pressed.connect(f)  # noqa
        self.released.connect(self.update if fr is None else fr)  # noqa

    def paint(self, p: QPainter):
        pass

    def paintEvent(self, event):
        pix = self.PixMapHover if self.underMouse() else self.PixMap
        if self.isDown():
            pix = self.PixMapPressed

        painter = QPainter(self)
        self.paint(painter)
        painter.drawPixmap(event.rect(), pix)

    def enterEvent(self, event):
        self.update()

    def leaveEvent(self, event):
        self.update()

    def sizeHint(self):
        return QSize(18, 18)


class PicButOpacity(PicButton):

    def __init__(self, f, pic: Path, opacity=.5, parent=None):

        super().__init__(f, pic, pic, pic, self.set_checked, parent)
        self.Opacity = opacity
        self.Clicked = False

    def set_checked(self):
        self.Clicked = not self.Clicked

    def paint(self, p: QPainter):
        if not self.underMouse() and not self.isDown() and not self.Clicked:
            p.setOpacity(self.Opacity)

    def sizeHint(self):
        return QSize(40, 40)

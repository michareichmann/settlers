from functools import partial

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPainter, QIcon, QPixmap
from PyQt5.QtWidgets import QLabel, QLineEdit, QPushButton, QSpinBox, QComboBox, QCheckBox, QPlainTextEdit, QAbstractButton

from plotting.utils import do, do_nothing, Path, choose

FontSize = 13
ButtonHeight = 50

LEFT = Qt.AlignLeft
RIGHT = Qt.AlignRight
CEN = Qt.AlignCenter


def my_widget(cls, align: Qt.AlignmentFlag, xpos: int = 0, parent=None):

    class MyWidget(cls):

        def __init__(self):
            super().__init__(parent)
            self.Align = align
            self.XPos = xpos

        def __repr__(self):
            return f'My{cls.__name__}'

        def __getitem__(self, item):
            return [self, self.Align, self.XPos][item]

    return MyWidget()


def combobox(lst, ind=0, align=CEN, xpos=0):
    b = my_widget(QComboBox, align, xpos)
    b.addItems(lst)
    b.setCurrentIndex(ind)
    return b


def spinbox(low, high, value, step=1, align=CEN, xpos=0):
    b = my_widget(QSpinBox, align, xpos)
    b.setRange(low, high)
    b.setValue(value)
    b.setSingleStep(step)
    return b


def line_edit(txt='', length=None, align=CEN, xpos=0):
    le = my_widget(QLineEdit, align, xpos)
    le.setText(str(txt))
    do(le.setMaximumWidth, length)
    return le


def text_edit(txt='', length=None, min_height=None, align=CEN, xpos=0):
    t = my_widget(QPlainTextEdit, align, xpos)
    t.setPlainText(txt)
    do(t.setMaximumWidth, length)
    do(t.setMinimumHeight, min_height)
    return t


def button(txt, f=do_nothing, size=None, height=ButtonHeight, align=CEN, xpos=0):
    but = my_widget(QPushButton, align, xpos)
    but.setText(txt)
    do(but.setFixedWidth, size)
    do(but.setMaximumHeight, height)
    but.clicked.connect(f)  # noqa
    return but


def check_box(value=False, size=None, align=CEN, xpos=0):
    b = my_widget(QCheckBox, align, xpos)
    b.setChecked(value)
    if size is not None:
        b.setStyleSheet('QCheckBox::indicator {{width: {0}px; height: {0}px;}}'.format(size))
    return b


def label(txt, color=None, bold=False, font=None, font_size=FontSize * 1.5, bg_col=None, align=CEN, xpos=0):
    lb = my_widget(QLabel, align, xpos)
    lb.setText(str(txt))
    format_widget(lb, color, bold, font_size, font, bg_col)  # noqa
    return lb


def pix_map(p: Path):
    return QIcon("filepath.svg").pixmap(QSize(100, 100)) if p.stem == 'svg' else QPixmap(str(p))


def format_widget(widget, color=None, bold=None, font_size=None, font=None, bg_col=None):
    dic = {'color': color, 'font-weight': 'bold' if bold else None, 'font-size': '{}px'.format(font_size) if font_size is not None else None, 'font-family': font, 'background-color':
           bg_col if bg_col is not None else None}
    widget.setStyleSheet(style_sheet(dic))


def style_sheet(dic):
    return '; '.join(f'{k}: {v}' for k, v in dic.items() if v is not None)


class PicButton(QAbstractButton):
    def __init__(self, f, pic: Path, pic_hover: Path = None, pic_pressed: Path = None, fr=None, align: Qt.AlignmentFlag = CEN, xpos: int = 0, parent=None):
        super(PicButton, self).__init__(parent)
        self.PicName = pic.name
        self.PixMap = pix_map(pic)
        self.PixMapHover = pix_map(choose(pic_hover, pic.with_stem(f'{pic.stem}-hover')))
        self.PixMapPressed = pix_map(choose(pic_pressed, pic.with_stem(f'{pic.stem}-pressed')))

        self.Align = align
        self.XPos = xpos

        self.pressed.connect(f)  # noqa
        self.released.connect(self.update if fr is None else fr)  # noqa

    def __getitem__(self, item):
        return [self, self.Align, self.XPos][item]

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


class OnOffButton(QAbstractButton):
    def __init__(self, f, off, pic_on: Path, pic_off: Path = None, fr=None, align: Qt.AlignmentFlag = CEN, xpos: int = 0, opacity=.8, parent=None):
        super(OnOffButton, self).__init__(parent)

        self.Opacity = opacity
        self.PixMapOn = pix_map(pic_on)
        self.PixMapOff = pix_map(pic_off)

        self.Align = align
        self.XPos = xpos
        self.Clicked = not off

        self.pressed.connect(partial(self.flick, f))  # noqa
        self.released.connect(self.update if fr is None else fr)  # noqa

    def __getitem__(self, item):
        return [self, self.Align, self.XPos][item]

    def flick(self, f):
        self.Clicked = not self.Clicked
        f()

    def paint(self, p: QPainter):
        if self.underMouse() and not self.isDown():
            p.setOpacity(self.Opacity)

    def paintEvent(self, event):
        pix = self.PixMapOn if self.Clicked else self.PixMapOff

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
        painter.setRenderHint(QPainter.LosslessImageRendering, True)
        self.paint(painter)
        painter.drawPixmap(event.rect(), pix, pix.rect())

    def enterEvent(self, event):
        self.update()

    def leaveEvent(self, event):
        self.update()

    def sizeHint(self):
        return QSize(47, 22)


class PicButOpacity(PicButton):

    def __init__(self, f, pic: Path, opacity=.5, align: Qt.AlignmentFlag = CEN, xpos: int = 0, fr=None, parent=None):

        super().__init__(f, pic, pic, pic, fr, align, xpos, parent)
        self.Opacity = opacity
        self.Clicked = False

    def set_clicked(self, status: bool):
        self.Clicked = status
        self.update()

    def flick(self):
        self.Clicked = not self.Clicked

    def paint(self, p: QPainter):
        if not self.underMouse() and not self.isDown() and not self.Clicked:
            p.setOpacity(self.Opacity)

    def sizeHint(self):
        return QSize(40, 40)

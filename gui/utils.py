from functools import partial

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPainter, QPixmap
from PyQt5 import QtSvg
from PyQt5.QtWidgets import QLabel, QLineEdit, QPushButton, QSpinBox, QComboBox, QCheckBox, QPlainTextEdit, QAbstractButton

from plotting.utils import do, do_nothing, Path, choose
from matplotlib.colors import cnames

from xml.etree import ElementTree


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
    do(but.setFixedHeight, height)
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


def figure(p: Path):
    return QtSvg.QSvgRenderer(str(p)) if p.suffix == '.svg' else QPixmap(str(p))


def format_widget(widget, color=None, bold=None, font_size=None, font=None, bg_col=None):
    dic = {'color': color, 'font-weight': 'bold' if bold else None, 'font-size': '{}px'.format(font_size) if font_size is not None else None, 'font-family': font, 'background-color':
           bg_col if bg_col is not None else None}
    widget.setStyleSheet(style_sheet(dic))


def style_sheet(dic):
    return '; '.join(f'{k}: {v}' for k, v in dic.items() if v is not None)


class MySvg:

    def __init__(self, path: Path):
        self.Path = path
        self.Str = self.load()

    def load(self):
        with open(self.Path) as f:
            return ''.join(f.readlines())

    def set_fill_color(self, color: str):
        s = self.Str.find('fill')
        self.Str = self.Str.replace(self.Str[s:s + 14], f'fill="{color if color.startswith("#") else cnames[color]}"')

    def render(self, painter: QPainter):
        QtSvg.QSvgRenderer(bytes(self.Str, 'utf-8')).render(painter)


class MyXML:
    def __init__(self, path: Path):
        self.Root = ElementTree.parse(path).getroot()
        self.G = self.Root[-1]
        self.Paths = self.G[0]

    def set_opacity(self, value: float):
        self.G.set('style', f'opacity: {value:.1f}')

    def set_style_attr(self, path_id, key: str, value):
        old_style = self.Paths[path_id].get('style')
        old_str = old_style[old_style.find(f'{key}:'): len(key) + 8]
        self.Paths[path_id].set('style', old_style.replace(old_str, f'{key}:{value}'))

    def render(self, painter: QPainter):
        QtSvg.QSvgRenderer(ElementTree.tostring(self.Root)).render(painter)


class MyAbstractButton(QAbstractButton):
    def __init__(self, align: Qt.AlignmentFlag, xpos: int, parent=None):
        super().__init__(parent)
        self.Align = align
        self.XPos = xpos

    def __repr__(self):
        return self.__class__.__name__

    def __getitem__(self, item):
        return [self, self.Align, self.XPos][item]


class SvgButton(MyAbstractButton):
    def __init__(self, f, pic: Path, fr=None, align: Qt.AlignmentFlag = CEN, xpos: int = 0, parent=None):
        super(SvgButton, self).__init__(align, xpos, parent)
        self.PicName = pic.name
        self.Pic = MySvg(pic)

        self.pressed.connect(f)  # noqa
        self.released.connect(self.update if fr is None else fr)  # noqa

    def paintEvent(self, event):
        self.Pic.set_fill_color('black' if self.isDown() else 'white' if self.underMouse() else 'red')
        painter = QPainter(self)
        self.Pic.render(painter)
        painter.end()

    def sizeHint(self):
        return QSize(14, 14)


class PicButton(MyAbstractButton):
    def __init__(self, f, pic: Path, pic_hover: Path = None, pic_pressed: Path = None, fr=None, align: Qt.AlignmentFlag = CEN, xpos: int = 0, parent=None):
        super(PicButton, self).__init__(align, xpos, parent)
        self.PicName = pic.name
        self.PixMap = figure(pic)
        self.PixMapHover = figure(choose(pic_hover, pic.with_stem(f'{pic.stem}-hover')))
        self.PixMapPressed = figure(choose(pic_pressed, pic.with_stem(f'{pic.stem}-pressed')))

        self.pressed.connect(f)  # noqa
        self.released.connect(self.update if fr is None else fr)  # noqa

    def paint(self, p: QPainter):
        pass

    def paintEvent(self, event):
        pix = [self.PixMapHover, self.PixMapPressed, self.PixMap][1 if self.isDown() else 0 if self.underMouse() else 2]

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
        self.PicOn = MyXML(pic_on)
        self.PicOff = MyXML(pic_off)

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

    def paintEvent(self, event):
        pix = self.PicOn if self.Clicked else self.PicOff
        pix.set_opacity(self.Opacity if self.underMouse() else 1)
        painter = QPainter(self)
        pix.render(painter)
        painter.end()

    def enterEvent(self, event):
        self.update()

    def leaveEvent(self, event):
        self.update()

    def sizeHint(self):
        return QSize(42, 16)


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

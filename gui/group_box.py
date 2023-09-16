from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QGroupBox
from gui.utils import format_widget


class GroupBox(QGroupBox):

    Height = 40

    def __init__(self):
        super(GroupBox, self).__init__()

        self.Widgets, self.Labels = [], []
        self.configure()

    def configure(self):
        self.setTitle('Mines')
        self.setFont(QFont('Ubuntu', 8, QFont.Bold))
        format_widget(self, color='red')

    def set_fonts(self, font):
        for widget in self.Widgets:
            widget.setFont(font)
        for label in self.Labels:
            label.setFont(font)

    def make(self):
        pass



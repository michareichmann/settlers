from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QGroupBox, QLayout
from gui.utils import format_widget


class GroupBox(QGroupBox):

    Height = 35
    Title = 'Group Box'

    def __init__(self):
        super(GroupBox, self).__init__()

        self.Widgets, self.Labels, self.Buttons, self.LineEdits = [], [], [], []
        self.Layout: QLayout | None = None
        self.configure()

    @property
    def used_containers(self):
        return [w for w in [self.Widgets, self.Labels, self.Buttons, self.LineEdits] if len(w)]

    def configure(self):
        self.setTitle(self.Title)
        self.setFont(QFont('Ubuntu', 8, QFont.Bold))
        format_widget(self, color='red')

    def set_fonts(self, font):
        for widget in self.Widgets:
            widget.setFont(font)
        for label in self.Labels:
            label.setFont(font)

    def make(self):
        pass

    def remove_widgets(self):
        ws = [self.Layout.itemAt(i).widget() for i in range(self.Layout.count())]
        for w in ws:
            self.Layout.removeWidget(w)
            w.deleteLater()
        self.Widgets, self.Labels, self.Buttons, self.LineEdits = [], [], [], []



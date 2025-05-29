

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QFont, QPixmap, QPainter
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QFormLayout, QHBoxLayout, QLabel, QSizePolicy, QStackedWidget

from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
from qfluentwidgets import PushButton, TogglePushButton, PrimaryToolButton, ToolButton, ToggleToolButton, IndeterminateProgressRing, StateToolTip, InfoBar, InfoBarPosition, LineEdit, PrimaryPushButton, ComboBox

from qfluentwidgets import FluentIcon as FIF




class Tab3Widget(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        pass
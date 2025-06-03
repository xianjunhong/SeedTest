from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QIcon
from PyQt5.QtMultimedia import QSoundEffect
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QDesktopWidget, QStackedWidget
from qfluentwidgets import (SegmentedWidget)

from .pod_home import PodHome
from .pod_data import PodData


class PodUi(QWidget):

    def __init__(self):
        super().__init__()

        # 设置图标
        self.setWindowIcon(QIcon("frank/uiModule/icons/PhenoSeeds_logo.ico"))
        # self.resize(800, 640)
        self.setup_ui()
        self.set_center()

    def setup_ui(self):
        self.pivot = SegmentedWidget()
        self.stackedWidget = QStackedWidget()
        # 关键！设置主窗口布局
        self.main_window_layout = QVBoxLayout(self)

        self.tab_1 = PodHome()
        self.tab_2 = PodData()



        # 添加标签页
        self.addSubInterface(self.tab_1, 'tab_1', '豆荚考种')
        self.addSubInterface(self.tab_2, 'tab_2', '数据管理')


        self.main_window_layout.addWidget(self.pivot)
        self.main_window_layout.addWidget(self.stackedWidget)
        # self.main_window_layout.setContentsMargins(30, 10, 30, 30)
        self.stackedWidget.setCurrentWidget(self.tab_1)
        self.pivot.setCurrentItem(self.tab_1.objectName())
        self.pivot.currentItemChanged.connect(
            lambda k: self.stackedWidget.setCurrentWidget(self.findChild(QWidget, k)))


        self.add_sound()

    def add_sound(self):
        self.click_sound = QSoundEffect()
        # 修改为绝对路径测试（确保文件存在）
        file_path = r"frank\uiModule\music\click.wav"
        self.click_sound.setSource(QUrl.fromLocalFile(file_path))
        self.click_sound.setVolume(0.8)  # 音量设置(0.0-1.0)
        buttons = self.findChildren(QPushButton)
        for button in buttons:
            button.clicked.connect(self.play_sound)


    def play_sound(self):

        self.click_sound.play()




    def set_center(self):
        self.resize(900, 900)
        screen = QDesktopWidget().screenGeometry()
        window_size = self.geometry()  # 需窗口已设置尺寸
        # 本来是//2,但是考虑到偏移，所以改为3
        x = (screen.width() - window_size.width()) // 3
        y = (screen.height() - window_size.height()) // 3
        self.move(x, y)



    def addSubInterface(self, widget, objectName, text):
        widget.setObjectName(objectName)
        self.stackedWidget.addWidget(widget)
        self.pivot.addItem(routeKey=objectName, text=text)


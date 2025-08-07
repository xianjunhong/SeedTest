import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QGridLayout, QStackedWidget, QPushButton
)
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QLabel, QGraphicsDropShadowEffect
from until import create_centered_square_pixmap

from frank.handleModule.pod.init_pod import InitPod
from frank.uiModule.pod.pod_ui import PodUi

from frank.handleModule.count_anything.init_count_anything import InitCountAnything
from frank.uiModule.count_anything.count_anything_ui import CountAnythingUi


class CardButton(QFrame):
    def __init__(self, icon_path, title, callback):
        super().__init__()

        self.setFixedSize(180, 240)  # 4:3 比例卡片
        self.setStyleSheet("""
            QFrame {
                border-radius: 16px;
                background-color: white;
            }
            QFrame:hover {
                background-color: #f5faff;
            }
        """)

        # 设置卡片阴影效果
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(12)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 60))
        self.setGraphicsEffect(shadow)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(0)

        # 图标（上 3/4）
        icon_label = QLabel(self)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_height = int(self.height() * 0.75)
        icon_label.setFixedHeight(icon_height)



        icon_size = 100  # 或者其他你想要的正方形区域大小
        icon_label.setPixmap(create_centered_square_pixmap(icon_path, icon_size))

        # 文本（下 1/4）
        title_label = QLabel(title, self)
        title_label.setFont(QFont("Arial", 22,  QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFixedHeight(int(self.height() * 0.25))

        layout.addWidget(icon_label)
        layout.addWidget(title_label)

        # 整个卡片点击跳转
        self.mousePressEvent = lambda event: callback()


class StartPage(QWidget):
    def __init__(self, switch_page_func):
        super().__init__()
        layout = QGridLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setAlignment(Qt.AlignTop )  # ✅ 添加对齐方式

        layout.addWidget(CardButton("icons/soy_pod.png", "豆荚考种", lambda: switch_page_func(1)), 0, 0)
        layout.addWidget(CardButton("icons/soy_seed.png", "籽粒考种", lambda: switch_page_func(2)), 0, 1)
        layout.addWidget(CardButton("icons/no.png", "植株考种", lambda: switch_page_func(3)), 0, 2)
        layout.addWidget(CardButton("icons/count_anything.png", "CountAnything", lambda: switch_page_func(4)), 0, 3)

        self.setLayout(layout)

class PodPage(QWidget):
    def __init__(self, switch_page_func):  # 接收函数参数
        super().__init__()
        self.ui = PodUi()
        self.init_tools = InitPod(self.ui)

        layout = QVBoxLayout()
        layout.addWidget(self.ui)
        back_btn = QPushButton("返回")
        back_btn.setFixedHeight(10)
        back_btn.clicked.connect(lambda: switch_page_func(0))
        layout.addWidget(back_btn)
        layout.setContentsMargins(0, 0, 0, 0)  # 可选：取消内边距以填满整个区域
        self.setLayout(layout)

class SeedPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("这是籽粒考种页面"))
        self.setLayout(layout)

class PlantPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("这是植株考种页面"))
        self.setLayout(layout)


class CountAnythingPage(QWidget):
    def __init__(self, switch_page_func):  # 接收函数参数
        super().__init__()
        self.ui = CountAnythingUi()
        self.init_tools = InitCountAnything(self.ui)

        layout = QVBoxLayout()
        layout.addWidget(self.ui)
        back_btn = QPushButton("返回")
        back_btn.setFixedHeight(10)
        back_btn.clicked.connect(lambda: switch_page_func(0))
        layout.addWidget(back_btn)
        layout.setContentsMargins(0, 0, 0, 0)  # 可选：取消内边距以填满整个区域
        self.setLayout(layout)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.stack = QStackedWidget()
        self.start_page = StartPage(self.switch_page)
        self.pod_page = PodPage(self.switch_page)
        self.count_anything_page = CountAnythingPage(self.switch_page)
        self.seed_page = SeedPage()
        self.plant_page = PlantPage()


        self.stack.addWidget(self.start_page)
        self.stack.addWidget(self.pod_page)
        self.stack.addWidget(self.seed_page)
        self.stack.addWidget(self.plant_page)
        self.stack.addWidget(self.count_anything_page)

        self.setCentralWidget(self.stack)
        self.setWindowTitle("智能考种系统")
        self.resize(800, 600)

    def switch_page(self, index):
        self.stack.setCurrentIndex(index)



if __name__ == '__main__':

    app = QApplication([])
    # 适应高dpi
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    app.setAttribute(Qt.AA_DisableWindowContextHelpButton)  # 可选：同时禁用帮助按钮
    app.setStyleSheet("QMessageBox { messagebox-icon: none; }")  # 移除图标（间接去音）

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

    # # 初始化ui
    # ui = Ui()
    # # 给ui加功能
    # init_tools = InitTools(ui)
    # ui.show()
    # app.exec_()
    # init_tools.tab_1.close_device()
    # sys.exit()


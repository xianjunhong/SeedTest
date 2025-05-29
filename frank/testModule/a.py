import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout,
    QGridLayout, QStackedWidget, QPushButton, QFrame
)
from PyQt5.QtGui import QIcon, QPixmap, QFont
from PyQt5.QtCore import Qt, QSize

class CardButton(QFrame):
    def __init__(self, icon_path, title, callback):
        super().__init__()
        self.setFrameShape(QFrame.Box)
        self.setLineWidth(1)
        self.setStyleSheet("QFrame:hover {border: 2px solid #0078d7;}")  # 鼠标悬停高亮

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        icon_label = QLabel()
        pixmap = QPixmap(icon_path).scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        icon_label.setPixmap(pixmap)
        icon_label.setAlignment(Qt.AlignCenter)

        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 12))
        title_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(icon_label)
        layout.addWidget(title_label)
        self.setLayout(layout)

        # 鼠标点击事件触发回调
        self.mousePressEvent = lambda event: callback()

class StartPage(QWidget):
    def __init__(self, switch_page_func):
        super().__init__()
        layout = QGridLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)

        layout.addWidget(CardButton("pod.png", "豆荚考种", lambda: switch_page_func(1)), 0, 0)
        layout.addWidget(CardButton("seed.png", "籽粒考种", lambda: switch_page_func(2)), 0, 1)
        layout.addWidget(CardButton("plant.png", "植株考种", lambda: switch_page_func(3)), 0, 2)

        self.setLayout(layout)

class PodPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("这是豆荚考种页面"))
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

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.stack = QStackedWidget()
        self.start_page = StartPage(self.switch_page)
        self.pod_page = PodPage()
        self.seed_page = SeedPage()
        self.plant_page = PlantPage()

        self.stack.addWidget(self.start_page)
        self.stack.addWidget(self.pod_page)
        self.stack.addWidget(self.seed_page)
        self.stack.addWidget(self.plant_page)

        self.setCentralWidget(self.stack)
        self.setWindowTitle("智能考种系统")
        self.resize(800, 600)

    def switch_page(self, index):
        self.stack.setCurrentIndex(index)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

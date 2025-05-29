from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QProgressBar, QStackedWidget

class RotatingProgressBar(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        # 创建一个堆叠控件
        self.stack = QStackedWidget(self)

        # 页面1：正常控件
        page1 = QLabel("目标控件", self)
        page1.setAlignment(Qt.AlignCenter)
        page1.setStyleSheet("background-color: lightblue; font-size: 20px;")

        # 页面2：旋转进度条
        self.progress = QProgressBar(self)
        self.progress.setRange(0, 0)  # 无限加载
        self.progress.setStyleSheet("QProgressBar {border: 2px solid gray; border-radius: 5px; text-align: center;}")

        # 添加到堆叠控件
        self.stack.addWidget(page1)
        self.stack.addWidget(self.progress)

        layout.addWidget(self.stack)

        # 5秒后切换回正常控件
        self.stack.setCurrentIndex(1)  # 显示进度条
        QTimer.singleShot(5000, lambda: self.stack.setCurrentIndex(0))  # 5 秒后切换回页面1

if __name__ == "__main__":
    app = QApplication([])
    window = RotatingProgressBar()
    window.resize(600, 6000)
    window.show()
    app.exec_()

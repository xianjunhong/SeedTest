import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QGroupBox, QHBoxLayout, QPushButton, QStackedWidget,
    QScrollArea, QFrame, QGraphicsDropShadowEffect
)
from PyQt5.QtGui import QPixmap, QFont, QIcon, QColor
from PyQt5.QtCore import Qt

from frank.handleModule.count_anything.init_count_anything import InitCountAnything
from frank.handleModule.pod.init_pod import InitPod
from frank.handleModule.soy_seed.init_soy_seed import InitSoySeed
from frank.uiModule.count_anything.count_anything_ui import CountAnythingUi
from frank.uiModule.pod.pod_ui import PodUi
from frank.uiModule.soy_seed.soy_seed_ui import SoySeedUi
from until import create_centered_square_pixmap

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
        title_label.setFont(QFont("KaiTi", 22, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFixedHeight(int(self.height() * 0.25))

        layout.addWidget(icon_label)
        layout.addWidget(title_label)

        # 整个卡片点击跳转
        self.mousePressEvent = lambda event: callback()


class CropHomePage(QWidget):
    def __init__(self, switch_func):
        super().__init__()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        content = QWidget()
        scroll.setWidget(content)
        content_layout = QVBoxLayout(content)

        # 大豆分组
        content_layout.addWidget(self.create_group("大豆", [
            ("icons/soy_seed.png", "籽粒考种", lambda: switch_func("soy_seed")),
            ("icons/soy_pod.png", "豆荚考种", lambda: switch_func("pod")),
            ("icons/no.png", "植株考种", lambda: switch_func("plant"))
        ]))

        # 小麦分组
        content_layout.addWidget(self.create_group("小麦", [
            ("icons/no.png", "籽粒考种", lambda: switch_func("wheat_seed"))
        ]))

        # 通用分组
        content_layout.addWidget(self.create_group("通用考种", [
            ("icons/count_anything.png", "图像分析", lambda: switch_func("count_anything"))
        ]))

        # 总布局
        layout = QVBoxLayout(self)
        layout.addWidget(scroll)



    def create_group(self, title, card_infos):
        group_box = QGroupBox(title)

        # 设置标题字体
        font = QFont("KaiTi", 20)  # 可以改成你想要的字体和字号

        group_box.setFont(font)

        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignLeft)
        layout.setSpacing(20)  # 设置卡片之间的间距为 20 像素

        for icon, text, cb in card_infos:
            layout.addWidget(CardButton(icon, text, cb))

        group_box.setLayout(layout)
        return group_box


# 豆荚考种页面
class PodPage(QWidget):
    def __init__(self, switch_page_func):  # 接收函数参数
        super().__init__()
        self.ui = PodUi()
        self.init_tools = InitPod(self.ui)

        layout = QVBoxLayout()
        layout.addWidget(self.ui)
        back_btn = QPushButton("返回")
        back_btn.setFixedHeight(10)
        back_btn.clicked.connect(switch_page_func)
        layout.addWidget(back_btn)
        layout.setContentsMargins(0, 0, 0, 0)  # 可选：取消内边距以填满整个区域
        self.setLayout(layout)

class SoySeedPage(QWidget):
    def __init__(self, switch_page_func):  # 接收函数参数
        super().__init__()
        self.ui = SoySeedUi()
        self.init_tools = InitSoySeed(self.ui)

        layout = QVBoxLayout()
        layout.addWidget(self.ui)
        back_btn = QPushButton("返回")
        back_btn.setFixedHeight(10)
        back_btn.clicked.connect(switch_page_func)
        layout.addWidget(back_btn)
        layout.setContentsMargins(0, 0, 0, 0)  # 可选：取消内边距以填满整个区域
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
        back_btn.clicked.connect(switch_page_func)
        layout.addWidget(back_btn)
        layout.setContentsMargins(0, 0, 0, 0)  # 可选：取消内边距以填满整个区域
        self.setLayout(layout)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("考种平台")
        self.setWindowIcon(QIcon("icons/app_icon.png"))
        self.resize(960, 700)

        self.stack = QStackedWidget(self)
        layout = QVBoxLayout(self)
        layout.addWidget(self.stack)

        # 子页面实例
        self.home_page = CropHomePage(self.switch_page)
        self.pod_page = PodPage(lambda: self.switch_page("home"))
        self.soy_seed_page = SoySeedPage(lambda: self.switch_page("home"))
        self.count_anything_page = CountAnythingPage(lambda: self.switch_page("home"))

        self.stack.addWidget(self.home_page)  # index 0
        self.stack.addWidget(self.pod_page)   # index 1
        self.stack.addWidget(self.soy_seed_page)

        self.stack.addWidget(self.count_anything_page)

        # 页面字典
        self.page_dict = {
            "home": self.home_page,
            "pod": self.pod_page,
            "soy_seed": self.soy_seed_page,
            "count_anything": self.count_anything_page,
            # 其他页面可以继续添加
        }
        self.current_page = self.home_page  # 初始页面
        self.stack.setCurrentWidget(self.home_page)

    def switch_page(self, page_name):
        if page_name in self.page_dict:
            next_page = self.page_dict[page_name]
            # 尝试关闭当前页面的 init_tools 中的设备
            if hasattr(self, "current_page") and hasattr(self.current_page, "init_tools"):
                tools = self.current_page.init_tools
                if hasattr(tools, "close_device") and callable(getattr(tools, "close_device")):
                    try:
                        tools.close_device()
                        print("成功关闭当前页面的设备")
                    except Exception as e:
                        print(f"关闭当前页面设备失败: {e}")
            print(f"切换到页面 {page_name}")
            self.stack.setCurrentWidget(self.page_dict[page_name])
            self.current_page = next_page
        else:
            print(f"页面 {page_name} 未注册")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

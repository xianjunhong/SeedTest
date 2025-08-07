import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QGroupBox,
    QHBoxLayout, QPushButton, QStackedWidget, QScrollArea,
    QFrame, QGraphicsDropShadowEffect
)
from PyQt5.QtGui import QPixmap, QFont, QIcon, QColor
from PyQt5.QtCore import Qt

# 页面和工具的引用
from frank.handleModule.count_anything.init_count_anything import InitCountAnything
from frank.handleModule.pod.init_pod import InitPod
from frank.handleModule.soy_seed.init_soy_seed import InitSoySeed
from frank.handleModule.wheat_seed.init_wheat_seed import InitWheatSeed
from frank.uiModule.count_anything.count_anything_ui import CountAnythingUi
from frank.uiModule.image_acquisition.image_acquisition_ui import ImageAcquisitionUi
from frank.handleModule.image_acquisition.init_image_acquisition import InitAcquisition
from frank.uiModule.pod.pod_ui import PodUi
from frank.uiModule.soy_seed.soy_seed_ui import SoySeedUi
from frank.uiModule.wheat_seed.wheat_seed_ui import WheatSeedUi
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
            ("icons/wheat_seed.png", "籽粒考种", lambda: switch_func("wheat_seed"))
        ]))

        # 通用分组
        content_layout.addWidget(self.create_group("通用考种", [
            ("icons/count_anything.png", "图像分析", lambda: switch_func("count_anything")),
            ("icons/orange_cat.png", "图像采集", lambda: switch_func("image_acquisition"))
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



class PodPage(QWidget):
    def __init__(self, switch_back):
        super().__init__()
        self.ui = PodUi()
        self.init_tools = InitPod(self.ui)
        layout = QVBoxLayout()
        layout.addWidget(self.ui)
        back_btn = QPushButton("返回")
        # back_btn.setFixedHeight(10)

        back_btn.clicked.connect(switch_back)
        layout.addWidget(back_btn)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)


class SoySeedPage(QWidget):
    def __init__(self, switch_back):
        super().__init__()
        self.ui = SoySeedUi()
        self.init_tools = InitSoySeed(self.ui)
        layout = QVBoxLayout()
        layout.addWidget(self.ui)
        back_btn = QPushButton("返回")
        # back_btn.setFixedHeight(10)
        back_btn.clicked.connect(switch_back)
        layout.addWidget(back_btn)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)


class CountAnythingPage(QWidget):
    def __init__(self, switch_back):
        super().__init__()
        self.ui = CountAnythingUi()
        self.init_tools = InitCountAnything(self.ui)
        layout = QVBoxLayout()
        layout.addWidget(self.ui)
        back_btn = QPushButton("返回")
        # back_btn.setFixedHeight(10)
        back_btn.clicked.connect(switch_back)
        layout.addWidget(back_btn)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

class ImageAcquisition(QWidget):
    def __init__(self, switch_back):
        super().__init__()
        self.ui = ImageAcquisitionUi()
        self.init_tools = InitAcquisition(self.ui)
        layout = QVBoxLayout()
        layout.addWidget(self.ui)
        back_btn = QPushButton("返回")
        # back_btn.setFixedHeight(10)
        back_btn.clicked.connect(switch_back)
        layout.addWidget(back_btn)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)


class WheatSeedPage(QWidget):
    def __init__(self, switch_back):
        super().__init__()
        self.ui = WheatSeedUi()
        self.init_tools = InitWheatSeed(self.ui)
        layout = QVBoxLayout()
        layout.addWidget(self.ui)
        back_btn = QPushButton("返回")

        back_btn.clicked.connect(switch_back)
        layout.addWidget(back_btn)
        layout.setContentsMargins(0, 0, 0, 0)
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
        # 一个字典，存储已创建的页面实例（键为页面名称，值为页面对象），避免重复创建页面。
        self.page_instances = {}

        # 一个字典，存储页面名称到页面创建函数的映射，页面创建函数是 lambda 表达式，用于延迟实例化页面。
        self.page_creators = {
            "home": lambda: CropHomePage(self.switch_page),
            "pod": lambda: PodPage(lambda: self.switch_page("home")),
            "soy_seed": lambda: SoySeedPage(lambda: self.switch_page("home")),
            "count_anything": lambda: CountAnythingPage(lambda: self.switch_page("home")),
            "image_acquisition": lambda: ImageAcquisition(lambda: self.switch_page("home")),
            "wheat_seed": lambda: WheatSeedPage(lambda: self.switch_page("home")),
            # 添加其他页面创建器
        }

        # 初始化首页
        home = self.page_creators["home"]()
        self.page_instances["home"] = home
        self.stack.addWidget(home)
        self.stack.setCurrentWidget(home)
        self.current_page = home

    def switch_page(self, page_name):
        if page_name not in self.page_creators:
            print(f"页面 {page_name} 未注册")
            return

        # 尝试关闭当前页面设备
        if hasattr(self.current_page, "init_tools"):
            tools = self.current_page.init_tools
            if hasattr(tools, "close_device") and callable(tools.close_device):
                try:
                    tools.close_device()
                    print("成功关闭当前页面设备")
                except Exception as e:
                    print(f"关闭设备失败: {e}")

        if page_name not in self.page_instances:
            page_widget = self.page_creators[page_name]()
            self.page_instances[page_name] = page_widget
            self.stack.addWidget(page_widget)

        self.current_page = self.page_instances[page_name]
        self.stack.setCurrentWidget(self.current_page)
        print(f"切换到页面 {page_name}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

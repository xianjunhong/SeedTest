"""
考种平台 - 主程序
整合考种、图像采集、设置三个模块
"""
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QHBoxLayout, QStackedWidget, QFrame, QGraphicsDropShadowEffect,
    QPushButton
)
from PyQt5.QtGui import QFont, QIcon, QColor
from PyQt5.QtCore import Qt

from common.config_manager import ConfigManager
from common.model_manager import ModelManager
from common.data_manager import DataManager

from modules.seed_inspection.inspection_ui import InspectionUI
from modules.seed_inspection.inspection_handler import InspectionHandler
from modules.image_acquisition.acquisition_ui import AcquisitionUI
from modules.image_acquisition.acquisition_handler import AcquisitionHandler
from modules.settings.settings_ui import SettingsUI
from modules.settings.settings_handler import SettingsHandler

from modules.seed_inspection.model_selection_dialog import ModelSelectionDialog
from utils import create_centered_square_pixmap


class CardButton(QFrame):
    """卡片按钮"""
    
    def __init__(self, icon_path, title, callback):
        super().__init__()
        self.setFixedSize(180, 240)
        self.setStyleSheet("""
            QFrame {
                border-radius: 16px;
                background-color: white;
            }
            QFrame:hover {
                background-color: #f5faff;
            }
        """)
        
        # 阴影效果
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(12)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 60))
        self.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(0)
        
        # 图标
        icon_label = QLabel(self)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_height = int(self.height() * 0.75)
        icon_label.setFixedHeight(icon_height)
        
        icon_size = 100
        icon_label.setPixmap(create_centered_square_pixmap(icon_path, icon_size))
        
        # 文本
        title_label = QLabel(title, self)
        title_label.setFont(QFont("KaiTi", 22, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFixedHeight(int(self.height() * 0.25))
        
        layout.addWidget(icon_label)
        layout.addWidget(title_label)
        
        # 点击事件
        self.mousePressEvent = lambda event: callback()


class HomePage(QWidget):
    """主页"""
    
    def __init__(self, switch_func):
        super().__init__()
        self.switch_func = switch_func
        self.setup_ui()
    
    def setup_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        
        # 标题
        title = QLabel("考种平台")
        title.setFont(QFont("Microsoft YaHei", 28, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #1976d2; margin: 20px;")
        layout.addWidget(title)
        
        # 卡片区域
        cards_layout = QHBoxLayout()
        cards_layout.setAlignment(Qt.AlignCenter)
        cards_layout.setSpacing(30)
        
        # 考种卡片
        inspection_card = CardButton(
            "icons/soy_seed.png",
            "考种",
            lambda: self.switch_func("inspection")
        )
        
        # 图像采集卡片
        acquisition_card = CardButton(
            "icons/pod.png",
            "图像采集",
            lambda: self.switch_func("acquisition")
        )
        
        # 设置卡片
        settings_card = CardButton(
            "icons/count_anything.png",
            "设置",
            lambda: self.switch_func("settings")
        )
        
        cards_layout.addWidget(inspection_card)
        cards_layout.addWidget(acquisition_card)
        cards_layout.addWidget(settings_card)
        
        layout.addLayout(cards_layout)
        layout.addStretch()
        
        # 底部信息
        info = QLabel("Powered by JinLab")
        info.setAlignment(Qt.AlignCenter)
        info.setStyleSheet("color: gray; margin: 10px;")
        layout.addWidget(info)


class MainWindow(QWidget):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("考种平台")
        self.setWindowIcon(QIcon("icons/app_icon.png"))
        self.resize(1200, 800)
        
        # 初始化配置管理器
        self.config_manager = ConfigManager('config.ini')
        
        # 初始化管理器
        self.model_manager = ModelManager(self.config_manager)
        self.data_manager = DataManager(self.config_manager)
        
        # 页面实例
        self.page_instances = {}
        self.handler_instances = {}  # 存储handler实例
        self.current_page = None
        self.current_handler = None
        
        # 创建UI
        self.setup_ui()
    
    def setup_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        
        # 堆叠窗口
        self.stack = QStackedWidget(self)
        layout.addWidget(self.stack)
        
        # 返回按钮（初始隐藏）
        self.btn_back = QPushButton("← 返回主页")
        self.btn_back.setFixedHeight(40)
        self.btn_back.setStyleSheet("""
            QPushButton {
                background-color: #1976d2;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
        """)
        self.btn_back.clicked.connect(lambda: self.switch_page("home"))
        self.btn_back.hide()
        layout.addWidget(self.btn_back)
        
        # 创建主页
        home_page = HomePage(self.switch_page)
        self.page_instances["home"] = home_page
        self.stack.addWidget(home_page)
        self.current_page = home_page
    
    def switch_page(self, page_name):
        """切换页面"""
        # 关闭当前页面的设备
        if self.current_handler:
            try:
                self.current_handler.close_device()
                print("已关闭当前页面设备")
            except Exception as e:
                print(f"关闭设备失败: {e}")
        
        # 特殊处理：考种模块需要先选择模型
        if page_name == "inspection":
            # 显示模型选择对话框
            dialog = ModelSelectionDialog(self.model_manager, self)
            if dialog.exec_() == dialog.Accepted:
                model_name = dialog.get_selected_model()
                if model_name:
                    self._create_inspection_page(model_name)
                else:
                    return  # 取消选择
            else:
                return  # 取消对话框
        else:
            # 创建或获取页面
            if page_name not in self.page_instances:
                if page_name == "acquisition":
                    self._create_acquisition_page()
                elif page_name == "settings":
                    self._create_settings_page()
        
        # 切换页面
        if page_name in self.page_instances:
            self.current_page = self.page_instances[page_name]
            self.stack.setCurrentWidget(self.current_page)
            
            # 更新current_handler（从page_instances获取对应的handler）
            if page_name in self.handler_instances:
                self.current_handler = self.handler_instances[page_name]
            elif page_name == "home":
                self.current_handler = None
            
            # 显示/隐藏返回按钮
            if page_name == "home":
                self.btn_back.hide()
            else:
                self.btn_back.show()
            
            print(f"已切换到: {page_name}")
    
    def _create_inspection_page(self, model_name):
        """创建考种页面"""
        # 如果已存在，先移除
        if "inspection" in self.page_instances:
            old_page = self.page_instances["inspection"]
            self.stack.removeWidget(old_page)
            old_page.deleteLater()
        
        # 创建新页面
        ui = InspectionUI(self.data_manager)
        handler = InspectionHandler(ui, self.config_manager, model_name)
        
        self.page_instances["inspection"] = ui
        self.handler_instances["inspection"] = handler
        self.current_handler = handler
        self.stack.addWidget(ui)
        
        print(f"考种页面已创建，模型: {model_name}")
    
    def _create_acquisition_page(self):
        """创建图像采集页面"""
        ui = AcquisitionUI()
        handler = AcquisitionHandler(ui, self.config_manager)
        
        self.page_instances["acquisition"] = ui
        self.handler_instances["acquisition"] = handler
        self.current_handler = handler
        self.stack.addWidget(ui)
        
        print("图像采集页面已创建")
    
    def _create_settings_page(self):
        """创建设置页面"""
        ui = SettingsUI()
        handler = SettingsHandler(ui, self.config_manager)
        
        self.page_instances["settings"] = ui
        self.handler_instances["settings"] = handler
        self.current_handler = handler
        self.stack.addWidget(ui)
        
        print("设置页面已创建")
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        # 关闭所有设备
        if self.current_handler:
            try:
                self.current_handler.close_device()
            except:
                pass
        event.accept()


def main():
    """主函数"""

    # 高DPI支持
    import os
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    app = QApplication(sys.argv)
    
    # 设置应用样式
    app.setStyle("Fusion")
    
    # 创建主窗口
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    print("高DPI支持")
    main()



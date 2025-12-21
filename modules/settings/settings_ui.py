"""
设置模块 - 主UI
"""
from PyQt5.QtWidgets import QWidget, QVBoxLayout

from .settings_home import SettingsHomePage


class SettingsUI(QWidget):
    """设置模块UI"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        
        # 创建主页面
        self.home_page = SettingsHomePage()
        layout.addWidget(self.home_page)
        
        # 直接暴露home_page的属性，方便访问
        for attr in dir(self.home_page):
            if not attr.startswith('_') and not hasattr(self, attr):
                setattr(self, attr, getattr(self.home_page, attr))


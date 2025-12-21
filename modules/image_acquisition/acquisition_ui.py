"""
图像采集模块 - 主UI
"""
from PyQt5.QtWidgets import QWidget, QVBoxLayout

from .acquisition_home import AcquisitionHomePage
from .acquisition_data import AcquisitionDataPage


class AcquisitionUI(QWidget):
    """图像采集模块UI"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        
        # 创建主页面
        self.home_page = AcquisitionHomePage()
        layout.addWidget(self.home_page)
        
        # 创建数据管理页面
        self.data_page = AcquisitionDataPage()
        self.home_page.data_page = self.data_page
        self.home_page.stacked_widget.addWidget(self.data_page)
        
        # 直接暴露home_page的属性，方便访问
        for attr in dir(self.home_page):
            if not attr.startswith('_') and not hasattr(self, attr):
                setattr(self, attr, getattr(self.home_page, attr))


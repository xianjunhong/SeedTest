"""
考种模块 - 主UI
包含主页和数据页的标签切换
"""
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QStackedWidget
from qfluentwidgets import SegmentedWidget

from .inspection_home import InspectionHomePage
from .inspection_data import InspectionDataPage


class InspectionUI(QWidget):
    """考种模块UI"""
    
    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager
        self.setup_ui()
    
    def setup_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        
        # 标签切换器
        self.pivot = SegmentedWidget()
        
        # 堆叠窗口
        self.stacked_widget = QStackedWidget()
        
        # 创建页面
        self.home_page = InspectionHomePage()
        self.data_page = InspectionDataPage(self.data_manager)
        
        # 添加页面
        self.add_page(self.home_page, 'home', '考种')
        self.add_page(self.data_page, 'data', '数据管理')
        
        # 添加到布局
        layout.addWidget(self.pivot)
        layout.addWidget(self.stacked_widget)
        
        # 设置默认页面
        self.stacked_widget.setCurrentWidget(self.home_page)
        self.pivot.setCurrentItem(self.home_page.objectName())
        
        # 连接切换信号
        self.pivot.currentItemChanged.connect(
            lambda key: self.stacked_widget.setCurrentWidget(self.findChild(QWidget, key))
        )
    
    def add_page(self, widget, object_name, text):
        """添加页面"""
        widget.setObjectName(object_name)
        self.stacked_widget.addWidget(widget)
        self.pivot.addItem(routeKey=object_name, text=text)


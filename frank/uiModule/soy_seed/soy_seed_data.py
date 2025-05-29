from PyQt5.QtWidgets import QTabWidget, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QTableWidget, QFormLayout, QPushButton, QSizePolicy, QHeaderView, QSplitter, QGroupBox, QDesktopWidget, QStackedWidget
from PyQt5.QtCore import Qt,QSize
from PyQt5.QtGui import QFont, QIcon
from qfluentwidgets import (PushButton, PrimaryPushButton,
                            LineEdit, ComboBox, TableWidget, Pivot, SegmentedWidget)

from frank.fieldModule.all_fields import SoySeedFields as FIELDS


class SoySeedData(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        headers = [f.label for f in FIELDS if f.table_visible]

        self.tab_2_layout = QVBoxLayout(self)

        self.table_widget = TableWidget()
        # 不许修改
        self.table_widget.setEditTriggers(QTableWidget.NoEditTriggers)
        # 共有几列
        self.table_widget.setColumnCount(len(headers))
        self.table_widget.setHorizontalHeaderLabels(headers)

        # 能设置表头字体大小，但是点击每行时的特效没了
        # self.table_widget.setStyleSheet("""
        #     QHeaderView::section {      /* 表头样式 */
        #         font: bold 16px "微软雅黑";
        #         color: #2c3e50;
        #     }
        #     """)




        # 默认行高
        self.table_widget.verticalHeader().setDefaultSectionSize(50)

        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.tab_2_layout.addWidget(self.table_widget)

        self.button_export = PrimaryPushButton("导出为 Excel")
        self.button_export.setMinimumHeight(70)
        font = QFont("Arial", 20)
        font.setBold(True)
        self.button_export.setFont(font)


        self.tab_2_layout.addWidget(self.button_export )

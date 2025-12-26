"""
图像采集模块 - 数据管理页面
"""
import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QTableWidget, QTableWidgetItem, QHeaderView, 
                             QMessageBox, QFileDialog, QLabel)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from qfluentwidgets import PushButton, PrimaryPushButton, CardWidget


class AcquisitionDataPage(QWidget):
    """图像采集数据管理页面"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        title = QLabel("数据管理")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title)
        
        # 操作按钮
        btn_layout = QHBoxLayout()
        
        self.btn_refresh = PushButton("刷新")
        self.btn_export_csv = PrimaryPushButton("导出 CSV")
        self.btn_delete_all = PushButton("删除全部")
        self.btn_delete_all.setStyleSheet("background-color: #d32f2f; color: white;")
        
        btn_layout.addWidget(self.btn_refresh)
        btn_layout.addWidget(self.btn_export_csv)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_delete_all)
        
        layout.addLayout(btn_layout)
        
        # 数据表格
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID", "品种编号", "时间", "重量(g)", "文件名", "操作"
        ])
        
        # 设置表格样式
        from PyQt5.QtWidgets import QHeaderView
        
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)  # 禁止编辑
        
        # 设置行高
        self.table.verticalHeader().setDefaultSectionSize(45)  # 增加行高
        
        # 设置列的拉伸模式（响应式布局）
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)      # ID固定
        header.setSectionResizeMode(1, QHeaderView.Stretch)    # 品种编号拉伸
        header.setSectionResizeMode(2, QHeaderView.Stretch)    # 时间拉伸
        header.setSectionResizeMode(3, QHeaderView.Fixed)      # 重量固定
        header.setSectionResizeMode(4, QHeaderView.Stretch)    # 文件名拉伸
        header.setSectionResizeMode(5, QHeaderView.Fixed)      # 操作固定
        
        # 只设置固定列的宽度
        self.table.setColumnWidth(0, 80)   # ID
        self.table.setColumnWidth(3, 80)   # 重量
        self.table.setColumnWidth(5, 200)  # 操作按钮
        
        layout.addWidget(self.table)
        
        self.setLayout(layout)
    
    def add_record_row(self, record, view_callback, delete_callback):
        """
        添加一行记录
        record: 记录字典
        view_callback: 查看回调函数
        delete_callback: 删除回调函数
        """
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        # ID
        item = QTableWidgetItem(str(record.get('id', '')))
        item.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, 0, item)
        
        # 品种编号
        item = QTableWidgetItem(str(record.get('variety_code', '')))
        item.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, 1, item)
        
        # 时间
        item = QTableWidgetItem(str(record.get('timestamp', '')))
        item.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, 2, item)
        
        # 重量
        weight = record.get('weight', 0)
        item = QTableWidgetItem(f"{weight:.2f}" if weight else "0.00")
        item.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, 3, item)
        
        # 文件名
        filename = os.path.basename(record.get('image_path', ''))
        item = QTableWidgetItem(filename)
        item.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, 4, item)
        
        # 操作按钮容器
        btn_view = PrimaryPushButton("查看图像")
        btn_view.setFixedSize(85, 35)  # 适配行高
        btn_view.clicked.connect(lambda: view_callback(record))
        
        btn_delete = QPushButton("删除")
        btn_delete.setFixedSize(75, 35)  # 适配行高
        btn_delete.setStyleSheet("""
            QPushButton {
                background-color: #d32f2f; 
                color: white; 
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #b71c1c;
            }
        """)
        btn_delete.clicked.connect(lambda: delete_callback(record))
        
        cell_widget = QWidget()
        btn_layout = QHBoxLayout(cell_widget)
        btn_layout.addWidget(btn_view)
        btn_layout.addWidget(btn_delete)
        btn_layout.setContentsMargins(8, 5, 8, 5)  # 增加边距
        btn_layout.setSpacing(10)  # 增加按钮间距
        btn_layout.setAlignment(Qt.AlignCenter)  # 居中对齐
        
        self.table.setCellWidget(row, 5, cell_widget)
    
    def clear_table(self):
        """清空表格"""
        self.table.setRowCount(0)


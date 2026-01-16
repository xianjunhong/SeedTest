"""
考种模块 - 数据页面
显示历史记录、查看图像、删除记录、导出Excel
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                              QTableWidget, QTableWidgetItem, QMessageBox, QFileDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from qfluentwidgets import PrimaryPushButton, TableWidget
import os


class InspectionDataPage(QWidget):
    """考种数据管理页面"""
    
    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        
        # 顶部按钮栏
        btn_layout = QHBoxLayout()
        
        self.btn_export = PrimaryPushButton("导出Excel")
        self.btn_refresh = PrimaryPushButton("刷新")
        self.btn_clear_all = PrimaryPushButton("清空所有数据")
        self.btn_clear_all.setStyleSheet("background-color: #d32f2f; color: white;")
        
        btn_layout.addWidget(self.btn_export)
        btn_layout.addWidget(self.btn_refresh)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_clear_all)
        
        layout.addLayout(btn_layout)
        
        # 表格
        self.table_widget = TableWidget()

        data_list = [
            "ID", "时间", "模型", "品种编号", "数量",
            "平均长度(cm)", "平均宽度(cm)", "重量(g)", "千粒重(g)", "操作"
        ]
        self.table_widget.setColumnCount(len(data_list))
        self.table_widget.setHorizontalHeaderLabels(data_list)
        
        # 设置表格样式
        from PyQt5.QtWidgets import QHeaderView
        
        self.table_widget.horizontalHeader().setStretchLastSection(True)
        self.table_widget.setAlternatingRowColors(True)
        self.table_widget.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_widget.setEditTriggers(QTableWidget.NoEditTriggers)  # 禁止编辑
        
        # 设置行高
        self.table_widget.verticalHeader().setDefaultSectionSize(45)  # 增加行高
        
        # 设置列的拉伸模式（响应式布局）
        header = self.table_widget.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)      # ID固定
        header.setSectionResizeMode(1, QHeaderView.Stretch)    # 时间拉伸
        header.setSectionResizeMode(2, QHeaderView.Stretch)    # 模型拉伸
        header.setSectionResizeMode(3, QHeaderView.Stretch)    # 品种编号拉伸
        header.setSectionResizeMode(4, QHeaderView.Fixed)      # 数量固定
        header.setSectionResizeMode(5, QHeaderView.Stretch)    # 平均长度拉伸
        header.setSectionResizeMode(6, QHeaderView.Stretch)    # 平均宽度拉伸
        header.setSectionResizeMode(7, QHeaderView.Fixed)      # 重量固定
        header.setSectionResizeMode(8, QHeaderView.Fixed)      # 千粒重固定
        header.setSectionResizeMode(9, QHeaderView.Fixed)      # 操作固定
        
        # 只设置固定列的宽度
        self.table_widget.setColumnWidth(0, 80)   # ID
        self.table_widget.setColumnWidth(4, 60)   # 数量
        self.table_widget.setColumnWidth(7, 80)   # 重量
        self.table_widget.setColumnWidth(8, 90)   # 千粒重
        self.table_widget.setColumnWidth(9, 200)  # 操作按钮
        
        layout.addWidget(self.table_widget)
        
        # 连接信号
        self.btn_export.clicked.connect(self.export_excel)
        self.btn_refresh.clicked.connect(self.load_data)
        self.btn_clear_all.clicked.connect(self.clear_all_data)
    
    def load_data(self):
        """加载数据到表格"""
        self.table_widget.setRowCount(0)
        records = self.data_manager.load_records()
        
        for record in records:
            self.add_table_row(record)
    
    def add_table_row(self, record):
        """添加一行到表格"""
        row_index = self.table_widget.rowCount()
        self.table_widget.insertRow(row_index)
        
        # 填充数据
        columns = [
            record.get('id', ''),
            record.get('timestamp', ''),
            record.get('model_name', ''),
            record.get('variety_code', ''),
            str(record.get('count', 0)),
            f"{record.get('avg_length', 0):.2f}",
            f"{record.get('avg_width', 0):.2f}",
            f"{record.get('weight', 0):.2f}",
            f"{record.get('thousand_seed_weight', 0):.2f}"
        ]
        
        for col, value in enumerate(columns):
            item = QTableWidgetItem(str(value))
            item.setTextAlignment(Qt.AlignCenter)
            self.table_widget.setItem(row_index, col, item)
        
        # 操作按钮
        btn_view = PrimaryPushButton("查看图像")
        btn_view.setFixedSize(85, 35)  # 适配行高
        btn_view.clicked.connect(lambda: self.view_image(record))
        
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
        btn_delete.clicked.connect(lambda: self.delete_record(record))
        
        cell_widget = QWidget()
        btn_layout = QHBoxLayout(cell_widget)
        btn_layout.addWidget(btn_view)
        btn_layout.addWidget(btn_delete)
        btn_layout.setContentsMargins(8, 5, 8, 5)  # 增加边距
        btn_layout.setSpacing(10)  # 增加按钮间距
        btn_layout.setAlignment(Qt.AlignCenter)  # 居中对齐
        
        self.table_widget.setCellWidget(row_index, 9, cell_widget)
    
    def view_image(self, record):
        """查看图像"""
        image_path = record.get('processed_image_path', '')
        
        if not os.path.exists(image_path):
            QMessageBox.warning(self, "错误", f"图像文件不存在:\n{image_path}")
            return
        
        # 使用系统默认程序打开图像
        try:
            os.startfile(image_path)
        except Exception as e:
            QMessageBox.warning(self, "错误", f"打开图像失败:\n{str(e)}")
    
    def delete_record(self, record):
        """删除记录"""
        record_id = record.get('id', '')
        
        reply = QMessageBox.question(
            self, "删除确认", 
            f"确定要删除记录 {record_id} 吗？\n这将同时删除相关的图像文件。",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success, message = self.data_manager.delete_record(record_id)
            if success:
                QMessageBox.information(self, "成功", message)
                self.load_data()  # 刷新表格
            else:
                QMessageBox.warning(self, "错误", message)
    
    def export_excel(self):
        """导出Excel"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存Excel文件", "", 
            "Excel 文件 (*.xlsx);;CSV 文件 (*.csv)"
        )
        
        if not file_path:
            return
        
        success, message = self.data_manager.export_to_excel(file_path)
        if success:
            QMessageBox.information(self, "成功", message)
        else:
            QMessageBox.warning(self, "错误", message)
    
    def clear_all_data(self):
        """清空所有数据"""
        reply = QMessageBox.question(
            self, "清空确认",
            "⚠️ 警告：此操作将删除所有考种记录和图像文件，且无法恢复！\n\n确定要继续吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success, message = self.data_manager.delete_all_records()
            if success:
                QMessageBox.information(self, "成功", message)
                self.load_data()  # 刷新表格
            else:
                QMessageBox.warning(self, "错误", message)


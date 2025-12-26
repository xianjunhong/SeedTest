"""
图像采集模块 - 主页面
纯图像采集功能，不做AI处理
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QGroupBox, QLineEdit, QPushButton, QComboBox,
                              QGridLayout, QFileDialog, QMessageBox, QStackedWidget, QSizePolicy)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from qfluentwidgets import PrimaryPushButton, SegmentedWidget
import os
import cv2
from datetime import datetime


class AcquisitionHomePage(QWidget):
    """图像采集主页面"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        """初始化UI"""
        main_layout = QVBoxLayout(self)
        
        # 选项卡切换
        self.pivot = SegmentedWidget()
        self.pivot.addItem("acquisition", "图像采集")
        self.pivot.addItem("data", "数据管理")
        self.pivot.setCurrentItem("acquisition")
        
        main_layout.addWidget(self.pivot)
        
        # 页面容器
        self.stacked_widget = QStackedWidget()
        
        # 采集页面
        self.acquisition_page = self._create_acquisition_page()
        self.stacked_widget.addWidget(self.acquisition_page)
        
        # 数据管理页面（稍后由 handler 添加）
        self.data_page = None  # 由 UI 类设置
        
        main_layout.addWidget(self.stacked_widget)
        
        # 连接切换信号
        self.pivot.currentItemChanged.connect(self._on_page_changed)
    
    def _on_page_changed(self, key):
        """页面切换"""
        if key == "acquisition":
            self.stacked_widget.setCurrentIndex(0)
        elif key == "data":
            self.stacked_widget.setCurrentIndex(1)
    
    def _create_acquisition_page(self):
        """创建采集页面"""
        page = QWidget()
        layout = QHBoxLayout(page)
        
        # 左侧：图像显示
        left_layout = QVBoxLayout()
        
        self.widget_display = QLabel()
        self.widget_display.setMinimumSize(480, 360)
        # 移除最大尺寸限制，让显示区域自适应窗口大小
        self.widget_display.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.widget_display.setScaledContents(False)
        self.widget_display.setStyleSheet("border: 2px solid #ccc; background-color: black;")
        self.widget_display.setAlignment(Qt.AlignCenter)
        self.widget_display.setText("相机未启动")
        
        left_layout.addWidget(self.widget_display)
        
        # 控制按钮
        btn_layout = QHBoxLayout()
        self.button_start_preview = PrimaryPushButton("开始预览")
        self.button_capture = PrimaryPushButton("拍照保存")
        self.button_capture.setEnabled(False)
        
        btn_layout.addWidget(self.button_start_preview)
        btn_layout.addWidget(self.button_capture)
        
        left_layout.addLayout(btn_layout)
        
        layout.addLayout(left_layout, 3)
        
        # 右侧：控制面板
        right_layout = QVBoxLayout()
        
        # 相机控制
        cam_group = self._create_camera_group()
        right_layout.addWidget(cam_group)
        
        # 天平控制
        balance_group = self._create_balance_group()
        right_layout.addWidget(balance_group)
        
        # 保存设置
        save_group = self._create_save_group()
        right_layout.addWidget(save_group)
        
        right_layout.addStretch()
        
        layout.addLayout(right_layout, 2)
        
        return page
    
    def _create_camera_group(self):
        """创建相机控制组"""
        group = QGroupBox("相机控制")
        layout = QVBoxLayout()
        
        # 相机选择
        cam_layout = QHBoxLayout()
        self.combo_devices_cam = QComboBox()
        self.btn_enum_cam = QPushButton("扫描相机")
        self.btn_open_cam = PrimaryPushButton("打开相机")
        
        cam_layout.addWidget(QLabel("相机:"))
        cam_layout.addWidget(self.combo_devices_cam, 1)
        cam_layout.addWidget(self.btn_enum_cam)
        layout.addLayout(cam_layout)
        layout.addWidget(self.btn_open_cam)
        
        # 提示文字
        hint_label = QLabel("相机参数请在设置页面调整")
        hint_label.setStyleSheet("color: #666; font-size: 12px;")
        layout.addWidget(hint_label)
        
        group.setLayout(layout)
        return group
    
    def _create_balance_group(self):
        """创建天平控制组"""
        group = QGroupBox("天平控制")
        layout = QVBoxLayout()
        
        # 天平选择
        balance_layout = QHBoxLayout()
        self.combo_balance_port = QComboBox()
        self.btn_scan_balance = QPushButton("扫描天平")
        self.btn_open_balance = PrimaryPushButton("打开天平")
        
        balance_layout.addWidget(QLabel("串口:"))
        balance_layout.addWidget(self.combo_balance_port, 1)
        balance_layout.addWidget(self.btn_scan_balance)
        layout.addLayout(balance_layout)
        layout.addWidget(self.btn_open_balance)
        
        # 天平状态
        status_layout = QHBoxLayout()
        self.label_balance_status = QLabel("未连接")
        self.label_balance_status.setStyleSheet("color: red; font-weight: bold;")
        self.btn_zero_balance = QPushButton("清零")
        self.btn_zero_balance.setEnabled(False)
        
        status_layout.addWidget(QLabel("状态:"))
        status_layout.addWidget(self.label_balance_status, 1)
        status_layout.addWidget(self.btn_zero_balance)
        layout.addLayout(status_layout)
        
        # 重量显示
        weight_layout = QHBoxLayout()
        self.label_weight = QLabel("0.00 g")
        self.label_weight.setStyleSheet("font-size: 18px; font-weight: bold;")
        weight_layout.addWidget(QLabel("重量:"))
        weight_layout.addWidget(self.label_weight, 1)
        layout.addLayout(weight_layout)
        
        group.setLayout(layout)
        return group
    
    def _create_save_group(self):
        """创建保存设置组"""
        group = QGroupBox("保存设置")
        layout = QVBoxLayout()
        
        # 品种编号（必填）
        variety_layout = QHBoxLayout()
        self.input_variety_code = QLineEdit()
        self.input_variety_code.setPlaceholderText("必填，如: V001")
        # 增大字体
        self.input_variety_code.setStyleSheet("""
            QLineEdit {
                font-size: 18px;
                font-weight: bold;
                padding: 8px;
                border: 2px solid #1976d2;
                border-radius: 4px;
            }
            QLineEdit:focus {
                border: 2px solid #0d47a1;
            }
        """)
        
        variety_label = QLabel("品种编号:")
        variety_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        
        variety_layout.addWidget(variety_label)
        variety_layout.addWidget(self.input_variety_code)
        
        layout.addLayout(variety_layout)
        
        # 保存路径
        path_layout = QHBoxLayout()
        self.input_save_path = QLineEdit("data/acquisition")
        self.btn_browse_path = QPushButton("浏览...")
        
        path_layout.addWidget(QLabel("保存路径:"))
        path_layout.addWidget(self.input_save_path, 1)
        path_layout.addWidget(self.btn_browse_path)
        
        layout.addLayout(path_layout)
        
        # 文件名前缀
        prefix_layout = QHBoxLayout()
        self.input_prefix = QLineEdit("img")
        
        prefix_layout.addWidget(QLabel("文件前缀:"))
        prefix_layout.addWidget(self.input_prefix)
        
        layout.addLayout(prefix_layout)
        
        group.setLayout(layout)
        return group
    
    def _create_stats_group(self):
        """创建统计信息组"""
        group = QGroupBox("统计信息")
        layout = QGridLayout()
        
        self.label_capture_count = QLabel("0")
        self.label_capture_count.setStyleSheet("font-size: 24px; font-weight: bold; color: #1976d2;")
        
        layout.addWidget(QLabel("已拍摄:"), 0, 0)
        layout.addWidget(self.label_capture_count, 0, 1)
        layout.addWidget(QLabel("张"), 0, 2)
        
        self.btn_clear_count = QPushButton("清零")
        layout.addWidget(self.btn_clear_count, 1, 0, 1, 3)
        
        group.setLayout(layout)
        return group


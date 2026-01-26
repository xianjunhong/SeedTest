"""
考种模块 - 主页面
相机预览、模型推理、天平称重、保存数据
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QGroupBox, QLineEdit, QPushButton, QComboBox,
                              QGridLayout, QSlider, QProgressBar, QSizePolicy)
from PyQt5.QtCore import Qt
from qfluentwidgets import PrimaryPushButton, SpinBox, DoubleSpinBox
import os


class InspectionHomePage(QWidget):
    """考种主页面"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        """初始化UI"""
        main_layout = QHBoxLayout(self)
        
        # 左侧：图像显示区域
        left_layout = QVBoxLayout()
        
        # 图像显示
        self.widget_display = QLabel()
        self.widget_display.setMinimumSize(480, 360)
        # 移除最大尺寸限制，让显示区域自适应窗口大小
        self.widget_display.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # 拉伸时保持原始比例
        self.widget_display.setScaledContents(False)
        self.widget_display.setStyleSheet("border: 2px solid #ccc; background-color: black;")
        self.widget_display.setAlignment(Qt.AlignCenter)
        self.widget_display.setText("相机未启动")
        
        # Loading 进度条（简洁无限循环进度条）
        self.loading_progress = QProgressBar(self.widget_display)
        self.loading_progress.setFixedSize(400, 30)
        self.loading_progress.setRange(0, 0)  # 不确定进度的循环模式
        self.loading_progress.setTextVisible(False)  # 隐藏文字
        self.loading_progress.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 15px;
                background-color: rgba(200, 200, 200, 150);
            }
            QProgressBar::chunk {
                border-radius: 15px;
                background-color: #2196F3;
            }
        """)
        self.loading_progress.hide()
        
        # 重写widget_display的resizeEvent来居中loading_progress
        original_resize = self.widget_display.resizeEvent
        def new_resize_event(event):
            original_resize(event)
            self._center_loading_progress()
        self.widget_display.resizeEvent = new_resize_event
        
        left_layout.addWidget(self.widget_display)
        
        # 图像控制按钮
        img_btn_layout = QHBoxLayout()
        self.button_live_img = PrimaryPushButton("开始预览")
        self.button_process_img = PrimaryPushButton("处理图像")
        self.button_process_img.setEnabled(False)
        
        img_btn_layout.addWidget(self.button_live_img)
        img_btn_layout.addWidget(self.button_process_img)
        
        left_layout.addLayout(img_btn_layout)
        
        main_layout.addLayout(left_layout, 3)
        
        # 右侧：控制面板
        right_layout = QVBoxLayout()
        
        # 相机控制
        cam_group = self._create_camera_group()
        right_layout.addWidget(cam_group)
        
        # 天平控制
        balance_group = self._create_balance_group()
        right_layout.addWidget(balance_group)
        
        # 检测参数
        detect_group = self._create_detection_group()
        right_layout.addWidget(detect_group)
        
        # 品种信息
        variety_group = self._create_variety_group()
        right_layout.addWidget(variety_group)
        
        # 结果显示
        result_group = self._create_result_group()
        right_layout.addWidget(result_group)
        
        # 保存按钮
        self.button_save_info = PrimaryPushButton("保存数据")
        self.button_save_info.setEnabled(False)
        self.button_save_info.setMinimumHeight(40)
        right_layout.addWidget(self.button_save_info)
        
        right_layout.addStretch()
        
        main_layout.addLayout(right_layout, 1)
    
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
    
    def _create_detection_group(self):
        """创建检测参数组"""
        group = QGroupBox("检测参数")
        layout = QVBoxLayout()
        
        # 置信度
        conf_layout = QHBoxLayout()
        self.slider_confidence = QSlider(Qt.Horizontal)
        self.slider_confidence.setRange(0, 100)
        self.slider_confidence.setValue(25)
        self.label_confidence = QLabel("25.0%")
        
        conf_layout.addWidget(QLabel("置信度:"))
        conf_layout.addWidget(self.slider_confidence, 1)
        conf_layout.addWidget(self.label_confidence)
        layout.addLayout(conf_layout)
        
        # 面积筛选
        area_layout = QHBoxLayout()
        self.slider_area = QSlider(Qt.Horizontal)
        self.slider_area.setRange(0, 50)
        self.slider_area.setValue(5)
        self.label_area = QLabel("5.0%")
        
        area_layout.addWidget(QLabel("面积筛选:"))
        area_layout.addWidget(self.slider_area, 1)
        area_layout.addWidget(self.label_area)
        layout.addLayout(area_layout)
        
        # 连接滑块信号
        self.slider_confidence.valueChanged.connect(
            lambda v: self.label_confidence.setText(f"{v}.0%")
        )
        self.slider_area.valueChanged.connect(
            lambda v: self.label_area.setText(f"{v}.0%")
        )
        
        group.setLayout(layout)
        return group
    
    def _create_variety_group(self):
        """创建品种信息组"""
        group = QGroupBox("品种信息")
        layout = QHBoxLayout()
        
        # 品种编号标签
        variety_label = QLabel("品种编号:")
        variety_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(variety_label)
        
        # 品种编号输入
        self.input_variety_code = QLineEdit()
        self.input_variety_code.setPlaceholderText("必填，如: V001")
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
        layout.addWidget(self.input_variety_code)
        
        group.setLayout(layout)
        return group
    
    def _create_result_group(self):
        """创建结果显示组"""
        group = QGroupBox("检测结果")
        layout = QGridLayout()
        
        self.label_count = QLabel("0")
        self.label_avg_length = QLabel("0.00 cm")
        self.label_avg_width = QLabel("0.00 cm")
        self.label_thousand_weight = QLabel("0.00 g")
        
        # 设置样式
        for label in [self.label_count, self.label_avg_length, 
                      self.label_avg_width, self.label_thousand_weight]:
            label.setStyleSheet("font-size: 16px; font-weight: bold; color: #1976d2;")
        
        layout.addWidget(QLabel("数量:"), 0, 0)
        layout.addWidget(self.label_count, 0, 1)
        layout.addWidget(QLabel("平均长度:"), 1, 0)
        layout.addWidget(self.label_avg_length, 1, 1)
        layout.addWidget(QLabel("平均宽度:"), 2, 0)
        layout.addWidget(self.label_avg_width, 2, 1)
        layout.addWidget(QLabel("千粒重:"), 3, 0)
        layout.addWidget(self.label_thousand_weight, 3, 1)
        
        group.setLayout(layout)
        return group
    
    def _center_loading_progress(self):
        """将loading_progress居中显示在widget_display上"""
        if self.loading_progress and self.widget_display:
            parent_width = self.widget_display.width()
            parent_height = self.widget_display.height()
            progress_width = self.loading_progress.width()
            progress_height = self.loading_progress.height()
            
            x = (parent_width - progress_width) // 2
            y = (parent_height - progress_height) // 2
            
            self.loading_progress.move(x, y)
    
    def update_result_display(self, count, avg_length, avg_width, thousand_weight):
        """更新结果显示"""
        self.label_count.setText(str(count))
        self.label_avg_length.setText(f"{avg_length:.2f} cm")
        self.label_avg_width.setText(f"{avg_width:.2f} cm")
        self.label_thousand_weight.setText(f"{thousand_weight:.2f} g")
    
    def clear_result_display(self):
        """清空结果显示"""
        self.update_result_display(0, 0, 0, 0)


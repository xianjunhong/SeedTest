"""
设置模块 - 主页面
包含相机设置、ROI设置、天平设置等
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QGroupBox, QLineEdit, QPushButton, QComboBox,
                              QGridLayout, QCheckBox, QMessageBox, QTabWidget)
from PyQt5.QtCore import Qt
from qfluentwidgets import PrimaryPushButton, DoubleSpinBox
from .roi_selector import ROISelector


class SettingsHomePage(QWidget):
    """设置主页面"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        """初始化UI"""
        main_layout = QVBoxLayout(self)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        
        # 相机和ROI设置
        camera_tab = self._create_camera_tab()
        self.tab_widget.addTab(camera_tab, "相机与ROI")
        
        # 天平设置
        balance_tab = self._create_balance_tab()
        self.tab_widget.addTab(balance_tab, "天平")
        
        # 检测设置
        detection_tab = self._create_detection_tab()
        self.tab_widget.addTab(detection_tab, "检测")
        
        # 路径设置
        path_tab = self._create_path_tab()
        self.tab_widget.addTab(path_tab, "路径")
        
        main_layout.addWidget(self.tab_widget)
        
        # 底部按钮
        btn_layout = QHBoxLayout()
        self.btn_save_settings = PrimaryPushButton("保存设置")
        self.btn_reset_settings = QPushButton("恢复默认")
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_reset_settings)
        btn_layout.addWidget(self.btn_save_settings)
        
        main_layout.addLayout(btn_layout)
    
    def _create_camera_tab(self):
        """创建相机和ROI设置标签页"""
        tab = QWidget()
        layout = QHBoxLayout(tab)
        
        # 左侧：ROI预览
        left_layout = QVBoxLayout()
        
        left_layout.addWidget(QLabel("<b>ROI 区域设置</b>"))
        
        # ROI选择器
        self.roi_selector = ROISelector()
        left_layout.addWidget(self.roi_selector)
        
        # ROI控制按钮
        roi_btn_layout = QHBoxLayout()
        self.btn_apply_roi = PrimaryPushButton("应用ROI")
        self.btn_apply_roi.setEnabled(False)
        
        roi_btn_layout.addStretch()
        roi_btn_layout.addWidget(self.btn_apply_roi)
        roi_btn_layout.addStretch()
        
        left_layout.addLayout(roi_btn_layout)
        
        layout.addLayout(left_layout, 3)
        
        # 右侧：相机控制
        right_layout = QVBoxLayout()
        
        # 相机选择
        cam_group = QGroupBox("相机控制")
        cam_layout = QVBoxLayout()
        
        select_layout = QHBoxLayout()
        self.combo_camera = QComboBox()
        self.btn_enum_camera = QPushButton("扫描相机")
        self.btn_open_camera = PrimaryPushButton("打开相机")
        
        select_layout.addWidget(QLabel("相机:"))
        select_layout.addWidget(self.combo_camera, 1)
        select_layout.addWidget(self.btn_enum_camera)
        cam_layout.addLayout(select_layout)
        cam_layout.addWidget(self.btn_open_camera)
        
        cam_group.setLayout(cam_layout)
        right_layout.addWidget(cam_group)
        
        # 相机参数
        param_group = QGroupBox("相机参数")
        param_layout = QGridLayout()
        
        self.input_exposure_time = QLineEdit("50000")
        self.input_gain = QLineEdit("0")
        self.input_frame_rate = QLineEdit("30.0")
        self.input_cm_per_pixel = QLineEdit("0.0057")
        
        param_layout.addWidget(QLabel("曝光时间:"), 0, 0)
        param_layout.addWidget(self.input_exposure_time, 0, 1)
        param_layout.addWidget(QLabel("增益:"), 1, 0)
        param_layout.addWidget(self.input_gain, 1, 1)
        param_layout.addWidget(QLabel("帧率:"), 2, 0)
        param_layout.addWidget(self.input_frame_rate, 2, 1)
        param_layout.addWidget(QLabel("cm/像素:"), 3, 0)
        param_layout.addWidget(self.input_cm_per_pixel, 3, 1)
        
        param_group.setLayout(param_layout)
        right_layout.addWidget(param_group)
        
        # ROI参数显示
        roi_param_group = QGroupBox("ROI 参数")
        roi_param_layout = QGridLayout()
        
        self.label_roi_x = QLabel("0")
        self.label_roi_y = QLabel("0")
        self.label_roi_width = QLabel("4000")
        self.label_roi_height = QLabel("3000")
        
        roi_param_layout.addWidget(QLabel("偏移X:"), 0, 0)
        roi_param_layout.addWidget(self.label_roi_x, 0, 1)
        roi_param_layout.addWidget(QLabel("偏移Y:"), 1, 0)
        roi_param_layout.addWidget(self.label_roi_y, 1, 1)
        roi_param_layout.addWidget(QLabel("宽度:"), 2, 0)
        roi_param_layout.addWidget(self.label_roi_width, 2, 1)
        roi_param_layout.addWidget(QLabel("高度:"), 3, 0)
        roi_param_layout.addWidget(self.label_roi_height, 3, 1)
        
        # 翻转选项
        self.check_reverse_x = QCheckBox("X轴翻转")
        self.check_reverse_y = QCheckBox("Y轴翻转")
        self.check_reverse_x.setChecked(True)
        self.check_reverse_y.setChecked(True)
        
        roi_param_layout.addWidget(self.check_reverse_x, 4, 0, 1, 2)
        roi_param_layout.addWidget(self.check_reverse_y, 5, 0, 1, 2)
        
        roi_param_group.setLayout(roi_param_layout)
        right_layout.addWidget(roi_param_group)
        
        right_layout.addStretch()
        
        layout.addLayout(right_layout, 2)
        
        return tab
    
    def _create_balance_tab(self):
        """创建天平设置标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 天平参数
        group = QGroupBox("天平参数")
        grid_layout = QGridLayout()
        
        self.input_balance_port = QLineEdit("COM3")
        self.input_balance_baudrate = QLineEdit("9600")
        self.input_balance_timeout = QLineEdit("1.0")
        
        grid_layout.addWidget(QLabel("串口:"), 0, 0)
        grid_layout.addWidget(self.input_balance_port, 0, 1)
        grid_layout.addWidget(QLabel("波特率:"), 1, 0)
        grid_layout.addWidget(self.input_balance_baudrate, 1, 1)
        grid_layout.addWidget(QLabel("超时(秒):"), 2, 0)
        grid_layout.addWidget(self.input_balance_timeout, 2, 1)
        
        group.setLayout(grid_layout)
        layout.addWidget(group)
        
        layout.addStretch()
        
        return tab
    
    def _create_detection_tab(self):
        """创建检测设置标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 检测参数
        group = QGroupBox("检测参数")
        grid_layout = QGridLayout()
        
        self.input_default_confidence = QLineEdit("25.0")
        self.input_default_area = QLineEdit("5.0")
        self.input_inference_confidence = QLineEdit("0.25")
        
        grid_layout.addWidget(QLabel("默认置信度(%):"), 0, 0)
        grid_layout.addWidget(self.input_default_confidence, 0, 1)
        grid_layout.addWidget(QLabel("默认面积筛选(%):"), 1, 0)
        grid_layout.addWidget(self.input_default_area, 1, 1)
        grid_layout.addWidget(QLabel("推理置信度:"), 2, 0)
        grid_layout.addWidget(self.input_inference_confidence, 2, 1)
        
        # 说明文字
        note = QLabel(
            "<i>提示：<br>"
            "- 默认置信度/面积筛选：滑块的初始值<br>"
            "- 推理置信度：模型推理时的置信度阈值</i>"
        )
        note.setStyleSheet("color: gray;")
        grid_layout.addWidget(note, 3, 0, 1, 2)
        
        group.setLayout(grid_layout)
        layout.addWidget(group)
        
        layout.addStretch()
        
        return tab
    
    def _create_path_tab(self):
        """创建路径设置标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 路径配置
        group = QGroupBox("路径配置")
        grid_layout = QGridLayout()
        
        self.input_models_folder = QLineEdit("models")
        self.input_model_mapping = QLineEdit("models/model_mapping.csv")
        self.input_images_folder = QLineEdit("data/images")
        self.input_processed_folder = QLineEdit("data/processed")
        self.input_data_file = QLineEdit("data/records.json")
        
        grid_layout.addWidget(QLabel("模型文件夹:"), 0, 0)
        grid_layout.addWidget(self.input_models_folder, 0, 1)
        
        grid_layout.addWidget(QLabel("模型映射文件:"), 1, 0)
        grid_layout.addWidget(self.input_model_mapping, 1, 1)
        
        grid_layout.addWidget(QLabel("原图文件夹:"), 2, 0)
        grid_layout.addWidget(self.input_images_folder, 2, 1)
        
        grid_layout.addWidget(QLabel("处理图文件夹:"), 3, 0)
        grid_layout.addWidget(self.input_processed_folder, 3, 1)
        
        grid_layout.addWidget(QLabel("数据文件:"), 4, 0)
        grid_layout.addWidget(self.input_data_file, 4, 1)
        
        # 警告文字
        warning = QLabel(
            "<b>⚠️ 警告：</b><br>"
            "修改路径配置需要重启程序才能生效！"
        )
        warning.setStyleSheet("color: red;")
        grid_layout.addWidget(warning, 5, 0, 1, 2)
        
        group.setLayout(grid_layout)
        layout.addWidget(group)
        
        layout.addStretch()
        
        return tab
    
    def update_roi_display(self, x, y, w, h):
        """更新ROI参数显示"""
        self.label_roi_x.setText(str(x))
        self.label_roi_y.setText(str(y))
        self.label_roi_width.setText(str(w))
        self.label_roi_height.setText(str(h))


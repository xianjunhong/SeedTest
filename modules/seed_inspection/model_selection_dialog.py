"""
模型选择对话框
允许用户选择考种模型
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                              QListWidget, QListWidgetItem, QPushButton,
                              QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from qfluentwidgets import PrimaryPushButton


class ModelSelectionDialog(QDialog):
    """模型选择对话框"""
    
    # 模型类型图标映射
    MODEL_ICONS = {
        'obb': '🔄',      # 旋转框检测 - 旋转图标
        'det': '🎯',      # 普通检测 - 目标图标
        'seg': '✂️',      # 分割检测 - 剪刀图标
        'default': '🤖'   # 默认 - 机器人图标
    }
    
    # 根据模型名称的特殊图标
    NAME_ICONS = {
        'soybean': '🌱',   # 大豆
        'soy': '🫘',       # 豆类
        'wheat': '🌾',     # 小麦
        'pod': '🫛',       # 豆荚
        'seed': '🌰',      # 种子
        'yolo': '⚡',      # YOLO系列
    }
    
    def __init__(self, model_manager, parent=None):
        super().__init__(parent)
        self.model_manager = model_manager
        self.selected_model = None
        self.setup_ui()
        self.load_models()
    
    def setup_ui(self):
        """初始化UI"""
        self.setWindowTitle("选择考种模型")
        self.setMinimumSize(500, 400)
        
        layout = QVBoxLayout(self)
        
        # 标题
        title = QLabel("请选择用于考种的模型")
        title.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # 说明文字
        desc = QLabel(
            "提示：模型文件位于 models/ 文件夹中\n"
            "您可以通过编辑 models/model_mapping.csv 来自定义显示名称"
        )
        desc.setStyleSheet("color: gray;")
        desc.setAlignment(Qt.AlignCenter)
        layout.addWidget(desc)
        
        # 模型列表
        self.list_widget = QListWidget()
        self.list_widget.setAlternatingRowColors(True)
        self.list_widget.itemDoubleClicked.connect(self.accept)
        
        # 设置列表样式 - 增大字体和行高
        list_font = QFont("Microsoft YaHei", 14)  # 增大字体到14号
        self.list_widget.setFont(list_font)
        
        # 设置样式表 - 增加行高和内边距
        self.list_widget.setStyleSheet("""
            QListWidget::item {
                padding: 12px;
                border-bottom: 1px solid #e0e0e0;
            }
            QListWidget::item:selected {
                background-color: #1976d2;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #e3f2fd;
            }
        """)
        
        layout.addWidget(self.list_widget)
        
        # 模型信息显示
        self.info_label = QLabel("请选择一个模型")
        self.info_label.setStyleSheet(
            "border: 1px solid #ccc; "
            "padding: 10px; "
            "background-color: #f5f5f5; "
            "border-radius: 5px;"
        )
        layout.addWidget(self.info_label)
        
        # 按钮
        btn_layout = QHBoxLayout()
        
        self.btn_refresh = QPushButton("刷新列表")
        self.btn_refresh.clicked.connect(self.load_models)
        
        self.btn_cancel = QPushButton("取消")
        self.btn_cancel.clicked.connect(self.reject)
        
        self.btn_ok = PrimaryPushButton("确定")
        self.btn_ok.clicked.connect(self.accept)
        self.btn_ok.setEnabled(False)
        
        btn_layout.addWidget(self.btn_refresh)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_ok)
        
        layout.addLayout(btn_layout)
        
        # 连接信号
        self.list_widget.currentItemChanged.connect(self.on_selection_changed)
    
    def get_model_icon(self, model_file, model_type):
        """根据模型文件名和类型获取合适的图标"""
        # 优先根据文件名中的关键词匹配
        model_file_lower = model_file.lower()
        for keyword, icon in self.NAME_ICONS.items():
            if keyword in model_file_lower:
                return icon
        
        # 其次根据模型类型匹配
        return self.MODEL_ICONS.get(model_type, self.MODEL_ICONS['default'])
    
    def load_models(self):
        """加载模型列表"""
        self.list_widget.clear()
        
        # 扫描模型
        models = self.model_manager.scan_models()
        
        if not models:
            QMessageBox.warning(
                self, "提示",
                "未找到任何模型文件！\n\n"
                "请将 .pt 模型文件放入 models/ 文件夹中。"
            )
            return
        
        # 添加到列表
        for model_file, display_name, model_type in models:
            # 获取合适的图标
            icon = self.get_model_icon(model_file, model_type)
            
            item = QListWidgetItem(f"{icon} {display_name}")
            item.setData(Qt.UserRole, {
                'file': model_file,
                'name': display_name,
                'type': model_type
            })
            
            # 设置提示信息
            item.setToolTip(
                f"文件名: {model_file}\n"
                f"类型: {model_type.upper()}\n"
                f"双击或点击确定以选择"
            )
            
            self.list_widget.addItem(item)
        
        # 默认选中第一个
        if self.list_widget.count() > 0:
            self.list_widget.setCurrentRow(0)
    
    def on_selection_changed(self, current, previous):
        """选择改变"""
        if current:
            data = current.data(Qt.UserRole)
            
            # 更新信息显示
            model_type_desc = {
                'obb': '旋转框检测 (OBB)',
                'det': '普通检测 (DET)',
                'seg': '分割检测 (SEG)'
            }
            
            info_text = (
                f"<b>模型名称：</b>{data['name']}<br>"
                f"<b>文件名：</b>{data['file']}<br>"
                f"<b>模型类型：</b>{model_type_desc.get(data['type'], data['type'])}"
            )
            
            self.info_label.setText(info_text)
            self.btn_ok.setEnabled(True)
        else:
            self.info_label.setText("请选择一个模型")
            self.btn_ok.setEnabled(False)
    
    def accept(self):
        """确认选择"""
        current_item = self.list_widget.currentItem()
        if current_item:
            data = current_item.data(Qt.UserRole)
            self.selected_model = data['file']
            super().accept()
        else:
            QMessageBox.warning(self, "提示", "请选择一个模型")
    
    def get_selected_model(self):
        """获取选中的模型文件名"""
        return self.selected_model


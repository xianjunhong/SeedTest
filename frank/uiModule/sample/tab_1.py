
from PyQt5.QtCore import QSize, QTimer, Qt
from PyQt5.QtGui import QFont, QMovie
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QFormLayout, QHBoxLayout, QLabel, QSizePolicy, QProgressBar
from qfluentwidgets import LineEdit, PrimaryPushButton, PushButton, ComboBox, IndeterminateProgressBar, FluentThemeColor

from ..fieldModule.all_fields import FIELDS


class Tab1Widget(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        # 延迟执行 resize 后的初始化
        QTimer.singleShot(0, self.update_display_area)

    def setup_ui(self):
        self.setObjectName("tab1")
        self.font = QFont()
        self.font.setPointSize(16)

        self.tab_1_layout = QHBoxLayout(self)

        # 左侧布局
        self.left_widget = QWidget()
        self.left_layout = QVBoxLayout(self.left_widget)
        self.left_layout.setContentsMargins(0, 0, 0, 0)

        # 设备选择
        self.combo_devices = QWidget()
        self.left_layout.addWidget(self.combo_devices)
        self.combo_devices_layout = QHBoxLayout(self.combo_devices)
        self.combo_devices_layout.setContentsMargins(0, 0, 0, 0)

        # 下拉框
        self.combo_devices_cam = ComboBox()
        self.combo_devices_cam.setMinimumHeight(30)
        self.combo_devices_layout.addWidget(self.combo_devices_cam, stretch=7)

        # 打开设备按钮
        self.enum_devices_cam_button = PushButton("检索相机")
        self.enum_devices_cam_button.setMinimumHeight(30)
        self.combo_devices_layout.addWidget(self.enum_devices_cam_button, stretch=1)

        # 打开设备按钮
        self.combo_devices_cam_button = PrimaryPushButton("打开相机")
        self.combo_devices_cam_button.setMinimumHeight(30)
        self.combo_devices_layout.addWidget(self.combo_devices_cam_button, stretch=1)

        # 黑色背景容器
        self.background = QWidget()
        self.background_layout = QVBoxLayout(self.background)
        self.background.setMinimumSize(QSize(900, 900))
        self.background_layout.setContentsMargins(0,0,0,0)

        self.background.setStyleSheet("background: black;")
        self.background.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.left_layout.addWidget(self.background)

        # 因为要保持正方形，所以必须写成子组件，不能让布局管理器管理
        self.widget_display = QLabel(self.background)
        # self.widget_display.setStyleSheet("background: gray;")  # 模拟摄像头画面
        self.widget_display.setStyleSheet("""
            QLabel {
                background: black;
                color: white;  
                font-size: 70px;  
                qproperty-alignment: AlignCenter; 
            }
        """)
        self.widget_display.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # 下面这个其实不生效，因为他是background的子组件，只有布局管理器的才生效
        self.widget_display.setMinimumSize(QSize(900, 900))  # 初始最小尺寸


        self.widget_display.setText("请加载相机...")  # 默认显示文字

        # loading动画（放在摄像头显示区域上方）
        self.loading_label = QLabel(self.widget_display)
        self.loading_movie = QMovie(r"frank\uiModule\icon\loading.gif")  # 确保这个GIF文件在项目目录中
        # self.loading_label.setFixedSize(500, images)  # 设置固定大小
        self.loading_label.setMovie(self.loading_movie)
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.loading_label.setStyleSheet("background: transparent;")  # 关键设置
        self.loading_label.setAttribute(Qt.WA_TranslucentBackground)  # 启用透明背景
        self.loading_label.setScaledContents(True)  # 关键设置：允许内容缩放

        # 设置初始大小（按比例缩放）
        self.loading_label.setFixedSize(500, 500)  # 初始大小，会根据窗口调整
        self.loading_label.hide()

        # # 无限旋转进度条（放在摄像头显示区域上方）
        # self.progress_bar = QProgressBar(self.widget_display)
        # self.progress_bar.setRange(0, 0)  # 设置为busy模式（无限循环）
        # self.progress_bar.setFixedWidth(500)  # 设置宽度
        # self.progress_bar.setAlignment(Qt.AlignCenter)  # 文字居中
        # self.progress_bar.hide()  # 默认隐藏

        # 不能让布局管理器管理
        # self.background_layout.addWidget(self.widget_display)


        self.tab_1_layout.addWidget(self.left_widget, stretch=3)

        # 右侧表单
        self.right_widget = QWidget()
        self.right_widget.setMinimumWidth(350)
        self.right_layout = QVBoxLayout(self.right_widget)
        self.right_layout.setContentsMargins(0, 0, 0, 0)

        self.balance_widget = QGroupBox('天平设置')

        self.balance_widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

        # 主布局使用 QFormLayout
        balance_layout = QFormLayout(self.balance_widget)
        balance_layout.setSpacing(10)


        # 第一行：可用串口 + 检索天平按钮

        self.label_devices_ports = QLabel("可用串口：")
        self.label_devices_ports.setFont(self.font)
        self.combo_devices_ports = ComboBox()

        balance_layout.addRow(self.label_devices_ports, self.combo_devices_ports)

        # 第二行：天平读数框（只读）
        self.line_weight_display = LineEdit()
        self.line_weight_display.setReadOnly(True)
        self.line_weight_display.setPlaceholderText("天平读数")
        self.line_weight_display.setMinimumHeight(30)
        self.line_weight_label = QLabel("当前质量：")
        self.line_weight_label.setFont(self.font)
        balance_layout.addRow(self.line_weight_label, self.line_weight_display)

        # 第三行：检索 + 打开 + 清零按钮
        row3_widget = QWidget()
        row3_layout = QHBoxLayout(row3_widget)
        row3_layout.setContentsMargins(0, 0, 0, 0)

        row3_layout.setSpacing(10)
        self.btn_scan_ports = PushButton("检索")
        self.btn_open_balance = PushButton("打开")
        self.btn_tare_balance = PushButton("清零")

        self.btn_scan_ports.setMinimumHeight(40)
        self.btn_open_balance.setMinimumHeight(40)
        self.btn_tare_balance.setMinimumHeight(40)

        row3_layout.addWidget(self.btn_scan_ports)
        row3_layout.addWidget(self.btn_open_balance)
        row3_layout.addWidget(self.btn_tare_balance)

        balance_layout.addRow(row3_widget)



        # 添加到界面布局（比如右侧布局）
        self.right_layout.addWidget(self.balance_widget)

        self.handle_widget = QGroupBox('采集')
        self.handle_widget.setEnabled(False)
        self.handle_layout = QVBoxLayout(self.handle_widget)



        self.form_widget = QWidget()

        self.form_layout = QFormLayout(self.form_widget)

        self.input_widgets = {}  # 存储 name -> QLineEdit 映射


        for field in FIELDS:
            if not field.form_visible:
                continue
            label = QLabel(f"{field.label}：")
            label.setFont(self.font)

            input_box = LineEdit()
            input_box.setFont(self.font)
            input_box.setMinimumHeight(30)

            self.form_layout.addRow(label, input_box)
            self.input_widgets[field.name] = input_box  # 存下来供其他函数用




        self.handle_layout.addWidget(self.form_widget)

        self.buttons_layout = QHBoxLayout()
        self.buttons_layout.setSpacing(10)

        self.button_live_img = PushButton("实时图像")
        self.button_live_img.setFont(self.font)
        self.button_live_img.setMinimumHeight(40)
        self.buttons_layout.addWidget(self.button_live_img)

        self.button_process_img = PushButton("处理图像")
        self.button_process_img.setFont(self.font)
        self.button_process_img.setMinimumHeight(40)
        self.buttons_layout.addWidget(self.button_process_img)
        self.handle_layout.addLayout(self.buttons_layout)



        self.button_save_layout = QVBoxLayout()
        self.button_save_info = PrimaryPushButton("保存信息")
        self.button_save_info.setFont(self.font)
        self.button_save_info.setMinimumHeight(40)
        self.button_save_layout.addWidget(self.button_save_info)
        self.handle_layout.addLayout(self.button_save_layout)


        self.cam_param = QGroupBox('相机参数')
        self.cam_param.setEnabled(False)
        self.cam_param_layout = QFormLayout(self.cam_param)
        self.cam_param_layout.setSpacing(10)
        # 曝光
        self.label_ExposureTime = QLabel("曝光：")
        self.label_ExposureTime.setFont(self.font)
        self.input_ExposureTime = LineEdit()
        self.input_ExposureTime.setFont(self.font)
        self.input_ExposureTime.setMinimumHeight(30)
        self.cam_param_layout.addRow(self.label_ExposureTime, self.input_ExposureTime)

        self.label_Gain = QLabel("增益：")
        self.label_Gain.setFont(self.font)
        self.input_Gain = LineEdit()
        self.input_Gain.setFont(self.font)
        self.input_Gain.setMinimumHeight(30)
        self.cam_param_layout.addRow(self.label_Gain, self.input_Gain)

        self.label_FrameRate = QLabel("帧率：")
        self.label_FrameRate.setFont(self.font)
        self.input_FrameRate = LineEdit()
        self.input_FrameRate.setFont(self.font)
        self.input_FrameRate.setMinimumHeight(30)
        self.cam_param_layout.addRow(self.label_FrameRate, self.input_FrameRate)

        self.button_set_param = PushButton("设置参数")
        self.button_set_param.setFont(self.font)
        self.button_set_param.setMinimumHeight(40)
        self.cam_param_layout.addRow(self.button_set_param)

        self.right_layout.addWidget(self.handle_widget)
        self.right_layout.addWidget(self.cam_param)
        self.tab_1_layout.addWidget(self.right_widget, stretch=1)

    def update_display_area(self):
        print('init update_display_area')
        parent_size = self.background.size()
        side = min(parent_size.width(), parent_size.height())

        x = (parent_size.width() - side) // 2
        y = (parent_size.height() - side) // 2

        self.widget_display.setGeometry(x, y, side, side)

    def resizeEvent(self, event):
        print('resizeEvent called')
        self.update_display_area()
        super().resizeEvent(event)


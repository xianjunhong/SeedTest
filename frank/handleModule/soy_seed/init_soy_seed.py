import configparser
import json
import os
import uuid
from collections import OrderedDict
from datetime import datetime
from qfluentwidgets import InfoBar, InfoBarIcon, InfoBarPosition
from PyQt5.QtCore import Qt

import cv2
import numpy as np
import pandas as pd
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QTableWidgetItem, QMessageBox, QFileDialog
from qfluentwidgets import PrimaryPushButton
from serial.tools import list_ports

from frank.aiModule import soy_pod
from frank.fieldModule.all_fields import SoySeedFields as FIELDS
from frank.handleModule.CamOperation_class import CameraOperation
from frank.handleModule.my_thread.balance_thread import BalanceThread
from frank.handleModule.my_thread.camera_thread import CameraThread
from frank.handleModule.my_thread.img_processing_thread import ImageProcessingThread
from frank.handleModule.my_thread.model_loader_thread import ModelLoaderThread
from frank.handleModule.my_thread.sahi_img_processing_thread import SahiImageProcessingThread
from frank.handleModule.tools import cam_tool
from frank.hikModule.MvCameraControl_class import *
from frank.hikModule.MvErrorDefine_const import *


class InitSoySeed:
    def __init__(self, ui):
        self.ui = ui
        self.deviceList = None
        self.cam = None
        self.cam_thread = None
        self.last_frame = None
        self.processed_img = None

        # 定义变量obj_cam_operation，用于存储相机操作对象
        self.obj_cam_operation = None
        # 用于指示相机是否处于打开状态
        self.cam_is_open = False
        self.balance_thread = None
        self.balance_is_open = False
        self.balance_data = 0.0
        # 置信度
        self.select_confidence_radio = 0.0
        # 面积
        self.select_area_radio = 0.0
        self.dect_results = None
        # 读取配置文件
        self.load_config()

        self.connect_signals()
        self.dect_model = None
        self.have_load_model = False

    def load_config(self):
        # 读取配置文件
        config = configparser.ConfigParser()
        # 读的是相对start的路径
        config.read('config.ini')
        # 获取 ROI 配置
        self.roi_offset_y = config.getint('ROI', 'roi_offset_y')
        self.roi_offset_x = config.getint('ROI', 'roi_offset_x')
        self.roi_width = config.getint('ROI', 'roi_width')
        self.roi_height = config.getint('ROI', 'roi_height')
        self.reverse_x = config.getboolean('Reverse', 'reverse_x')
        self.reverse_y = config.getboolean('Reverse', 'reverse_y')
        self.CamExposureTime = config.getfloat('Cam', 'ExposureTime')
        self.CamGain = config.getfloat('Cam', 'Gain')
        self.CamFrameRate = config.getfloat('Cam', 'FrameRate')
        self.CmPerPixel = config.getfloat('Cam', 'CmPerPixel')

        self.ImageFolder = config.get('SoySeed', 'ImageFolder')
        self.ProcessedImageFolder = config.get('SoySeed', 'ProcessedImageFolder')
        # 如果文件夹路径不存在，则建立
        if not os.path.exists(self.ImageFolder):
            os.makedirs(self.ImageFolder)
        if not os.path.exists(self.ProcessedImageFolder):
            os.makedirs(self.ProcessedImageFolder)
        self.DataFile = config.get('SoySeed', 'DataFile')
        directory = os.path.dirname(self.DataFile)
        # 如果目录不存在，创建父目录
        if directory:
            os.makedirs(directory, exist_ok=True)
        # 检查 JSON 文件是否存在
        if not os.path.exists(self.DataFile):
            # 创建新的 JSON 文件，写入空列表
            with open(self.DataFile, 'w') as f:
                json.dump([], f)
            print(f"在 {self.DataFile} 创建了新的 JSON 文件，包含空列表")

        self.EnableSaveInfo = config.getboolean('SoySeed', 'EnableSaveInfo')
        self.ModulePath = config.get('SoySeed', 'ModulePath')




    def connect_signals(self):
        # 打开相机
        self.ui.tab_1.combo_devices_cam_button.clicked.connect(self.toggle_device)
        # 枚举相机
        self.ui.tab_1.enum_devices_cam_button.clicked.connect(self.enum_devices)
        # 枚举天平
        self.ui.tab_1.btn_scan_ports.clicked.connect(self.enum_ports)

        # 打开天平
        self.ui.tab_1.btn_open_balance.clicked.connect(self.open_ports)
        self.ui.tab_1.btn_tare_balance.clicked.connect(self.zero_balance)

        # 设置参数
        self.ui.tab_1.button_set_param.clicked.connect(self.set_param)
        # 保存信息
        self.ui.tab_1.button_save_info.clicked.connect(self.save_info)
        # 显示实时图像
        self.ui.tab_1.button_live_img.clicked.connect(self.open_device)
        # 处理图像
        self.ui.tab_1.button_process_img.clicked.connect(self.process_img)
        # 导出excel
        self.ui.tab_2.button_export.clicked.connect(self.export_to_excel)
        # 清空表格和json
        self.ui.tab_2.clear_all.clicked.connect(self.clear_table_and_json)

        self.ui.tab_1.select_confidence_input.valueChanged.connect(self.update_confidence_radio)
        self.ui.tab_1.select_area_input.valueChanged.connect(self.update_area_radio)

        # 加载模型，预热模型
        self.load_model(self.ModulePath)
        # # 从json加载信息
        self.load_table_data()

    def load_model(self,model_path):
        # self.cam_is_open = True
        # self.enable_controls()
        print("正在加载模型...")
        # 提示开始加载模型
        InfoBar.info(
            title='模型加载中',
            content='正在加载目标检测模型，请稍候...',
            orient=Qt.Horizontal,
            isClosable=False,
            position=InfoBarPosition.TOP,
            duration=0,  # duration=0 表示持续显示直到手动关闭
            parent=self.ui
        )

        self.model_thread = ModelLoaderThread(model_path)
        self.model_thread.model_loaded.connect(self.on_model_loaded)
        self.model_thread.load_failed.connect(self.on_model_failed)
        self.model_thread.start()

    def on_model_loaded(self, model):
        self.dect_model = model
        print("模型加载完成 ✅")
        self.have_load_model = True
        InfoBar.success(
            title='模型加载成功',
            content='目标检测模型已成功加载！',
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=3000,
            parent=self.ui  # 必须是 InfoBar 所在的窗口对象
        )

    def on_model_failed(self, error_msg):
        print(error_msg)
        self.have_load_model = False
        InfoBar.error(
            title='模型加载失败',
            content=f'错误信息: {error_msg}',
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=-1,  # 不自动关闭
            parent=self.ui
        )

    def toggle_device(self):
        if self.cam_is_open:
            self.close_cam()
            if not self.cam_is_open:
                self.ui.tab_1.combo_devices_cam_button.setText("打开相机")
            #     展示一张全黑的图到display函数
            # 创建一张黑图（480高 x 640宽 x 3通道）
            black_image = np.zeros((480, 640, 3), dtype=np.uint8)
            # 显示黑图
            self.display_image(black_image)

        else:
            if self.have_load_model ==  False:
                QMessageBox.warning(self.ui, "Error", '请等待模型加载！', QMessageBox.Ok)
                return
            self.open_device()
            if self.cam_is_open:
                self.ui.tab_1.combo_devices_cam_button.setText("关闭相机")

    def enum_devices(self):
        self.deviceList = cam_tool.enum_devices()
        if self.deviceList is None:
            QMessageBox.warning(self.ui, "Error", '未检索到相机!', QMessageBox.Ok)
            return MV_E_CALLORDER

        dev_list = cam_tool.identify_different_devices(self.deviceList)
        # 清空设备组合框中的当前项
        self.ui.tab_1.combo_devices_cam.clear()
        # 将设备列表添加到设备组合框中
        self.ui.tab_1.combo_devices_cam.addItems(dev_list)
        # 设置设备组合框的当前索引为第一个项
        self.ui.tab_1.combo_devices_cam.setCurrentIndex(0)

    def enum_ports(self):

        dev_list = [port.device for port in list_ports.comports()]
        print(dev_list)
        # for port in ports:
        #     # 根据你的设备描述自行修改关键字，比如 'USB Serial', 'Arduino' 等
        #     if "USB Serial" in port.description:
        #         return port.device
        # 清空设备组合框中的当前项
        self.ui.tab_1.combo_devices_ports.clear()
        # 将设备列表添加到设备组合框中
        self.ui.tab_1.combo_devices_ports.addItems(dev_list)
        # 设置设备组合框的当前索引为第一个项
        self.ui.tab_1.combo_devices_ports.setCurrentIndex(0)
        if not dev_list:
            QMessageBox.warning(self.ui, "Error", 'No serial port detected!', QMessageBox.Ok)

    # 打开相机并开始取流
    def open_device(self):
        if self.cam_is_open:
            QMessageBox.warning(self.ui, "Error", 'Camera is Running!', QMessageBox.Ok)
            return MV_E_CALLORDER

        # 获取用户选择相机索引
        select_cam_index = self.ui.tab_1.combo_devices_cam.currentIndex()
        if select_cam_index < 0:
            QMessageBox.warning(self.ui, "Error", 'Please select a camera!', QMessageBox.Ok)
            return MV_E_CALLORDER

        self.cam, _ = cam_tool.creat_camera(self.deviceList, select_cam_index)
        # 第四个参数代表相机已经开启
        self.obj_cam_operation = CameraOperation(self.cam, self.deviceList, select_cam_index, True)

        # ch:打开设备 | en:Open device
        ret = self.cam.MV_CC_OpenDevice(MV_ACCESS_Exclusive, 0)
        if 0 != ret:
            strError = "Open device1 failed ret:" + cam_tool.ToHexStr(ret)
            QMessageBox.warning(self.ui, "Error", strError, QMessageBox.Ok)
            self.cam_is_open = False
        else:
            # 设置ROI
            ret = self.obj_cam_operation.set_roi(self.roi_offset_x, self.roi_offset_y, self.roi_width, self.roi_height, self.reverse_x, self.reverse_y)
            if ret != 0:
                strError = "Set ROI failed ret:" + cam_tool.ToHexStr(ret)
                QMessageBox.warning(self.ui, "Error", strError, QMessageBox.Ok)
                return ret

            # 获取以往的参数
            self.get_param()

            # 自动开启相机
            self.start_camera()
            self.enable_controls()

    # 打开天平
    def open_ports(self):
        if self.balance_is_open:
            QMessageBox.warning(self.ui, "Error", 'Balance is Running!', QMessageBox.Ok)
            return MV_E_CALLORDER

        # 获取用户选择天平索引
        select_balance_index = self.ui.tab_1.combo_devices_ports.currentIndex()
        if select_balance_index < 0:
            QMessageBox.warning(self.ui, "Error", 'Please select a balance!', QMessageBox.Ok)
            return MV_E_CALLORDER

        self.balance_thread = BalanceThread(self.ui.tab_1.combo_devices_ports.currentText())
        self.balance_thread.data_received.connect(self.update_balance)

        self.balance_thread.start()
        self.balance_is_open = True

    # 更新天平信息
    def update_balance(self, data):
        self.balance_data = data
        self.ui.tab_1.line_weight_display.setText(data + 'g')

    # 清零天平
    def zero_balance(self):
        if not self.balance_is_open:
            QMessageBox.warning(self.ui, "Error", 'Balance is not open!', QMessageBox.Ok)
            return
        self.balance_thread.zero_balance()

    # 开启相机
    def start_camera(self):
        if self.cam_is_open:
            QMessageBox.warning(self.ui, "Error", 'Camera is Running!', QMessageBox.Ok)
            return
        self.clear_inputs()

        self.cam_is_open = True
        cam_tool.start_grab(self.cam)
        self.cam_thread = CameraThread(self.cam)
        self.cam_thread.image_update.connect(self.update_image)
        self.cam_thread.start()
        print('相机线程开启')

    # 一直更新图像
    def update_image(self, img):
        # 如果没有启动线程，直接return
        if not self.cam_thread:
            return
        self.last_frame = img.copy()  # 保存最后一帧
        height, width = img.shape[:2]
        frame_width = self.ui.tab_1.widget_display.width()
        frame_height = self.ui.tab_1.widget_display.height()
        scale = min(frame_width / width, frame_height / height)
        new_width = int(width * scale)
        new_height = int(height * scale)
        img_resized = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_LINEAR)
        h, w, ch = img_resized.shape
        bytes_per_line = ch * w
        qt_image = QImage(img_resized.data, w, h, bytes_per_line, QImage.Format_BGR888)
        self.ui.tab_1.widget_display.setPixmap(QPixmap.fromImage(qt_image))

    # ch: 获取参数
    def get_param(self):
        # 设置自动曝光
        # ret = self.cam.MV_CC_SetEnumValue("ExposureAuto", 1)
        # if ret == MV_OK:
        #     return
        # 如果设置自动曝光失败，则设置手动曝光

        ret = self.obj_cam_operation.Get_parameter()
        if ret != MV_OK:
            strError = "Get param failed ret:" + cam_tool.ToHexStr(ret)
            QMessageBox.warning(self.ui, "Error", strError, QMessageBox.Ok)
        else:
            print('获得参数成功')
            self.ui.tab_1.input_ExposureTime.setText("{0:.2f}".format(self.CamExposureTime))
            self.ui.tab_1.input_Gain.setText("{0:.2f}".format(self.CamGain))
            self.ui.tab_1.input_FrameRate.setText("{0:.2f}".format(self.CamFrameRate))
            # 设置初始化参数
            ret = self.obj_cam_operation.Set_parameter(self.CamFrameRate, self.CamExposureTime, self.CamGain)
            if ret != MV_OK:
                strError = "Set param failed ret:" + cam_tool.ToHexStr(ret)
                QMessageBox.warning(self.ui, "Error", strError, QMessageBox.Ok)

    # ch: 设置参数 | en:set param
    def set_param(self):
        frame_rate = float(self.ui.tab_1.input_FrameRate.text() or self.CamFrameRate)
        exposure = float(self.ui.tab_1.input_ExposureTime.text() or self.CamExposureTime)
        gain = float(self.ui.tab_1.input_Gain.text() or self.CamGain)
        print(f"frame_rate = {frame_rate}")

        if cam_tool.is_float(frame_rate) != True or cam_tool.is_float(exposure) != True or cam_tool.is_float(gain) != True:
            strError = "Set param failed ret:" + cam_tool.ToHexStr(MV_E_PARAMETER)
            QMessageBox.warning(self.ui, "Error", strError, QMessageBox.Ok)
            return MV_E_PARAMETER

        ret = self.obj_cam_operation.Set_parameter(frame_rate, exposure, gain)
        if ret != MV_OK:
            strError = "Set param failed ret:" + cam_tool.ToHexStr(ret)
            QMessageBox.warning(self.ui, "Error", strError, QMessageBox.Ok)

        return MV_OK

    # ch: 设置控件状态 | en:set enable status
    def enable_controls(self):

        # 拍摄图像
        self.ui.tab_1.handle_widget.setEnabled(self.cam_is_open)
        self.ui.tab_1.button_save_info.setEnabled(self.cam_is_open)
        # 设置参数
        self.ui.tab_1.cam_param.setEnabled(self.cam_is_open)
        self.ui.tab_1.button_set_param.setEnabled(self.cam_is_open)
        print("enable_controls完成")

    def close_cam(self):
        if self.cam_thread:
            self.cam_thread.stop()
            # 停止取流
            self.cam.MV_CC_StopGrabbing()
            self.cam_thread = None
            self.cam_is_open = False
            self.cam.MV_CC_CloseDevice()
    def close_balance(self):
        if self.balance_thread:
            self.balance_thread.stop()
            self.balance_thread = None
            self.balance_is_open = False

    def close_device(self):
        self.close_balance()
        self.close_cam()

        print('关闭设备')


    def save_info(self):

        # uuid随机一个file_name
        uid = str(uuid.uuid4().int)[:8]  # 生成 8 位短 UUID

        # 保存处理后的图像
        if float(self.balance_data) < 0.0:
            QMessageBox.warning(self.ui, "Error", "天平信息异常", QMessageBox.Ok)
            return




        # 打开这一行，可以做到直接能够保存信息
        if self.EnableSaveInfo:
            if self.processed_img is None:
                self.processed_img = self.last_frame

        # 保存处理后的图像
        if self.processed_img is not None:
            cv2.imwrite(os.path.join(self.ProcessedImageFolder, f"processed_{uid}.jpg"), self.processed_img)
        else:
            QMessageBox.warning(self.ui, "Error", "保存失败", QMessageBox.Ok)
            return

        # 图像存储在lase_frame中，将该图像保存到self.ImageFolder/uid.jpg
        if self.last_frame is not None:
            cv2.imwrite(os.path.join(self.ImageFolder, f"{uid}.jpg"), self.last_frame)
        else:
            QMessageBox.warning(self.ui, "Error", "保存失败", QMessageBox.Ok)
            return

        # 提取表单的信息，只提取form可见信息，如果你还想在table添加其他信息，下面添加即可
        record = self.extract_inputs()

        # 生成产品名称（如果用户未输入）
        if not record['name']:
            record['name'] = uid

        # 计算图片的 **绝对路径**
        file_path = os.path.abspath(os.path.join(self.ProcessedImageFolder, f"processed_{uid}.jpg"))

        # 获取当前时间
        now = datetime.now()
        # **格式化创建时间**
        create_time = now.strftime('%Y-%m-%d %H:%M:%S')  # 2025-03-06 15:30:45

        # 在record中添加额外数据
        # 将id添加到第一位，方便导入excel在第一个
        record = OrderedDict([("id", uid)] + list(record.items()))
        record['create_time'] = create_time
        record['file_path'] = file_path
        record['weight'] = self.balance_data

        # 保存数据到 JSON
        cam_tool.save_to_json(self.DataFile, record)

        # 在表格中添加信息
        self.add_to_table_row(record)
        QMessageBox.information(self.ui, "成功", f"图片已保存: {file_path}", QMessageBox.Ok)

        #清空ui.tab_1.input_id
        self.clear_inputs()
        # 显示实时画面
        self.open_device()
        # 清理processed_img
        self.processed_img = None

    def clear_inputs(self):
        for field in FIELDS:
            if field.form_visible == False:
                continue
            widget = self.ui.tab_1.input_widgets[field.name]
            widget.setText(str(field.default))

    # 将信息填入到form中
    def fill_inputs(self, data: dict):
        for field in FIELDS:
            if field.form_visible == False:
                continue
            value = data.get(field.name, field.default)

            formatted = str(value)

            widget = self.ui.tab_1.input_widgets[field.name]

            # 如果已经有文本了，就不要set了
            # if widget.text() != "":
            #     continue
            widget.setText(formatted)

    # 提取form的信息，只提取可见信息
    def extract_inputs(self) -> dict:
        result = {}
        for field in FIELDS:
            if field.form_visible == False:
                continue
            text = self.ui.tab_1.input_widgets[field.name].text()
            try:
                result[field.name] = field.dtype(text)
            except:
                result[field.name] = field.default
        return result

    def process_img(self):
        # 可以继续采集
        print('进入process_img')
        # 停止线程
        self.close_cam()
        if self.last_frame is None:
            return

        # tmp_img = cv2.imread(r'display_img/16.jpg')
        # self.last_frame = tmp_img

        # 显示loading动画
        self.ui.tab_1.loading_movie.start()  # 开始播放动画
        self.ui.tab_1.loading_label.show()
        self.ui.tab_1.loading_label.move(
            self.ui.tab_1.widget_display.width() // 2 - self.ui.tab_1.loading_label.width() // 2,
            self.ui.tab_1.widget_display.height() // 2 - self.ui.tab_1.loading_label.height() // 2
        )



        # 禁用按钮防止重复点击
        self.ui.tab_1.button_process_img.setEnabled(False)
        self.ui.tab_1.button_live_img.setEnabled(False)
        # 这是调试用的，我不想拍摄画面，直接把图片写死


        # 输入图像，处理图像
        # self.pod_thread = ImageProcessingThread(tmp_img,self.dect_model)


        # 创建 SAHI 处理线程
        # self.pod_thread = ImageProcessingThread(self.last_frame, self.dect_model)
        self.pod_thread = SahiImageProcessingThread(self.last_frame, self.dect_model)
        self.pod_thread.result_ready.connect(self.handle_image_result)
        self.pod_thread.start()

    # 处理图像结果
    def handle_image_result(self, results):

        # if len(results.object_prediction_list) == 0 or self.last_frame is None:
        #     return
        # if len(results[0]) == 0 or self.last_frame is None:
        #     return
        # self.processed_img = self.paint_dect_result(results,self.last_frame.copy(),self.select_confidence_radio,self.select_area_radio)
        self.processed_img = self.paint_sahi_dect_result(results,self.last_frame.copy(),self.select_confidence_radio,self.select_area_radio)
        self.display_image(self.processed_img)
        self.dect_results = results


    # 用来将图像展示到pixmap
    
    def display_image(self, img):

        frame_width = self.ui.tab_1.widget_display.width()
        frame_height = self.ui.tab_1.widget_display.height()

        img_resized = cam_tool.scale_img(img, frame_width, frame_height)

        h, w, ch = img_resized.shape
        bytes_per_line = w * ch
        qt_image = QImage(img_resized.data, w, h, bytes_per_line, QImage.Format_BGR888)
        self.ui.tab_1.widget_display.setPixmap(QPixmap.fromImage(qt_image))
        """处理完成后恢复UI"""
        self.ui.tab_1.loading_movie.stop()  # 停止动画
        self.ui.tab_1.loading_label.hide()
        # self.ui.tab_1.progress_bar.hide()  # 隐藏进度条
        # 重新启用按钮
        self.ui.tab_1.button_live_img.setEnabled(True)
        self.ui.tab_1.button_process_img.setEnabled(True)

    def load_table_data(self):
        """ 启动时加载 pod.json 填充 table_widget """
        self.ui.tab_2.table_widget.setRowCount(0)  # 清空表格
        data = cam_tool.load_json(self.DataFile)

        for record in data:
            self.add_to_table_row(record)

    # 增加一条记录到表格
    def add_to_table_row(self, record):
        """ 在 table_widget 中添加一行 """
        row_index = self.ui.tab_2.table_widget.rowCount()
        self.ui.tab_2.table_widget.insertRow(row_index)

        visible_fields = [f for f in FIELDS if f.table_visible]

        for col, field in enumerate(visible_fields):

            if col == len(visible_fields) - 1:
                break

            value = record.get(field.name, field.default)

            # 格式化 float：保留两位小数
            if isinstance(value, float):
                value_str = f"{value:.2f}"
            else:
                value_str = str(value)

            item = QTableWidgetItem(value_str)
            item.setTextAlignment(Qt.AlignCenter)  # 水平+垂直居中
            self.ui.tab_2.table_widget.setItem(row_index, col, item)

        # font = QFont("Arial")
        # font.setBold(True)
        # item.setFont(font)

        # 创建操作按钮（查看、删除）
        btn_view = PrimaryPushButton("查看")
        btn_view.clicked.connect(lambda: cam_tool.open_image(self.ui, record["file_path"]))

        btn_delete = PrimaryPushButton("删除")
        btn_delete.clicked.connect(lambda: self.delete_record(record["id"]))

        # 添加按钮到最后一列，len(record)
        cell_widget = QWidget()
        layout = QHBoxLayout()
        layout.addWidget(btn_view)
        layout.addWidget(btn_delete)
        layout.setContentsMargins(5, 5, 5, 5)
        cell_widget.setLayout(layout)
        self.ui.tab_2.table_widget.setCellWidget(row_index, len(visible_fields) - 1, cell_widget)

    # 删除某条记录
    def delete_record(self, id):

        """ 删除选中的数据行，并从 pod.json 移除 """
        reply = QMessageBox.question(self.ui, "删除确认", "确定要删除该记录吗？", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.No:
            return

        # 从表格中删除
        for i in range(self.ui.tab_2.table_widget.rowCount()):
            # id一定是第0列
            # 找到编号为id的列
            if self.ui.tab_2.table_widget.item(i, 0).text() == id:
                self.ui.tab_2.table_widget.removeRow(i)
                break

        # 从 pod.json 里删除
        data = cam_tool.load_json(self.DataFile)

        new_data = [record for record in data if record["id"] != id]

        with open(self.DataFile, "w", encoding="utf-8") as f:
            json.dump(new_data, f, indent=4, ensure_ascii=False)

        # 在文件夹里删除
        file_path = os.path.join(self.ImageFolder, f"{id}.jpg")

        if os.path.exists(file_path):
            os.remove(file_path)
        print(f"{id}已删除")

    def export_to_excel(self):
        """ 从 pod.json 导出数据为 Excel 并情况json数据 """
        file_path, _ = QFileDialog.getSaveFileName(self.ui, "保存 Excel 文件", "", "Excel 文件 (*.xlsx);;CSV 文件 (*.csv)")

        if not file_path:
            return

        try:
            # 加载 pod.json 数据
            data = cam_tool.load_json(self.DataFile)
            df = pd.DataFrame(data)

            # 导出到指定路径（CSV 或 Excel）
            if file_path.endswith(".csv"):
                df.to_csv(file_path, index=False, encoding="utf-8-sig")
            else:
                df.to_excel(file_path, index=False, engine="openpyxl")



            QMessageBox.information(self.ui, "导出成功", f"数据已成功导出至:\n{file_path}", QMessageBox.Ok)

        except Exception as e:
            QMessageBox.warning(self.ui, "错误", f"导出失败: {str(e)}", QMessageBox.Ok)



    def clear_table_and_json(self):

        # 清空前发出警告
        reply = QMessageBox.question(self.ui, "清空确认", "确定要清空所有数据吗？", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.No:
            return
        """ 清空 table_widget 和 pod.json 数据 """
        # 清空表格
        self.ui.tab_2.table_widget.setRowCount(0)

        # 清空 pod.json 文件
        with open(self.DataFile, "w", encoding="utf-8") as f:
            json.dump([], f, indent=4, ensure_ascii=False)

    def paint_dect_result(self, results, img, select_confidence_radio, select_area_radio):
        # 获取图像的高度、宽度和通道数
        h, w, _ = img.shape
        # 计算点半径，基于图像最小边长，设置最小值为1
        point_radius = max(int(min(w, h) * 0.005), 1)
        # 设置点的颜色为蓝色 (BGR格式)
        point_color = (0, 0, 243)
        # 设置填充厚度为-1，表示填充圆
        thickness = -1
        print(f"box个数为:{len(results[0])}")
        # 从YOLO结果中提取边界框坐标和置信度分数
        boxes = results[0].boxes.xyxy  # [x1, y1, x2, y2] 坐标
        scores = results[0].boxes.conf  # 置信度分数
        if boxes is None or scores is None:
            # 传入的要是一个字典
            result = dict()
            # result["num"] = len(results[0])
            result["num"] = 0
            # 将结果填充到form
            self.fill_inputs(result)
            return img  # 如果没有结果，返回原图

        # 根据边界框计算面积
        areas = [(x2 - x1) * (y2 - y1) for x1, y1, x2, y2 in boxes]
        if not areas:
            # 传入的要是一个字典
            result = dict()
            # result["num"] = len(results[0])
            result["num"] = 0
            # 将结果填充到form
            self.fill_inputs(result)
            return img  # 如果没有有效面积，返回原图

        # 面积排序
        sorted_areas = sorted(areas)
        # 计算保留的面积下限（排除最小 select_area_radio %）
        cutoff_index = int(len(sorted_areas) * (select_area_radio / 100.0))
        # 小于这个面积的全部被过滤掉
        area_threshold = sorted_areas[cutoff_index] if cutoff_index < len(sorted_areas) else sorted_areas[-1]

        cnt = 0
        # 开始绘制
        for i, (x1, y1, x2, y2) in enumerate(boxes):
            area = areas[i]
            confidence = scores[i]
            center_x = int((x1 + x2) / 2)  # 计算中心点x坐标
            center_y = int((y1 + y2) / 2)  # 计算中心点y坐标

            # 过滤条件
            if confidence < (select_confidence_radio / 100.0):
                continue  # 置信度低于阈值，跳过
            if area < area_threshold:
                continue  # 面积低于阈值，跳过
            cnt += 1
            cv2.circle(img, (center_x, center_y), point_radius, point_color, thickness)  # 绘制圆点
        print(cnt)
        # 结果存储为字典
        result = dict()
        result["num"] = cnt  # 记录通过过滤的检测数量
        # 将结果填充到表单
        self.fill_inputs(result)

        return img  # 返回绘制后的图像

    def paint_sahi_dect_result(self, results, img, select_confidence_radio, select_area_radio):
        # 获取图像的高度、宽度和通道数
        h, w, _ = img.shape
        # 计算点半径，基于图像最小边长，设置最小值为1
        point_radius = max(int(min(w, h) * 0.005), 1)
        # 设置点的颜色为蓝色 (BGR格式)
        point_color = (0, 0, 243)
        # 设置填充厚度为-1，表示填充圆
        thickness = -1

        boxes = results.object_prediction_list

        # 先按面积排序，找出面积的百分位阈值
        # 取出所有面积
        areas = [box.bbox.area for box in boxes]
        if not areas:
            return img  # 没有结果直接返回原图

        # 面积排序
        sorted_areas = sorted(areas)
        # 计算保留的面积下限（排除最小 select_area_radio %）
        cutoff_index = int(len(sorted_areas) * (select_area_radio / 100.0))
        # 小于这个面积的全部被过滤掉
        area_threshold = sorted_areas[cutoff_index] if cutoff_index < len(sorted_areas) else sorted_areas[-1]

        cnt = 0
        length = 0
        width = 0
        # 开始绘图
        for box in boxes:
            x1, y1, x2, y2 = box.bbox.to_xyxy()
            area = box.bbox.area
            confidence = box.score.value
            center_x = int((x1 + x2) / 2)
            center_y = int((y1 + y2) / 2)

            # 换成cm
            length += max(x2 - x1, y2 - y1) * self.CmPerPixel
            width += min(x2 - x1, y2 - y1) * self.CmPerPixel

            # 过滤条件
            if confidence < (select_confidence_radio / 100.0):
                continue
            if area < area_threshold:
                continue
            cnt += 1
            cv2.circle(img, (center_x, center_y), point_radius, point_color, thickness)

        print(f"cnt:{cnt}")
        # 传入的要是一个字典
        result = dict()
        # result["num"] = len(results[0])
        result["num"] = cnt
        # 保留两位小数

        result["length"] = round(length / cnt, 2)

        result["width"] = round(width / cnt, 2)
        # 将结果填充到form
        self.fill_inputs(result)

        return img

    def update_confidence_radio(self,val):
        self.select_confidence_radio = val
        # self.processed_img = self.paint_dect_result(self.dect_results, self.last_frame.copy(), self.select_confidence_radio, self.select_area_radio)
        self.processed_img = self.paint_sahi_dect_result(self.dect_results, self.last_frame.copy(), self.select_confidence_radio, self.select_area_radio)
        self.display_image(self.processed_img)


    def  update_area_radio(self,val):
        self.select_area_radio = val
        # self.processed_img = self.paint_dect_result(self.dect_results, self.last_frame.copy(), self.select_confidence_radio, self.select_area_radio)
        self.processed_img = self.paint_sahi_dect_result(self.dect_results, self.last_frame.copy(), self.select_confidence_radio, self.select_area_radio)
        self.display_image(self.processed_img)

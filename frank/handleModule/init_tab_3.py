
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import *
from .CamOperation_class import CameraOperation

from ..hikModule.MvCameraControl_class import *
from ..hikModule.MvErrorDefine_const import *
from ..hikModule.CameraParams_header import *
from ..uiModule import ui
import ctypes
import configparser
import json
import os
import webbrowser
import uuid
from datetime import datetime
import pandas as pd
from PyQt5.QtWidgets import QTableWidgetItem, QPushButton, QMessageBox, QFileDialog, QHeaderView
from qfluentwidgets import MessageDialog, MessageBox, setTheme, Theme, PrimaryPushButton, PushButton, StateToolTip, InfoBar, InfoBarPosition, InfoBarIcon




# 将返回的错误码转换为十六进制显示
def ToHexStr(num):
    chaDic = {10: 'a', 11: 'b', 12: 'c', 13: 'd', 14: 'e', 15: 'f'}
    hexStr = ""
    if num < 0:
        num = num + 2 ** 32
    while num >= 16:
        digit = num % 16
        hexStr = chaDic.get(digit, str(digit)) + hexStr
        num //= 16
    hexStr = chaDic.get(num, str(num)) + hexStr
    return hexStr

# Decoding Characters
def decoding_char(c_ubyte_value):
    c_char_p_value = ctypes.cast(c_ubyte_value, ctypes.c_char_p)
    try:
        decode_str = c_char_p_value.value.decode('gbk')  # Chinese characters
    except UnicodeDecodeError:
        decode_str = str(c_char_p_value.value)
    return decode_str
def is_float(str):
    try:
        float(str)
        return True
    except ValueError:
        return False


def open_image(file_path):
    """ 使用默认应用程序打开图片 """
    webbrowser.open(file_path)



class InitTab3:
    def __init__(self,ui):



        self.ui = ui
        MvCamera.MV_CC_Initialize()
        self.device_list = MV_CC_DEVICE_INFO_LIST()
        self.cam = MvCamera()
        # select_cam_index，用于指定当前选中的相机索引
        self.select_cam_index = 0
        # 定义变量obj_cam_operation，用于存储相机操作对象
        self.obj_cam_operation = 0
        # 用于指示相机是否处于打开状态
        self.is_open = False
        # 读取配置文件
        self.load_config()
        
        

    def load_config(self):
        # 读取配置文件
        config = configparser.ConfigParser()
        # 读的是相对start的路径
        config.read('./frank/handleModule/config.ini')
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
        self.ImageFolder = config.get('SavePath', 'ImageFolder')
        self.DataFile = config.get('Data', 'DataFile')

        self.ui.tab_3.combo_devices_cam_button.clicked.connect(self.open_device)
        self.ui.tab_3.enum_devices_cam_button.clicked.connect(self.enum_devices)
        self.ui.tab_3.button_set_param.clicked.connect(self.set_param)
        self.ui.tab_3.button_save_info.clicked.connect(self.save_info)




        # 自动枚举设备
        self.enum_devices()

        # # 从json加载信息
        self.load_table_data()
        
        
        # 连接清除按钮信号
        self.ui.tab_3.btn_clear.clicked.connect(self.ui.tab_3.widget_display.clear_rects)
        # self.ui.tab_3.btn_rect_choose.clicked.connect()
        self.ui.tab_3.btn_rect_choose.clicked.connect(self.ui.tab_3.widget_display.toggle_drawing_mode)

        # 点击实时画面则开启相机
        self.ui.tab_3.live_image_btn.clicked.connect(self.open_device)

        # 切换画面
        self.ui.tab_3.btn_rect_choose.clicked.connect(self.switch_screen)

        # 连接信号（在现有初始化代码中添加）
        self.ui.tab_3.widget_display.detectionStarted.connect(self.show_detection_status)
        self.ui.tab_3.widget_display.detectionFinished.connect(self.hide_detection_status)


        #    切换画面
        # self.ui.tab_3.button_save_info.clicked.connect(self.switch_screen)

    def enum_devices(self):

        self.device_list = MV_CC_DEVICE_INFO_LIST()

        n_layer_type = (MV_GIGE_DEVICE | MV_USB_DEVICE | MV_GENTL_CAMERALINK_DEVICE
                        | MV_GENTL_CXP_DEVICE | MV_GENTL_XOF_DEVICE)
        ret = MvCamera.MV_CC_EnumDevices(n_layer_type, self.device_list)
        if ret != 0:
            strError = "Enum devices fail! ret = :" + ToHexStr(ret)
            QMessageBox.warning(self.ui, "Error", strError, QMessageBox.Ok)
            return ret

        if self.device_list.nDeviceNum == 0:
            QMessageBox.warning(self.ui, "Info", "Find no device", QMessageBox.Ok)
            return ret
        print("Find %d devices!" % self.device_list.nDeviceNum)

        devList = []
        for i in range(0, self.device_list.nDeviceNum):
            mvcc_dev_info = cast(self.device_list.pDeviceInfo[i], POINTER(MV_CC_DEVICE_INFO)).contents
            if mvcc_dev_info.nTLayerType == MV_GIGE_DEVICE or mvcc_dev_info.nTLayerType == MV_GENTL_GIGE_DEVICE:
                print("\ngige device: [%d]" % i)
                user_defined_name = decoding_char(mvcc_dev_info.SpecialInfo.stGigEInfo.chUserDefinedName)
                model_name = decoding_char(mvcc_dev_info.SpecialInfo.stGigEInfo.chModelName)
                print("device user define name: " + user_defined_name)
                print("device model name: " + model_name)

                nip1 = ((mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0xff000000) >> 24)
                nip2 = ((mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x00ff0000) >> 16)
                nip3 = ((mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x0000ff00) >> 8)
                nip4 = (mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x000000ff)
                print("current ip: %d.%d.%d.%d " % (nip1, nip2, nip3, nip4))
                devList.append(
                    "[" + str(i) + "]GigE: " + user_defined_name + " " + model_name + "(" + str(nip1) + "." + str(
                        nip2) + "." + str(nip3) + "." + str(nip4) + ")")
            elif mvcc_dev_info.nTLayerType == MV_USB_DEVICE:
                print("\nu3v device: [%d]" % i)
                user_defined_name = decoding_char(mvcc_dev_info.SpecialInfo.stUsb3VInfo.chUserDefinedName)
                model_name = decoding_char(mvcc_dev_info.SpecialInfo.stUsb3VInfo.chModelName)
                print("device user define name: " + user_defined_name)
                print("device model name: " + model_name)

                strSerialNumber = ""
                for per in mvcc_dev_info.SpecialInfo.stUsb3VInfo.chSerialNumber:
                    if per == 0:
                        break
                    strSerialNumber = strSerialNumber + chr(per)
                print("user serial number: " + strSerialNumber)
                devList.append("[" + str(i) + "]USB: " + user_defined_name + " " + model_name
                               + "(" + str(strSerialNumber) + ")")
            elif mvcc_dev_info.nTLayerType == MV_GENTL_CAMERALINK_DEVICE:
                print("\nCML device: [%d]" % i)
                user_defined_name = decoding_char(mvcc_dev_info.SpecialInfo.stCMLInfo.chUserDefinedName)
                model_name = decoding_char(mvcc_dev_info.SpecialInfo.stCMLInfo.chModelName)
                print("device user define name: " + user_defined_name)
                print("device model name: " + model_name)

                strSerialNumber = ""
                for per in mvcc_dev_info.SpecialInfo.stCMLInfo.chSerialNumber:
                    if per == 0:
                        break
                    strSerialNumber = strSerialNumber + chr(per)
                print("user serial number: " + strSerialNumber)
                devList.append("[" + str(i) + "]CML: " + user_defined_name + " " + model_name
                               + "(" + str(strSerialNumber) + ")")
            elif mvcc_dev_info.nTLayerType == MV_GENTL_CXP_DEVICE:
                print("\nCXP device: [%d]" % i)
                user_defined_name = decoding_char(mvcc_dev_info.SpecialInfo.stCXPInfo.chUserDefinedName)
                model_name = decoding_char(mvcc_dev_info.SpecialInfo.stCXPInfo.chModelName)
                print("device user define name: " + user_defined_name)
                print("device model name: " + model_name)

                strSerialNumber = ""
                for per in mvcc_dev_info.SpecialInfo.stCXPInfo.chSerialNumber:
                    if per == 0:
                        break
                    strSerialNumber = strSerialNumber + chr(per)
                print("user serial number: " + strSerialNumber)
                devList.append("[" + str(i) + "]CXP: " + user_defined_name + " " + model_name
                               + "(" + str(strSerialNumber) + ")")
            elif mvcc_dev_info.nTLayerType == MV_GENTL_XOF_DEVICE:
                print("\nXoF device: [%d]" % i)
                user_defined_name = decoding_char(mvcc_dev_info.SpecialInfo.stXoFInfo.chUserDefinedName)
                model_name = decoding_char(mvcc_dev_info.SpecialInfo.stXoFInfo.chModelName)
                print("device user define name: " + user_defined_name)
                print("device model name: " + model_name)

                strSerialNumber = ""
                for per in mvcc_dev_info.SpecialInfo.stXoFInfo.chSerialNumber:
                    if per == 0:
                        break
                    strSerialNumber = strSerialNumber + chr(per)
                print("user serial number: " + strSerialNumber)
                devList.append("[" + str(i) + "]XoF: " + user_defined_name + " " + model_name
                               + "(" + str(strSerialNumber) + ")")

        print(devList)

        # 清空设备组合框中的当前项
        self.ui.tab_3.combo_devices_cam.clear()
        # 将设备列表添加到设备组合框中
        self.ui.tab_3.combo_devices_cam.addItems(devList)
        # 设置设备组合框的当前索引为第一个项
        self.ui.tab_3.combo_devices_cam.setCurrentIndex(0)

        # ch:打开相机 | en:open device
        # 额外增加获取参数 + 取流

        # 打开相机并开始取流

    def open_device(self):
        if self.is_open:
            QMessageBox.warning(self.ui, "Error", 'Camera is Running!', QMessageBox.Ok)
            return MV_E_CALLORDER

        # 获取用户选择相机索引

        self.select_cam_index = self.ui.tab_3.combo_devices_cam.currentIndex()
        if self.select_cam_index < 0:
            QMessageBox.warning(self.ui, "Error", 'Please select a camera!', QMessageBox.Ok)
            return MV_E_CALLORDER

        self.obj_cam_operation = CameraOperation(self.cam, self.device_list, self.select_cam_index)
        ret = self.obj_cam_operation.open_device()

        if 0 != ret:
            strError = "Open device failed ret:" + ToHexStr(ret)
            QMessageBox.warning(self.ui, "Error", strError, QMessageBox.Ok)
            self.is_open = False
        else:
            # 设置ROI

            ret = self.obj_cam_operation.set_roi(self.roi_offset_x, self.roi_offset_y, self.roi_width, self.roi_height, self.reverse_x, self.reverse_y)
            if ret != 0:
                strError = "Set ROI failed ret:" + ToHexStr(ret)
                QMessageBox.warning(self.ui, "Error", strError, QMessageBox.Ok)
                return ret
            print('即将获取参数')
            # 获取以往的参数
            self.get_param()
            self.is_open = True
            print('即将取流')
            # 自动取流
            self.start_grabbing()

        # ch:开始取流 | en:Start grab image

    def start_grabbing(self):
        print('start_garbbing')
        ret = self.obj_cam_operation.Start_grabbing(self.ui.tab_3.widget_display.winId())
        print(ret)
        if ret != 0:
            strError = "Start grabbing failed ret:" + ToHexStr(ret)
            QMessageBox.warning(self.ui, "Error", strError, QMessageBox.Ok)
        else:
            self.enable_controls()

        # ch: 获取参数 | en:get param

    def get_param(self):
        ret = self.obj_cam_operation.Get_parameter()
        if ret != MV_OK:
            strError = "Get param failed ret:" + ToHexStr(ret)
            QMessageBox.warning(self.ui, "Error", strError, QMessageBox.Ok)
        else:

            print('获得参数成功')

            self.ui.tab_3.input_ExposureTime.setText("{0:.2f}".format(self.CamExposureTime))
            self.ui.tab_3.input_Gain.setText("{0:.2f}".format(self.CamGain))
            self.ui.tab_3.input_FrameRate.setText("{0:.2f}".format(self.CamFrameRate))
            # 设置初始化参数
            ret = self.obj_cam_operation.Set_parameter(self.CamFrameRate, self.CamExposureTime, self.CamGain)
            if ret != MV_OK:
                strError = "Set param failed ret:" + ToHexStr(ret)
                QMessageBox.warning(self.ui, "Error", strError, QMessageBox.Ok)

        # ch: 设置参数 | en:set param

    def set_param(self):

        frame_rate = self.ui.tab_3.input_FrameRate.text()
        exposure = self.ui.tab_3.input_ExposureTime.text()
        gain = self.ui.tab_3.input_Gain.text()

        if is_float(frame_rate) != True or is_float(exposure) != True or is_float(gain) != True:
            strError = "Set param failed ret:" + ToHexStr(MV_E_PARAMETER)
            QMessageBox.warning(self.ui, "Error", strError, QMessageBox.Ok)
            return MV_E_PARAMETER

        ret = self.obj_cam_operation.Set_parameter(frame_rate, exposure, gain)
        if ret != MV_OK:
            strError = "Set param failed ret:" + ToHexStr(ret)
            QMessageBox.warning(self.ui, "Error", strError, QMessageBox.Ok)

        return MV_OK

        # ch: 设置控件状态 | en:set enable status

    def enable_controls(self):

        # 拍摄图像
        self.ui.tab_3.form_widget.setEnabled(self.is_open)
        self.ui.tab_3.button_save_info.setEnabled(self.is_open)
        # 设置参数
        self.ui.tab_3.cam_param.setEnabled(self.is_open)
        self.ui.tab_3.button_set_param.setEnabled(self.is_open)
        print("enable_controls完成")

    def close_device(self):
        if self.is_open:
            print('关闭相机啦')
            self.obj_cam_operation.Close_device()
            # ch:反初始化SDK | en: finalize SDK
            MvCamera.MV_CC_Finalize()
            self.is_open = False

    def save_info(self):

        # uuid随机一个file_name
        uid = str(uuid.uuid4().int)[:8]  # 生成 8 位短 UUID

        # 保存图片
        ret, file_name = self.obj_cam_operation.Save_jpg(self.ImageFolder, uid)
        if ret != MV_OK:
            QMessageBox.warning(self.ui, "Error", f"保存图片失败: {ToHexStr(ret)}", QMessageBox.Ok)
            return

        # 生成产品名称（如果用户未输入）
        product_name = self.ui.tab_3.input_name.text().strip()
        if not product_name:
            product_name = uid
        product_id = uid

        # 计算图片的 **绝对路径**
        file_path = os.path.abspath(os.path.join(self.ImageFolder, f"{uid}.jpg"))

        # 获取当前时间
        now = datetime.now()
        # **格式化创建时间**
        create_time = now.strftime('%Y-%m-%d %H:%M:%S')  # 2025-03-06 15:30:45

        # 保存数据到 JSON
        record = {"product_id": product_id, "product_name": product_name, "create_time": create_time, "file_path": file_path}
        self.save_to_json(record)

        # 在表格中添加信息
        self.add_to_table(product_id, product_name, create_time, file_path)

        QMessageBox.information(self.ui, "成功", f"图片已保存: {file_path}", QMessageBox.Ok)

        #     清空ui.tab_1.input_id
        self.ui.tab_3.input_name.clear()

    def load_json(self):
        """ 加载 pod.json 文件 """
        if os.path.exists(self.DataFile):
            try:
                with open(self.DataFile, "r", encoding="utf-8") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return []  # 解析错误，返回空列表
        return []

    def load_table_data(self):
        """ 启动时加载 pod.json 填充 table_widget """
        self.ui.tab_2.table_widget.setRowCount(0)  # 清空表格
        data = self.load_json()

        for record in data:
            self.add_to_table(record["product_id"], record["product_name"], record["create_time"], record["file_path"])

    def save_to_json(self, record):
        """ 保存数据到 pod.json """
        data = self.load_json()
        data.append(record)  # 添加新记录

        with open(self.DataFile, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def add_to_table(self, product_id, product_name, create_time, file_path):
        """ 在 table_widget 中添加一行 """
        row_count = self.ui.tab_2.table_widget.rowCount()
        self.ui.tab_2.table_widget.insertRow(row_count)

        # 添加产品编号
        item = QTableWidgetItem(product_id)

        item.setTextAlignment(Qt.AlignCenter)  # 水平+垂直居中

        self.ui.tab_2.table_widget.setItem(row_count, 0, item)

        # 添加产品名称
        item = QTableWidgetItem(product_name)
        item.setTextAlignment(Qt.AlignCenter)
        font = QFont("Arial")
        font.setBold(True)
        item.setFont(font)
        self.ui.tab_2.table_widget.setItem(row_count, 1, item)

        # 添加创建时间
        item = QTableWidgetItem(create_time)
        item.setTextAlignment(Qt.AlignCenter)

        self.ui.tab_2.table_widget.setItem(row_count, 2, item)

        # 创建操作按钮（查看、删除）
        btn_view = PrimaryPushButton("查看")
        btn_view.clicked.connect(lambda: open_image(file_path))

        btn_delete = PrimaryPushButton("删除")
        btn_delete.clicked.connect(lambda: self.delete_record(product_id))

        # 添加按钮到第三列
        cell_widget = QWidget()
        layout = QHBoxLayout()
        layout.addWidget(btn_view)
        layout.addWidget(btn_delete)
        layout.setContentsMargins(5, 5, 5, 5)
        cell_widget.setLayout(layout)
        self.ui.tab_2.table_widget.setCellWidget(row_count, 3, cell_widget)



    def switch_screen(self):
        print('switch_screen')
        # 保存图像，返回地址，关闭摄像头，切换画面
        # self.ui.tab_3.cam_widget_display.save_image()
        # uuid随机一个file_name
        if not self.is_open:
            return
        uid = str(uuid.uuid4().int)[:8]  # 生成 8 位短 UUID
        # 保存图片
        ret, file_name = self.obj_cam_operation.Save_jpg(self.ImageFolder, uid)
        if ret != MV_OK:
            QMessageBox.warning(self.ui, "Error", f"保存图片失败: {ToHexStr(ret)}", QMessageBox.Ok)
            return
        print(file_name)
        self.close_device()
        self.ui.tab_3.widget_display.set_image(os.path.join(self.ImageFolder, file_name))


    def show_detection_status(self):
        """ 显示检测状态提示 """
        print('show_detection_status')
        # self.ui.tab_3.stateTooltip.setContent('正在推理')
        # self.ui.tab_3.stateTooltip.move(510, 30)
        # self.ui.tab_3.stateTooltip.show()
        w = InfoBar(
            icon=InfoBarIcon.INFORMATION,
            title='',
            content="推理中ing",
            orient=Qt.Horizontal,
            isClosable=False,
            position=InfoBarPosition.TOP,
            # position='Custom',   # NOTE: use custom info bar manager
            duration=2000,
            parent=self.ui.tab_3.widget_display
        )
        w.show()

    def hide_detection_status(self):
        """ 隐藏检测状态提示 """
        print('hide_detection_status')
        # self.ui.tab_3.stateTooltip.setContent('完成啦 😆')
        InfoBar.success(
            title='',
            content="推理完毕",
            orient=Qt.Horizontal,
            isClosable=False,
            position=InfoBarPosition.TOP,
            # position='Custom',   # NOTE: use custom info bar manager
            duration=2000,
            parent=self.ui.tab_3.widget_display
        )
        # 推理完毕以后解除选择框的按钮状态
        self.ui.tab_3.btn_rect_choose.setChecked(False)
        # 取消画框
        self.ui.tab_3.widget_display.toggle_drawing_mode()


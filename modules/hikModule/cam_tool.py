


# 将返回的错误码转换为十六进制显示
import ctypes
from ctypes import byref
import json
import os
import subprocess
import sys
import traceback
import numpy as np

import cv2
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage
from PyQt5.QtWidgets import QMessageBox
from serial.tools import list_ports


from .CameraParams_const import MV_USB_DEVICE
from .CameraParams_header import MV_CC_DEVICE_INFO_LIST, MV_CC_DEVICE_INFO, MV_FRAME_OUT
from .MvCameraControl_class import MvCamera
from .MvErrorDefine_const import MV_OK
from .PixelType_header import PixelType_Gvsp_RGB8_Packed


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

# 枚举设备
def enum_devices():
    """
    device = 0  枚举网口、USB口、未知设备、cameralink 设备
    device = 1 枚举GenTL设备
    """

    tlayerType = MV_USB_DEVICE
    deviceList = MV_CC_DEVICE_INFO_LIST()
    # 枚举设备
    ret = MvCamera.MV_CC_EnumDevices(tlayerType, deviceList)
    if ret != 0:
        print("enum devices fail! ret[0x%x]" % ret)
        return None
    if deviceList.nDeviceNum == 0:
        print("find no device!")
        return None
    print("Find %d devices!" % deviceList.nDeviceNum)
    return deviceList



# 判断不同类型设备
def identify_different_devices(deviceList):
    dev_list = []
    # 判断不同类型设备，并输出相关信息
    for i in range(0, deviceList.nDeviceNum):
        mvcc_dev_info = ctypes.cast(deviceList.pDeviceInfo[i], ctypes.POINTER(MV_CC_DEVICE_INFO)).contents
        # 判断是否为 USB 接口相机
        if mvcc_dev_info.nTLayerType == MV_USB_DEVICE:
            print ("U3V 设备序号e: [%d]" % i)
            strModeName = ""
            for per in mvcc_dev_info.SpecialInfo.stUsb3VInfo.chModelName:
                if per == 0:
                    break
                strModeName = strModeName + chr(per)
            print ("当前设备型号名 : %s" % strModeName)
        dev_list.append(f"[{i}]USB: {strModeName}")
    return dev_list


# 创建相机实例并创建句柄
def creat_camera(deviceList , nConnectionNum ):
    """

    :param deviceList:        设备列表
    :param nConnectionNum:    需要连接的设备序号
    :param log:               是否创建日志
    :param log_path:          日志保存路径
    :return:                  相机实例和设备列表
    """
    # 创建相机实例
    cam = MvCamera()
    # 选择设备并创建句柄
    stDeviceList = ctypes.cast(deviceList.pDeviceInfo[int(nConnectionNum)], ctypes.POINTER(MV_CC_DEVICE_INFO)).contents

    # 创建句柄,不生成日志
    ret = cam.MV_CC_CreateHandleWithoutLog(stDeviceList)
    if ret != 0:
        print("create handle fail! ret[0x%x]" % ret)
        sys.exit()
    return cam , stDeviceList

def start_grab(cam):
    ret = cam.MV_CC_StartGrabbing()
    if ret != 0:
        print("开始取流失败! ret[0x%x]" % ret)
        return ret
    return 0


def load_json(DataFile):
    """ 加载 pod.json 文件 """
    if os.path.exists(DataFile):
        try:
            with open(DataFile, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []  # 解析错误，返回空列表
    return []

def save_to_json(DataFile,record):
    """ 保存数据到 xxx.json """
    data = load_json(DataFile)
    data.append(record)  # 添加新记录

    with open(DataFile, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def open_image(ui, image_path):
    try:
        if not os.path.exists(image_path):
            QMessageBox.warning(ui, "文件不存在", f"图像文件 {image_path} 不存在。")
            return

        # 在 Windows 上使用默认图片查看器打开图像
        subprocess.run(['start', image_path], shell=True, check=True)
    except Exception as e:
        error_message = f"查看图像时发生错误：{str(e)}\n{traceback.format_exc()}"
        QMessageBox.critical(ui, "查看错误", error_message)
        print(error_message)

def scale_img(processed_img, frame_width, frame_height):
    height, width = processed_img.shape[:2]
    scale = min(frame_width / width, frame_height / height)
    new_width = int(width * scale)
    new_height = int(height * scale)
    img_resized = cv2.resize(processed_img, (new_width, new_height), interpolation=cv2.INTER_LINEAR)
    return img_resized


def convert_cv_to_qimage(cv_img):
    # 输出图像的rgb值
    height, width, channel = cv_img.shape
    bytes_per_line = 3 * width
    qt_img = QImage(cv_img.data, width, height, bytes_per_line, QImage.Format_RGB888)
    return qt_img.rgbSwapped()


def get_image(cam):
    """
    从相机获取一帧图像
    返回: (ret_code, image_array)
    """
    from ...hikModule.CameraParams_header import MV_FRAME_OUT
    
    try:
        # 创建输出帧信息结构体
        stOutFrame = MV_FRAME_OUT()
        
        # 获取图像缓冲区（超时时间1000ms）
        ret = cam.MV_CC_GetImageBuffer(stOutFrame, 1000)
        
        if ret == MV_OK:
            try:
                # 获取图像数据长度
                nFrameLen = stOutFrame.stFrameInfo.nFrameLen
                
                # 从缓冲区复制数据
                image_data = (ctypes.c_ubyte * nFrameLen)()
                ctypes.memmove(byref(image_data), stOutFrame.pBufAddr, nFrameLen)
                
                # 转换为numpy数组
                image_array = np.frombuffer(image_data, dtype=np.uint8)
                
                # 根据像素格式处理
                width = stOutFrame.stFrameInfo.nWidth
                height = stOutFrame.stFrameInfo.nHeight
                pixel_format = stOutFrame.stFrameInfo.enPixelType
                
                # 像素格式常量 (来自PixelType_header.py)
                PixelType_Gvsp_BayerRG8 = 17301513    # 0x01080009
                PixelType_Gvsp_BayerGB8 = 17301514    # 0x0108000A
                PixelType_Gvsp_BayerGR8 = 17301512    # 0x01080008
                PixelType_Gvsp_BayerBG8 = 17301515    # 0x0108000B
                
                # 判断像素格式（Bayer格式的图像数据是单通道）
                if pixel_format == PixelType_Gvsp_BayerRG8:
                    # BayerRG8格式 - 转为RGB（和老代码camera_thread.py一致）
                    image = image_array.reshape((height, width))
                    image = cv2.cvtColor(image, cv2.COLOR_BAYER_RG2RGB)
                    
                elif pixel_format == PixelType_Gvsp_RGB8_Packed or pixel_format == 0x02180014 or len(image_array) == width * height * 3:
                    # RGB8格式或3通道数据，直接reshape
                    image = image_array.reshape((height, width, 3))
                    # RGB转BGR (OpenCV使用BGR)
                    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                    
                elif pixel_format == PixelType_Gvsp_BayerGB8 or pixel_format == 0x0108000A:
                    # BayerGB8格式 - 直接转为BGR
                    image = image_array.reshape((height, width))
                    image = cv2.cvtColor(image, cv2.COLOR_BAYER_GB2BGR)
                    
                elif pixel_format == PixelType_Gvsp_BayerGR8 or pixel_format == 0x01080008:
                    # BayerGR8格式 - 直接转为BGR
                    image = image_array.reshape((height, width))
                    image = cv2.cvtColor(image, cv2.COLOR_BAYER_GR2BGR)
                    
                elif pixel_format == PixelType_Gvsp_BayerBG8 or pixel_format == 0x0108000B:
                    # BayerBG8格式 - 直接转为BGR
                    image = image_array.reshape((height, width))
                    image = cv2.cvtColor(image, cv2.COLOR_BAYER_BG2BGR)
                    
                elif pixel_format == PixelType_Gvsp_Mono8 or len(image_array) == width * height:
                    # Mono8灰度格式
                    image = image_array.reshape((height, width))
                    image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
                    
                elif len(image_array) == width * height * 3:
                    # 未知的3通道格式，直接reshape
                    image = image_array.reshape((height, width, 3))
                    
                else:
                    print(f"⚠️ 未知像素格式: {pixel_format:#x}, 数据大小: {len(image_array)}")
                    cam.MV_CC_FreeImageBuffer(stOutFrame)
                    return ret, None
                
                # 释放缓冲区
                cam.MV_CC_FreeImageBuffer(stOutFrame)
                
                return MV_OK, image
                
            except Exception as e:
                # 确保释放缓冲区
                cam.MV_CC_FreeImageBuffer(stOutFrame)
                print(f"图像处理异常: {e}")
                import traceback
                traceback.print_exc()
                return ret, None
        else:
            return ret, None
            
    except Exception as e:
        print(f"获取图像异常: {e}")
        import traceback
        traceback.print_exc()
        return None, None

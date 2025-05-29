from ctypes import c_ubyte, cdll, memset, byref, sizeof
import sys
import serial
import threading
import time
import serial.tools.list_ports
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout
import cv2
import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal

from ...hikModule.CameraParams_header import MV_FRAME_OUT
from ...hikModule.MvCameraControl_class import MvCamera


class BalanceThread(QThread):
    data_received = pyqtSignal(str)

    def __init__(self, port='COM7', baudrate=9600):
        super().__init__()
        self.port = port
        self.baudrate = baudrate
        self.ser = None
        self.reading = False
        self.cur_num = 0

    def run(self):
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=0.1)  # 设置适当的超时
            print(self.ser)
            self.reading = True

            while self.reading:
                if self.ser.in_waiting > 0:  # 检查是否有数据可读
                    data = self.ser.read_until(b'=')
                    print("---" , data)
                    if data:
                        data = data.decode('ascii').strip('=')[::-1]
                        # 如果数据是空，则continue

                        if not data:
                            continue
                        if self.cur_num != data:
                            self.cur_num = data
                            self.data_received.emit(data)
                            print(data)
                # else:
                #     # 没有数据时短暂让出CPU
                #     self.msleep(50)  # 比time.sleep更精确的QThread睡眠

        except serial.SerialException as e:
            print(f"串口错误: {e}")
        finally:
            if self.ser and self.ser.is_open:
                self.ser.close()

    def zero_balance(self):
        if self.ser and self.reading:
            self.ser.write(b'Z\r\n')


    def stop(self):
        self.reading = False
        self.wait()  # 等待线程安全退出
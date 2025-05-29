from ctypes import c_ubyte, cdll, memset, byref, sizeof

import cv2
import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal

from ...hikModule.CameraParams_header import MV_FRAME_OUT
from ...hikModule.MvCameraControl_class import MvCamera


def image_control(data , stFrameInfo):
    data = data.reshape(stFrameInfo.nHeight, stFrameInfo.nWidth, -1)
    image = cv2.cvtColor(data, cv2.COLOR_BAYER_RG2RGB)
    return image

class CameraThread(QThread):
    image_update = pyqtSignal(np.ndarray)

    def __init__(self, cam: MvCamera):
        super().__init__()
        self.cam = cam
        self._running = True

    def run(self):
        stOutFrame = MV_FRAME_OUT()
        memset(byref(stOutFrame), 0, sizeof(stOutFrame))
        while self._running:
            ret = self.cam.MV_CC_GetImageBuffer(stOutFrame, 1000)

            if None != stOutFrame.pBufAddr and 0 == ret and stOutFrame.stFrameInfo.enPixelType == 17301513:
                # print("get one frame: Width[%d], Height[%d], nFrameNum[%d]" % (stOutFrame.stFrameInfo.nWidth, stOutFrame.stFrameInfo.nHeight, stOutFrame.stFrameInfo.nFrameNum))
                pData = (c_ubyte * stOutFrame.stFrameInfo.nWidth * stOutFrame.stFrameInfo.nHeight)()
                cdll.msvcrt.memcpy(byref(pData), stOutFrame.pBufAddr, stOutFrame.stFrameInfo.nWidth * stOutFrame.stFrameInfo.nHeight)
                data = np.frombuffer(pData, count=int(stOutFrame.stFrameInfo.nWidth * stOutFrame.stFrameInfo.nHeight), dtype=np.uint8)
                image = image_control(data=data, stFrameInfo=stOutFrame.stFrameInfo)
            else:
                print("no data[0x%x]" % ret)
            nRet = self.cam.MV_CC_FreeImageBuffer(stOutFrame)

            self.image_update.emit(image)

    def stop(self):
        self._running = False
        self.wait()

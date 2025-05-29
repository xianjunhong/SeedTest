import threading
import uuid
import os
import cv2
import numpy as np
import base64
from PyQt5.QtCore import QObject, pyqtSignal, QThread

from ...aiModule.trex import Trex

class TrexThread(QThread):
    finished = pyqtSignal(list, str)  # 发出bbox列表和embedding字符串
    failed = pyqtSignal(str)          # 发出错误信息

    def __init__(self, image, bbox):
        super().__init__()
        self.image = image  # numpy数组 (cv2.imread或者摄像头拍的图)
        self.abs_bbox = bbox  # 绝对坐标 (x1, y1, x2, y2)

    def run(self):
        try:
            # 注意：这里直接喂image数组，不需要保存文件了！

            # tmp_img = self.image.copy()
            # xmin, ymin, xmax, ymax = self.abs_bbox
            # cv2.rectangle(tmp_img, (xmin, ymin), (xmax, ymax), (0, 255, 0), 2)  # 绿色框
            # save_path = "111.jpg"
            # cv2.imwrite(save_path, tmp_img)
            detector = Trex(
                image=self.image,
                prompt=self.abs_bbox,  # 直接用矩形框作为 prompt
                threshold=0.5
            )

            if detector.run_async():
                detector.poll_result()
                self.finished.emit(detector.result.bbox, detector.result.embedding)
            else:
                raise RuntimeError("创建任务失败")
        except Exception as e:
            self.failed.emit(str(e))

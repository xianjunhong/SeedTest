# src/threads/model_loader_thread.py

from PyQt5.QtCore import QThread, pyqtSignal
from ultralytics import YOLO
import numpy as np
import os

class ModelLoaderThread(QThread):
    model_loaded = pyqtSignal(object)
    load_failed = pyqtSignal(str)

    def __init__(self, model_path: str):
        super().__init__()
        self.model_path = model_path

    def run(self):
        try:
            if not os.path.exists(self.model_path):
                raise FileNotFoundError(f"模型路径不存在: {self.model_path}")

            model = YOLO(self.model_path)

            # 预热模型：推理一张空图像防止第一次使用卡顿
            dummy_image = np.zeros((640, 640, 3), dtype=np.uint8)
            model(dummy_image)

            self.model_loaded.emit(model)
        except Exception as e:
            self.load_failed.emit(f"模型加载失败：{str(e)}")

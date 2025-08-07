from PyQt5.QtCore import QThread, pyqtSignal
from sahi import AutoDetectionModel
from sahi.predict import get_sliced_prediction
import numpy as np
import os
import torch
from ultralytics import YOLO


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

            # 加载 SAHI 模型
            model = AutoDetectionModel.from_pretrained(
                model_type='yolov8',  # 根据你的模型类型调整
                model_path=self.model_path,
                confidence_threshold=0.5,
                device="cuda:0"
            )

            # 预热模型：推理一张空图像
            dummy_image = np.zeros((640, 640, 3), dtype=np.uint8)
            get_sliced_prediction(
                dummy_image,
                model,
                slice_height=640,
                slice_width=640,
                overlap_height_ratio=0.3,
                overlap_width_ratio=0.3
            )

            self.model_loaded.emit(model)
        except Exception as e:
            self.load_failed.emit(f"模型加载失败：{str(e)}")

    # def run(self):
    #     try:
    #         if not os.path.exists(self.model_path):
    #             raise FileNotFoundError(f"模型路径不存在: {self.model_path}")
    #
    #         model = YOLO(self.model_path)
    #
    #         # 预热模型：推理一张空图像防止第一次使用卡顿
    #         dummy_image = np.zeros((640, 640, 3), dtype=np.uint8)
    #         model(dummy_image)
    #
    #         self.model_loaded.emit(model)
    #     except Exception as e:
    #         self.load_failed.emit(f"模型加载失败：{str(e)}")
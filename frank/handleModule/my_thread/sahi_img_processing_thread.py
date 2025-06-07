from sahi.predict import get_sliced_prediction
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtCore import pyqtSignal
import time

class SahiImageProcessingThread(QThread):
    result_ready = pyqtSignal(object)  # 信号，用于传递处理结果

    def __init__(self, image, detection_model):
        super().__init__()
        self.image = image  # 输入图像 (numpy 格式)
        self.detection_model = detection_model  # SAHI 模型

    def run(self):
        start = time.time()
        # 使用 SAHI 进行切片预测
        result = get_sliced_prediction(
            self.image,  # 直接传入 numpy 图像
            self.detection_model,
            slice_height=640,
            slice_width=640,
            overlap_height_ratio=0.2,
            overlap_width_ratio=0.2
        )
        # 发射结果信号
        print(f"Total time: {time.time() - start} seconds")
        self.result_ready.emit(result)
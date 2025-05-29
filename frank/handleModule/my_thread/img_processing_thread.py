from PyQt5.QtCore import QThread, pyqtSignal


class ImageProcessingThread(QThread):
    result_ready = pyqtSignal(object)

    def __init__(self, frame, processing_function):
        super().__init__()
        self.frame = frame
        self.processing_function = processing_function

    def run(self):
        # 指定处理函数
        result = self.processing_function(self.frame)
        self.result_ready.emit(result)

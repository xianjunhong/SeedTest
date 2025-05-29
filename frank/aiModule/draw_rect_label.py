from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt, QRect, QPoint, pyqtSignal
from PyQt5.QtGui import QPainter, QPen

class DrawRectLabel(QLabel):
    # 信号用于传递坐标给外部
    rects_updated = pyqtSignal(float, float, float, float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.allow_draw = False
        self.start_point = None
        self.end_point = None
        self.rects = []
        self.current_rect = None

    def set_allow_draw(self, flag: bool):
        self.allow_draw = flag

    def mousePressEvent(self, event):
        if not self.allow_draw:
            return
        self.start_point = event.pos()
        self.end_point = event.pos()
        self.update()

    def mouseMoveEvent(self, event):
        if not self.allow_draw or self.start_point is None:
            return
        self.end_point = event.pos()
        self.update()

    def mouseReleaseEvent(self, event):
        if not self.allow_draw or self.start_point is None:
            return
        self.end_point = event.pos()
        self.current_rect = QRect(self.start_point, self.end_point).normalized()

        # 转化为相对坐标（百分比坐标）
        label_width = self.width()
        label_height = self.height()

        xmin_rel = self.current_rect.left() / label_width
        ymin_rel = self.current_rect.top() / label_height
        xmax_rel = self.current_rect.right() / label_width
        ymax_rel = self.current_rect.bottom() / label_height

        # 打印相对坐标
        print(f"在draw_rect_label.py中输出 Relative coordinates: xmin: {xmin_rel:.2f}, ymin: {ymin_rel:.2f}, xmax: {xmax_rel:.2f}, ymax: {ymax_rel:.2f}")

        # 发射信号，将相对坐标传递出去
        self.rects_updated.emit(xmin_rel, ymin_rel, xmax_rel, ymax_rel)

        self.start_point = None
        self.end_point = None
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        if not self.allow_draw:
            return

        painter = QPainter(self)
        pen = QPen(Qt.green, 2, Qt.DashLine)
        painter.setPen(pen)

        if self.start_point and self.end_point:
            temp_rect = QRect(self.start_point, self.end_point)
            painter.drawRect(temp_rect)
        elif self.current_rect:
            painter.drawRect(self.current_rect)

    # 计算实际坐标 (在外部调用时用来获取绝对坐标)
    def get_absolute_coordinates(self, xmin_rel, ymin_rel, xmax_rel, ymax_rel):
        label_width = self.width()
        label_height = self.height()

        xmin_abs = xmin_rel * label_width
        ymin_abs = ymin_rel * label_height
        xmax_abs = xmax_rel * label_width
        ymax_abs = ymax_rel * label_height

        return xmin_abs, ymin_abs, xmax_abs, ymax_abs

    def clear_rect(self):
        """清除当前绘制的矩形框"""
        self.start_point = None
        self.end_point = None
        self.current_rect = None
        self.update()

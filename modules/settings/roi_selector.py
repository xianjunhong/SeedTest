"""
ROI可视化框选组件
允许用户在相机预览上拖拽绘制矩形来设置ROI区域
"""
from PyQt5.QtWidgets import QLabel, QMessageBox, QSizePolicy
from PyQt5.QtCore import Qt, QRect, QPoint, pyqtSignal
from PyQt5.QtGui import QPainter, QPen, QColor, QPixmap
import numpy as np


class ROISelector(QLabel):
    """ROI选择器 - 可拖拽绘制矩形"""
    
    roi_selected = pyqtSignal(int, int, int, int)  # offset_x, offset_y, width, height
    
    def __init__(self):
        super().__init__()
        self.setMinimumSize(480, 360)  # 改为更小的最小尺寸，适应各种分辨率
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setScaledContents(False)
        self.setStyleSheet("border: 2px solid #1976d2; background-color: black;")
        self.setAlignment(Qt.AlignCenter)
        self.setText("请打开相机开始预览")
        
        # ROI绘制相关
        self.drawing = False
        self.start_point = None
        self.end_point = None
        self.current_roi = None  # (x, y, w, h)
        
        # 图像相关
        self.original_pixmap = None
        self.image_rect = None  # 图像在label中的实际位置
        
        # 相机实际分辨率（用于坐标转换）
        # 默认值会在打开相机时从配置文件或实际相机获取
        self.camera_resolution = (4000, 3000)  # 临时默认值
        
        # 启用鼠标跟踪
        self.setMouseTracking(True)
    
    def set_image(self, pixmap):
        """
        设置要显示的图像
        pixmap: QPixmap
        """
        self.original_pixmap = pixmap
        
        # 计算图像在label中的实际位置（居中缩放）
        if pixmap:
            label_w = self.width()
            label_h = self.height()
            img_w = pixmap.width()
            img_h = pixmap.height()
            
            # 计算缩放比例
            scale = min(label_w / img_w, label_h / img_h)
            scaled_w = int(img_w * scale)
            scaled_h = int(img_h * scale)
            
            # 计算居中位置
            x = (label_w - scaled_w) // 2
            y = (label_h - scaled_h) // 2
            
            self.image_rect = QRect(x, y, scaled_w, scaled_h)
        
        self.update_display()
    
    def update_display(self):
        """更新显示"""
        if not self.original_pixmap or not self.image_rect:
            return
        
        # 创建临时pixmap用于绘制
        temp_pixmap = self.original_pixmap.copy()
        
        # 如果有ROI，绘制到pixmap上
        if self.current_roi:
            # current_roi存储的是相机实际分辨率坐标，需要转换为pixmap坐标
            x, y, w, h = self.current_roi
            
            # 计算转换比例（相机分辨率 -> pixmap尺寸）
            cam_w, cam_h = self.camera_resolution
            scale_x = self.original_pixmap.width() / cam_w
            scale_y = self.original_pixmap.height() / cam_h
            
            # 转换为pixmap坐标
            px = int(x * scale_x)
            py = int(y * scale_y)
            pw = int(w * scale_x)
            ph = int(h * scale_y)
            
            painter = QPainter(temp_pixmap)
            pen = QPen(QColor(0, 255, 0), 3)  # 绿色线条
            painter.setPen(pen)
            
            painter.drawRect(px, py, pw, ph)
            
            # 绘制半透明填充
            painter.fillRect(px, py, pw, ph, QColor(0, 255, 0, 30))
            
            # 绘制尺寸信息（显示实际分辨率的尺寸）
            painter.setPen(QColor(255, 255, 255))
            painter.drawText(px + 5, py + 20, f"{w} × {h} (实际分辨率)")
            
            painter.end()
        
        self.setPixmap(temp_pixmap)
    
    def mousePressEvent(self, event):
        """鼠标按下"""
        if event.button() == Qt.LeftButton and self.image_rect:
            # 检查是否在图像区域内
            if self.image_rect.contains(event.pos()):
                self.drawing = True
                # 转换为图像坐标
                self.start_point = self._label_to_image_coords(event.pos())
    
    def mouseMoveEvent(self, event):
        """鼠标移动"""
        if self.drawing and self.start_point and self.image_rect:
            # 转换为图像坐标
            self.end_point = self._label_to_image_coords(event.pos())
            
            # 计算矩形
            x = min(self.start_point.x(), self.end_point.x())
            y = min(self.start_point.y(), self.end_point.y())
            w = abs(self.end_point.x() - self.start_point.x())
            h = abs(self.end_point.y() - self.start_point.y())
            
            self.current_roi = (x, y, w, h)
            self.update_display()
    
    def mouseReleaseEvent(self, event):
        """鼠标释放"""
        if event.button() == Qt.LeftButton and self.drawing:
            self.drawing = False
            
            if self.current_roi:
                x, y, w, h = self.current_roi
                # 发出信号
                self.roi_selected.emit(x, y, w, h)
    
    def _label_to_image_coords(self, label_pos):
        """
        将label坐标转换为相机实际分辨率坐标
        label_pos: QPoint (label上的坐标)
        返回: QPoint (相机实际分辨率上的坐标)
        """
        if not self.image_rect:
            return label_pos
        
        # label坐标相对于image_rect的偏移
        x = label_pos.x() - self.image_rect.x()
        y = label_pos.y() - self.image_rect.y()
        
        # 转换为相机实际分辨率坐标（基于camera_resolution）
        cam_w, cam_h = self.camera_resolution
        scale_x = cam_w / self.image_rect.width()
        scale_y = cam_h / self.image_rect.height()
        
        img_x = int(x * scale_x)
        img_y = int(y * scale_y)
        
        # 限制在相机分辨率范围内
        img_x = max(0, min(img_x, cam_w))
        img_y = max(0, min(img_y, cam_h))
        
        return QPoint(img_x, img_y)
    
    def set_roi(self, x, y, w, h):
        """手动设置ROI"""
        self.current_roi = (x, y, w, h)
        self.update_display()
    
    def clear_roi(self):
        """清除ROI"""
        self.current_roi = None
        self.update_display()
    
    def get_roi(self):
        """获取当前ROI"""
        return self.current_roi
    
    def set_camera_resolution(self, width, height):
        """
        设置相机实际分辨率（用于坐标转换）
        width, height: 相机的实际分辨率
        """
        self.camera_resolution = (width, height)
        print(f"📷 ROI选择器已设置相机分辨率: {width} × {height}")


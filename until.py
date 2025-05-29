from PyQt5.QtGui import QPixmap, QPainter
from PyQt5.QtCore import Qt


def create_centered_square_pixmap(icon_path: str, square_size: int) -> QPixmap:
    """
    将图片缩放并居中到一个正方形画布中，保持原始长宽比。

    :param icon_path: 图片路径
    :param square_size: 正方形画布边长
    :return: 处理后的 QPixmap
    """
    pixmap = QPixmap(icon_path)
    if pixmap.isNull():
        return QPixmap(square_size, square_size)  # 返回空白图

    scaled_pixmap = pixmap.scaled(square_size, square_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)

    final_pixmap = QPixmap(square_size, square_size)
    final_pixmap.fill(Qt.transparent)

    painter = QPainter(final_pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    x_offset = (square_size - scaled_pixmap.width()) // 2
    y_offset = (square_size - scaled_pixmap.height()) // 2
    painter.drawPixmap(x_offset, y_offset, scaled_pixmap)
    painter.end()

    return final_pixmap

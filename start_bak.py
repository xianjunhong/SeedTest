from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

from frank.uiModule.ui import Ui
from frank.uiModule.tab_1 import Tab1Widget
from frank.uiModule.tab_2 import Tab2Widget
from frank.handleModule.init_tools import InitTools
import sys

if __name__ == '__main__':

    app = QApplication([])
    # 适应高dpi
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    app.setAttribute(Qt.AA_DisableWindowContextHelpButton)  # 可选：同时禁用帮助按钮
    app.setStyleSheet("QMessageBox { messagebox-icons: none; }")  # 移除图标（间接去音）

    # 初始化ui
    ui = Ui()
    # 给ui加功能
    init_tools = InitTools(ui)
    ui.show()
    app.exec_()
    init_tools.tab_1.close_device()
    sys.exit()




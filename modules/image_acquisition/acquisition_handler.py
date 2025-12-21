"""
图像采集模块 - 业务逻辑处理器
"""
import cv2
import numpy as np
import os
import json
import uuid
import pandas as pd
from datetime import datetime
from PyQt5.QtWidgets import QMessageBox, QFileDialog
from PyQt5.QtGui import QPixmap

from common.camera_base import CameraBase
from common.config_manager import ConfigManager
from common.balance_manager import BalanceManager


class AcquisitionHandler:
    """图像采集处理器"""
    
    def __init__(self, ui, config_manager):
        self.ui = ui
        self.config_manager = config_manager
        
        # 初始化相机
        self.camera = CameraBase(config_manager)
        
        # 初始化天平
        self.balance_manager = BalanceManager()
        self.current_weight = 0.0
        
        # 状态变量
        self.save_path = "data/acquisition"
        self.data_file = "data/acquisition_records.json"
        self.last_frame = None  # 存储最后一帧用于拍照
        
        # 确保保存路径存在
        os.makedirs(self.save_path, exist_ok=True)
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        
        # 初始化JSON文件
        if not os.path.exists(self.data_file):
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump([], f)
        
        # 连接信号
        self._connect_signals()
        
        # 加载数据
        self.load_data()
    
    def _connect_signals(self):
        """连接UI信号"""
        # 相机信号
        self.ui.btn_enum_cam.clicked.connect(self.enum_cameras)
        self.ui.btn_open_cam.clicked.connect(self.toggle_camera)
        
        # 天平信号
        self.ui.btn_scan_balance.clicked.connect(self.scan_balance)
        self.ui.btn_open_balance.clicked.connect(self.open_balance)
        self.ui.btn_zero_balance.clicked.connect(self.zero_balance)
        
        # 预览和拍照
        self.ui.button_start_preview.clicked.connect(self.start_preview)
        self.ui.button_capture.clicked.connect(self.capture_image)
        
        # 保存设置
        self.ui.btn_browse_path.clicked.connect(self.browse_save_path)
        self.ui.input_save_path.textChanged.connect(self.update_save_path)
        
        # 数据管理
        self.ui.data_page.btn_refresh.clicked.connect(self.load_data)
        self.ui.data_page.btn_export_csv.clicked.connect(self.export_csv)
        self.ui.data_page.btn_delete_all.clicked.connect(self.delete_all_records)
    
    # ========== 相机控制 ==========
    def enum_cameras(self):
        """枚举相机"""
        success, message, device_list = self.camera.enum_devices()
        if success:
            self.ui.combo_devices_cam.clear()
            self.ui.combo_devices_cam.addItems(device_list)
        else:
            QMessageBox.warning(self.ui, "错误", message)
    
    def toggle_camera(self):
        """切换相机状态"""
        if self.camera.is_open:
            self.close_camera()
        else:
            self.open_camera()
    
    def open_camera(self):
        """打开相机"""
        device_index = self.ui.combo_devices_cam.currentIndex()
        if device_index < 0:
            QMessageBox.warning(self.ui, "错误", "请先扫描并选择相机")
            return
        
        success, message = self.camera.open_device(device_index)
        if success:
            self.ui.btn_open_cam.setText("关闭相机")
            self.ui.button_start_preview.setEnabled(True)
            # 自动开始预览
            self.start_preview()
        else:
            QMessageBox.warning(self.ui, "错误", message)
    
    def close_camera(self):
        """关闭相机"""
        self.camera.stop_grabbing()
        self.camera.close_device()
        
        self.ui.btn_open_cam.setText("打开相机")
        self.ui.button_start_preview.setEnabled(False)
        self.ui.button_capture.setEnabled(False)
        
        # 显示黑屏
        black_image = np.zeros((480, 640, 3), dtype=np.uint8)
        self.display_image(black_image)
    
    def start_preview(self):
        """开始预览"""
        if not self.camera.is_open:
            QMessageBox.warning(self.ui, "错误", "请先打开相机")
            return
        
        success, message = self.camera.start_grabbing()
        if success:
            # 连接图像更新信号
            self.camera.cam_thread.image_update.connect(self.update_camera_image)
            self.ui.button_capture.setEnabled(True)
        else:
            QMessageBox.warning(self.ui, "错误", message)
    
    def update_camera_image(self, image):
        """更新相机图像"""
        self.last_frame = image.copy()  # 保存当前帧
        self.display_image(image)
    
    # ========== 天平控制 ==========
    def scan_balance(self):
        """扫描天平"""
        ports = self.balance_manager.scan_ports()
        self.ui.combo_balance_port.clear()
        if ports:
            self.ui.combo_balance_port.addItems(ports)
            from qfluentwidgets import InfoBar, InfoBarPosition
            from PyQt5.QtCore import Qt
            InfoBar.success(
                title='串口扫描',
                content=f'找到 {len(ports)} 个串口',
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self.ui
            )
        else:
            QMessageBox.warning(self.ui, "提示", "未检测到可用串口，请检查：\n1. 天平是否已连接\n2. 驱动是否已安装")
    
    def open_balance(self):
        """打开天平"""
        if self.balance_manager.is_connected:
            # 关闭天平
            self.balance_manager.disconnect()
            self.ui.btn_open_balance.setText("打开天平")
            self.ui.label_balance_status.setText("未连接")
            self.ui.label_balance_status.setStyleSheet("color: red; font-weight: bold;")
            self.ui.btn_zero_balance.setEnabled(False)
            self.ui.label_weight.setText("0.00 g")
            self.current_weight = 0.0
            return
        
        port_string = self.ui.combo_balance_port.currentText()
        if not port_string:
            QMessageBox.warning(self.ui, "错误", "请先扫描并选择串口")
            return
        
        # 从格式化字符串中提取实际串口名
        port = self.balance_manager.get_port_name(port_string)
        
        success, message = self.balance_manager.connect(port)
        if success:
            # 启动天平线程
            self.balance_manager.start()
            
            # 连接信号
            self.balance_manager.balance_thread.data_received.connect(self.update_weight)
            self.balance_manager.balance_thread.error_occurred.connect(self.handle_balance_error)
            self.balance_manager.balance_thread.connection_lost.connect(self.handle_balance_lost)
            
            self.ui.btn_open_balance.setText("关闭天平")
            self.ui.label_balance_status.setText("已连接")
            self.ui.label_balance_status.setStyleSheet("color: green; font-weight: bold;")
            self.ui.btn_zero_balance.setEnabled(True)
        else:
            QMessageBox.warning(self.ui, "错误", f"连接失败: {message}")
    
    def update_weight(self, weight_str):
        """更新重量显示"""
        try:
            self.current_weight = float(weight_str)
            self.ui.label_weight.setText(f"{self.current_weight:.2f} g")
        except ValueError:
            pass
    
    def zero_balance(self):
        """天平清零"""
        if self.balance_manager.is_connected:
            self.balance_manager.zero()
    
    def handle_balance_error(self, error_msg):
        """处理天平错误"""
        self.ui.label_balance_status.setText("⚠️ 异常")
        self.ui.label_balance_status.setStyleSheet("color: orange; font-weight: bold;")
    
    def handle_balance_lost(self):
        """处理天平断线"""
        self.balance_manager.is_connected = False
        self.ui.btn_open_balance.setText("打开天平")
        self.ui.label_balance_status.setText("❌ 断开")
        self.ui.label_balance_status.setStyleSheet("color: red; font-weight: bold;")
        self.ui.btn_zero_balance.setEnabled(False)
        QMessageBox.warning(self.ui, "警告", "天平连接丢失，请重新连接")
    
    # ========== 拍照保存 ==========
    def capture_image(self):
        """拍照并保存记录"""
        # 检查品种编号
        variety_code = self.ui.input_variety_code.text().strip()
        if not variety_code:
            QMessageBox.warning(self.ui, "错误", "请输入品种编号")
            return
        
        # 优先使用预览中的最后一帧
        if self.last_frame is not None:
            image = self.last_frame.copy()
            print("📸 使用预览帧拍照")
        else:
            # 如果没有预览，直接获取一帧
            success, image = self.camera.capture_image()
            if not success or image is None:
                QMessageBox.warning(self.ui, "错误", "拍照失败，请先开始预览")
                return
            print("📸 直接获取图像拍照")
        
        # 生成唯一ID
        record_id = str(uuid.uuid4().hex)[:8]
        
        # 生成文件名
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        prefix = self.ui.input_prefix.text() or "img"
        filename = f"{prefix}_{timestamp_str}_{record_id}.jpg"
        filepath = os.path.join(self.save_path, filename)
        
        # 直接保存图像（相机数据格式已经适合保存）
        success_save = cv2.imwrite(filepath, image)
        
        if success_save:
            # 创建记录
            record = {
                'id': record_id,
                'variety_code': variety_code,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'weight': round(self.current_weight, 2),
                'image_path': os.path.abspath(filepath),
                'filename': filename
            }
            
            # 保存到JSON
            self._save_record(record)
            
            # 刷新数据页面
            self.load_data()
            
            # 清空品种编号输入框
            self.ui.input_variety_code.clear()
            self.ui.input_variety_code.setFocus()  # 聚焦到输入框方便下次输入
            
            # 自动恢复实时预览（如果相机已打开）
            if self.camera.is_open and not (self.camera.cam_thread and self.camera.cam_thread.running):
                self.start_preview()
            
            # 显示提示
            print(f"✅ 已保存: {filepath}")
            from qfluentwidgets import InfoBar, InfoBarPosition
            from PyQt5.QtCore import Qt
            InfoBar.success(
                title='保存成功',
                content=f'{filename}',
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self.ui
            )
        else:
            QMessageBox.warning(self.ui, "错误", f"保存图像失败: {filepath}")
    
    def browse_save_path(self):
        """浏览保存路径"""
        path = QFileDialog.getExistingDirectory(self.ui, "选择保存路径", self.save_path)
        if path:
            self.ui.input_save_path.setText(path)
    
    def update_save_path(self, path):
        """更新保存路径"""
        self.save_path = path
        os.makedirs(path, exist_ok=True)
    
    # ========== 显示工具 ==========
    def display_image(self, image):
        """显示图像"""
        widget = self.ui.widget_display
        pixmap = self.camera.image_to_pixmap(image, widget.width(), widget.height())
        if pixmap:
            widget.setPixmap(pixmap)
    
    # ========== 数据管理 ==========
    def _save_record(self, record):
        """保存记录到JSON"""
        try:
            # 读取现有数据
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 添加新记录（插入到最前面）
            data.insert(0, record)
            
            # 保存
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 记录已保存: {record['id']}")
        except Exception as e:
            print(f"❌ 保存记录失败: {e}")
    
    def load_data(self):
        """加载数据到表格"""
        self.ui.data_page.clear_table()
        
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for record in data:
                self.ui.data_page.add_record_row(
                    record,
                    self.view_image,
                    self.delete_record
                )
            
            print(f"✅ 已加载 {len(data)} 条记录")
        except Exception as e:
            print(f"❌ 加载数据失败: {e}")
    
    def view_image(self, record):
        """查看图像"""
        image_path = record.get('image_path')
        if image_path and os.path.exists(image_path):
            # 使用系统默认图片查看器打开
            import subprocess
            import platform
            
            try:
                if platform.system() == 'Windows':
                    os.startfile(image_path)
                elif platform.system() == 'Darwin':  # macOS
                    subprocess.run(['open', image_path])
                else:  # Linux
                    subprocess.run(['xdg-open', image_path])
            except Exception as e:
                QMessageBox.warning(self.ui, "错误", f"打开图像失败: {e}")
        else:
            QMessageBox.warning(self.ui, "错误", "图像文件不存在")
    
    def delete_record(self, record):
        """删除单条记录"""
        reply = QMessageBox.question(
            self.ui, "确认删除",
            f"确定要删除记录 {record['id']} 吗？\n图像文件也将被删除。",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.No:
            return
        
        try:
            # 读取数据
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 移除记录
            data = [r for r in data if r['id'] != record['id']]
            
            # 保存
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # 删除图像文件
            image_path = record.get('image_path')
            if image_path and os.path.exists(image_path):
                os.remove(image_path)
            
            # 刷新表格
            self.load_data()
            
            print(f"✅ 已删除记录: {record['id']}")
        except Exception as e:
            QMessageBox.warning(self.ui, "错误", f"删除失败: {e}")
    
    def delete_all_records(self):
        """删除全部记录"""
        reply = QMessageBox.question(
            self.ui, "确认删除",
            "确定要删除所有记录吗？\n所有图像文件也将被删除，此操作不可恢复！",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.No:
            return
        
        try:
            # 读取数据
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 删除所有图像文件
            for record in data:
                image_path = record.get('image_path')
                if image_path and os.path.exists(image_path):
                    try:
                        os.remove(image_path)
                    except:
                        pass
            
            # 清空JSON
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump([], f)
            
            # 刷新表格
            self.load_data()
            
            QMessageBox.information(self.ui, "成功", "已删除所有记录")
        except Exception as e:
            QMessageBox.warning(self.ui, "错误", f"删除失败: {e}")
    
    def export_csv(self):
        """导出CSV"""
        filepath, _ = QFileDialog.getSaveFileName(
            self.ui, "保存 CSV 文件", "", "CSV 文件 (*.csv)"
        )
        
        if not filepath:
            return
        
        try:
            # 读取数据
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not data:
                QMessageBox.warning(self.ui, "提示", "没有数据可导出")
                return
            
            # 转换为DataFrame
            df = pd.DataFrame(data)
            
            # 选择要导出的列
            columns = ['id', 'variety_code', 'timestamp', 'weight', 'filename']
            df = df[columns]
            
            # 重命名列
            df.columns = ['ID', '品种编号', '时间', '重量(g)', '文件名']
            
            # 导出CSV
            df.to_csv(filepath, index=False, encoding='utf-8-sig')
            
            QMessageBox.information(self.ui, "成功", f"数据已导出至:\n{filepath}")
            print(f"✅ 已导出 CSV: {filepath}")
        except Exception as e:
            QMessageBox.warning(self.ui, "错误", f"导出失败: {e}")
    
    # ========== 清理 ==========
    def close_device(self):
        """关闭设备并重置UI状态"""
        print("🧹 清理图像采集模块资源...")
        
        # 断开所有信号连接
        if self.camera.cam_thread:
            try:
                self.camera.cam_thread.image_update.disconnect()
                print("✅ 已断开相机信号")
            except:
                pass
        
        # 关闭设备
        self.camera.stop_grabbing()
        self.camera.close_device()
        self.balance_manager.disconnect()
        
        # 重置UI状态
        self.ui.home_page.btn_open_cam.setText("打开相机")
        self.ui.home_page.button_start_preview.setEnabled(False)
        self.ui.home_page.button_start_preview.setText("开始预览")
        self.ui.home_page.button_capture.setEnabled(False)
        self.ui.home_page.btn_open_balance.setText("打开天平")
        self.ui.home_page.label_balance_status.setText("未连接")
        self.ui.home_page.label_balance_status.setStyleSheet("color: red; font-weight: bold;")
        self.ui.home_page.btn_zero_balance.setEnabled(False)
        self.ui.home_page.label_weight.setText("0.00 g")
        
        # 清空画面
        self.ui.home_page.widget_display.setText("相机未启动")
        self.ui.home_page.widget_display.clear()
        
        # 重置状态变量
        self.last_frame = None
        self.current_weight = 0.0
        
        print("✅ 图像采集模块资源清理完成")


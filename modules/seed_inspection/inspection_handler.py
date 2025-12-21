"""
考种模块 - 业务逻辑处理器
整合相机、天平、模型，处理考种流程
"""
import cv2
import numpy as np
import uuid
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QThread, pyqtSignal, Qt

from common.camera_base import CameraBase
from common.balance_manager import BalanceManager
from common.model_manager import ModelManager
from common.data_manager import DataManager
from common.config_manager import ConfigManager


class ModelLoadThread(QThread):
    """模型加载线程"""
    load_finished = pyqtSignal(bool, str)  # (success, message)
    
    def __init__(self, model_manager, model_name):
        super().__init__()
        self.model_manager = model_manager
        self.model_name = model_name
    
    def run(self):
        """后台加载模型"""
        success, message, model = self.model_manager.load_model(self.model_name)
        self.load_finished.emit(success, message)


class InspectionHandler:
    """考种处理器"""
    
    def __init__(self, ui, config_manager, model_name):
        self.ui = ui
        self.config_manager = config_manager
        self.model_name = model_name
        
        # 初始化管理器
        self.camera = CameraBase(config_manager)
        self.balance_manager = BalanceManager()
        self.model_manager = ModelManager(config_manager)
        self.data_manager = DataManager(config_manager)
        
        # 状态变量
        self.last_frame = None
        self.processed_image = None
        self.detection_results = None
        self.current_weight = 0.0
        self.showing_processed = False  # 标记是否正在显示处理后图像
        
        # 检测参数
        self.confidence_threshold = config_manager.get_detection_config()['default_confidence']
        self.area_threshold = config_manager.get_detection_config()['default_area_filter']
        
        # 加载模型
        self._load_model()
        
        # 连接信号
        self._connect_signals()
    
    def _load_model(self):
        """后台加载模型"""
        print(f"🔄 开始加载模型: {self.model_name}")
        
        # 创建加载线程
        self.model_load_thread = ModelLoadThread(self.model_manager, self.model_name)
        self.model_load_thread.load_finished.connect(self._on_model_loaded)
        self.model_load_thread.start()
    
    def _on_model_loaded(self, success, message):
        """模型加载完成回调"""
        if success:
            print(f"✅ 模型加载成功: {self.model_name}")
            # 使用非阻塞的InfoBar提示
            from qfluentwidgets import InfoBar, InfoBarPosition
            InfoBar.success(
                title='模型加载成功',
                content=f'{self.model_name} 已就绪',
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=2000,  # 2秒后自动消失
                parent=self.ui
            )
        else:
            print(f"❌ 模型加载失败: {message}")
            QMessageBox.warning(self.ui, "错误", f"模型加载失败:\n{message}")
    
    def _connect_signals(self):
        """连接UI信号"""
        # 相机信号
        self.ui.home_page.btn_enum_cam.clicked.connect(self.enum_cameras)
        self.ui.home_page.btn_open_cam.clicked.connect(self.toggle_camera)
        
        # 天平信号
        self.ui.home_page.btn_scan_balance.clicked.connect(self.scan_balance)
        self.ui.home_page.btn_open_balance.clicked.connect(self.open_balance)
        self.ui.home_page.btn_zero_balance.clicked.connect(self.zero_balance)
        
        # 处理信号
        self.ui.home_page.button_live_img.clicked.connect(self.start_preview)
        self.ui.home_page.button_process_img.clicked.connect(self.process_image)
        self.ui.home_page.button_save_info.clicked.connect(self.save_data)
        
        # 参数调整信号
        self.ui.home_page.slider_confidence.valueChanged.connect(self.update_confidence)
        self.ui.home_page.slider_area.valueChanged.connect(self.update_area_filter)
        
        # 相机图像更新
        if self.camera.cam_thread:
            self.camera.cam_thread.image_update.connect(self.update_camera_image)
    
    # ========== 相机控制 ==========
    def enum_cameras(self):
        """枚举相机"""
        success, message, device_list = self.camera.enum_devices()
        if success:
            self.ui.home_page.combo_devices_cam.clear()
            self.ui.home_page.combo_devices_cam.addItems(device_list)
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
        device_index = self.ui.home_page.combo_devices_cam.currentIndex()
        if device_index < 0:
            QMessageBox.warning(self.ui, "错误", "请先扫描并选择相机")
            return
        
        success, message = self.camera.open_device(device_index)
        if success:
            self.ui.home_page.btn_open_cam.setText("关闭相机")
            self.ui.home_page.button_live_img.setEnabled(True)
            # 自动开始预览
            self.start_preview()
        else:
            QMessageBox.warning(self.ui, "错误", message)
    
    def close_camera(self):
        """关闭相机"""
        self.camera.stop_grabbing()
        self.camera.close_device()
        
        self.ui.home_page.btn_open_cam.setText("打开相机")
        self.ui.home_page.button_live_img.setEnabled(False)
        self.ui.home_page.button_process_img.setEnabled(False)
        
        # 显示黑屏
        black_image = np.zeros((480, 640, 3), dtype=np.uint8)
        self.display_image(black_image)
    
    def start_preview(self):
        """开始预览"""
        if not self.camera.is_open:
            QMessageBox.warning(self.ui, "错误", "请先打开相机")
            return
        
        # 清除"显示处理后图像"标志
        self.showing_processed = False
        
        success, message = self.camera.start_grabbing()
        if success:
            # 断开旧的信号连接（如果有）
            try:
                self.camera.cam_thread.image_update.disconnect(self.update_camera_image)
            except:
                pass
            # 连接图像更新信号
            self.camera.cam_thread.image_update.connect(self.update_camera_image)
            self.ui.home_page.button_process_img.setEnabled(True)
            print("📹 开始实时预览")
        else:
            QMessageBox.warning(self.ui, "错误", message)
    
    def update_camera_image(self, image):
        """更新相机图像"""
        # 如果正在显示处理后的图像，不要覆盖
        if hasattr(self, 'showing_processed') and self.showing_processed:
            return
        
        self.last_frame = image.copy()
        self.display_image(image)
    
    # ========== 天平控制 ==========
    def scan_balance(self):
        """扫描天平"""
        ports = self.balance_manager.scan_ports()
        self.ui.home_page.combo_balance_port.clear()
        if ports:
            self.ui.home_page.combo_balance_port.addItems(ports)
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
            self.ui.home_page.btn_open_balance.setText("打开天平")
            self.ui.home_page.label_balance_status.setText("未连接")
            self.ui.home_page.label_balance_status.setStyleSheet("color: red; font-weight: bold;")
            self.ui.home_page.btn_zero_balance.setEnabled(False)
            return
        
        port_string = self.ui.home_page.combo_balance_port.currentText()
        if not port_string:
            QMessageBox.warning(self.ui, "错误", "请先扫描并选择串口")
            return
        
        # 从格式化字符串中提取实际串口名
        port = self.balance_manager.get_port_name(port_string)
        
        success, message = self.balance_manager.connect(port)
        if success:
            self.balance_manager.start()
            
            # 连接信号
            self.balance_manager.balance_thread.data_received.connect(self.update_weight)
            self.balance_manager.balance_thread.error_occurred.connect(self.handle_balance_error)
            self.balance_manager.balance_thread.connection_lost.connect(self.handle_balance_lost)
            
            self.ui.home_page.btn_open_balance.setText("关闭天平")
            self.ui.home_page.label_balance_status.setText("已连接")
            self.ui.home_page.label_balance_status.setStyleSheet("color: green; font-weight: bold;")
            self.ui.home_page.btn_zero_balance.setEnabled(True)
        else:
            QMessageBox.warning(self.ui, "错误", message)
    
    def update_weight(self, weight_str):
        """更新重量显示"""
        try:
            self.current_weight = float(weight_str)
            self.ui.home_page.label_weight.setText(f"{self.current_weight:.2f} g")
        except ValueError:
            pass
    
    def handle_balance_error(self, error_msg):
        """处理天平错误"""
        self.ui.home_page.label_balance_status.setText("⚠️ 异常")
        self.ui.home_page.label_balance_status.setStyleSheet("color: orange; font-weight: bold;")
    
    def handle_balance_lost(self):
        """处理天平断线"""
        self.balance_manager.is_connected = False
        self.ui.home_page.label_balance_status.setText("❌ 断开")
        self.ui.home_page.label_balance_status.setStyleSheet("color: red; font-weight: bold;")
        QMessageBox.warning(self.ui, "警告", "天平连接丢失，请重新连接")
    
    def zero_balance(self):
        """天平清零"""
        if self.balance_manager.is_connected:
            self.balance_manager.zero()
    
    # ========== 图像处理 ==========
    def process_image(self):
        """处理图像"""
        if self.last_frame is None:
            QMessageBox.warning(self.ui, "错误", "请先拍摄图像")
            return
        
        # 记录是否正在预览
        self.was_grabbing = self.camera.cam_thread and self.camera.cam_thread.running
        
        # 停止预览并断开信号
        if self.was_grabbing:
            # 先断开信号连接，防止后续图像覆盖
            try:
                self.camera.cam_thread.image_update.disconnect(self.update_camera_image)
            except Exception as e:
                pass
            
            # 再停止取流
            self.camera.stop_grabbing()
        
        # 显示loading进度条
        self.ui.home_page._center_loading_progress()  # 先居中
        self.ui.home_page.loading_progress.show()
        self.ui.home_page.loading_progress.raise_()  # 提升到最上层
        self.ui.home_page.button_process_img.setEnabled(False)
        
        # 处理UI事件，确保loading立即显示
        from PyQt5.QtWidgets import QApplication
        QApplication.processEvents()
        
        # 直接推理（不使用SAHI）
        try:
            inference_config = self.config_manager.get_detection_config()
            
            # 直接使用YOLOv8推理
            results = self.model_manager.current_model.predict(
                self.last_frame,
                conf=inference_config['inference_confidence'],
                verbose=False
            )
            
            # 检查结果（区分OBB和DET模型）
            if results and len(results) > 0:
                r = results[0]
                # OBB模型使用obb字段，DET模型使用boxes字段
                if self.model_manager.current_model_type == 'obb' and hasattr(r, 'obb') and r.obb is not None:
                    print(f"✅ OBB推理完成，检测到 {len(r.obb)} 个目标")
                elif hasattr(r, 'boxes') and r.boxes is not None:
                    print(f"✅ DET推理完成，检测到 {len(r.boxes)} 个目标")
                else:
                    print("✅ 推理完成，未检测到目标")
            else:
                print("✅ 推理完成，未检测到目标")
            
            # 处理结果
            self.handle_direct_inference_result(results)
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.handle_inference_error(f"推理失败: {str(e)}")
    
    def handle_direct_inference_result(self, results):
        """处理直接推理结果（YOLOv8）"""
        self.detection_results = results
        
        # 解析YOLOv8结果
        detections = []
        if results and len(results) > 0:
            r = results[0]
            
            # OBB模型处理
            if self.model_manager.current_model_type == 'obb' and hasattr(r, 'obb') and r.obb is not None:
                obb = r.obb
                
                # 获取置信度
                confs = obb.conf.cpu().numpy()
                
                # 优先使用xyxyxyxy（四角点）格式
                if hasattr(obb, 'xyxyxyxy') and obb.xyxyxyxy is not None:
                    xyxyxyxy = obb.xyxyxyxy.cpu().numpy()
                    for i in range(len(obb)):
                        pts = xyxyxyxy[i]  # shape: (4, 2)
                        
                        # 计算边界框（用于面积和绘制）
                        x_coords = pts[:, 0]
                        y_coords = pts[:, 1]
                        x1, y1 = float(x_coords.min()), float(y_coords.min())
                        x2, y2 = float(x_coords.max()), float(y_coords.max())
                        
                        # 计算OBB的实际长宽（四边形的边长）
                        edge1 = np.linalg.norm(pts[1] - pts[0])
                        edge2 = np.linalg.norm(pts[2] - pts[1])
                        length = max(edge1, edge2)
                        width = min(edge1, edge2)
                        area = 0.5 * abs(sum(x_coords[j] * y_coords[(j+1)%4] - x_coords[(j+1)%4] * y_coords[j] for j in range(4)))
                        
                        detections.append({
                            'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2,
                            'confidence': float(confs[i]),
                            'length': float(length),
                            'width': float(width),
                            'area': float(area)
                        })
                
                # 或使用xywhr格式
                elif hasattr(obb, 'xywhr') and obb.xywhr is not None:
                    xywhr = obb.xywhr.cpu().numpy()
                    for i in range(len(obb)):
                        cx, cy, w, h, r = xywhr[i]
                        
                        # 近似边界框
                        half_w, half_h = w/2, h/2
                        x1 = float(cx - half_w)
                        y1 = float(cy - half_h)
                        x2 = float(cx + half_w)
                        y2 = float(cy + half_h)
                        
                        length = max(w, h)
                        width = min(w, h)
                        area = w * h
                        
                        detections.append({
                            'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2,
                            'confidence': float(confs[i]),
                            'length': float(length),
                            'width': float(width),
                            'area': float(area)
                        })
            
            # DET模型处理（原逻辑）
            elif hasattr(r, 'boxes') and r.boxes is not None:
                boxes = r.boxes
                for i in range(len(boxes)):
                    x1, y1, x2, y2 = boxes.xyxy[i].cpu().numpy()
                    conf = boxes.conf[i].cpu().numpy()
                    
                    length = x2 - x1
                    width = y2 - y1
                    area = length * width
                    
                    detections.append({
                        'x1': float(x1), 'y1': float(y1),
                        'x2': float(x2), 'y2': float(y2),
                        'confidence': float(conf),
                        'length': float(length),
                        'width': float(width),
                        'area': float(area)
                    })
        
        # 保存原始检测结果，用于后续滑块调整
        self.raw_detections = detections
        
        # 绘制结果
        self.processed_image = self.visualize_direct_results(
            self.last_frame.copy(),
            detections,
            self.confidence_threshold,
            self.area_threshold
        )
        
        # 处理所有挂起的UI事件，确保相机信号完全停止
        from PyQt5.QtWidgets import QApplication
        QApplication.processEvents()
        
        # 设置标志，防止相机图像覆盖
        self.showing_processed = True
        
        # 显示图像
        self.display_image(self.processed_image)
        
        # 隐藏loading
        self.ui.home_page.loading_progress.hide()
        self.ui.home_page.button_process_img.setEnabled(True)
        self.ui.home_page.button_save_info.setEnabled(True)
        
        # 处理完成后，不自动重启预览，让用户查看检测结果
        # 用户可以手动点击"开始预览"来恢复实时预览
        print("✅ 检测完成，显示检测结果。点击'开始预览'可恢复实时预览。")
    
    def visualize_direct_results(self, image, detections, confidence_threshold, area_threshold):
        """
        可视化直接推理结果
        """
        if not detections:
            self.ui.home_page.update_result_display(0, 0, 0, 0)
            return image
        
        # 筛选
        filtered = self._filter_detections(detections, confidence_threshold, area_threshold)
        
        if not filtered:
            self.ui.home_page.update_result_display(0, 0, 0, 0)
            return image
        
        # 计算统计信息
        count = len(filtered)
        avg_length = np.mean([d['length'] for d in filtered]) * self.camera.cm_per_pixel
        avg_width = np.mean([d['width'] for d in filtered]) * self.camera.cm_per_pixel
        
        # 计算千粒重
        if self.current_weight > 0 and count > 0:
            thousand_weight = (self.current_weight / count) * 1000
        else:
            thousand_weight = 0
        
        # 更新显示
        self.ui.home_page.update_result_display(count, avg_length, avg_width, thousand_weight)
        
        # 绘制点
        colors = self._generate_colors(count)
        h, w = image.shape[:2]
        point_radius = max(int(min(w, h) * 0.008), 15)  # 增大点的半径，最小15像素
        
        for i, det in enumerate(filtered):
            center_x = int((det['x1'] + det['x2']) / 2)
            center_y = int((det['y1'] + det['y2']) / 2)
            color = colors[i % len(colors)]
            
            # 图像是RGB格式，颜色也用RGB顺序
            cv2.circle(image, (center_x, center_y), point_radius, color, -1)
            # 添加白色边框（加粗到3像素）
            cv2.circle(image, (center_x, center_y), point_radius, (255, 255, 255), 3)
        
        return image
    
    def handle_inference_error(self, error_msg):
        """处理推理错误"""
        QMessageBox.warning(self.ui, "错误", error_msg)
        self.ui.home_page.loading_progress.hide()
        self.ui.home_page.button_process_img.setEnabled(True)
        
        # 重新开始预览
        print("📹 推理失败，重新启动相机预览...")
        self.camera.start_grabbing()
    
    def _filter_detections(self, detections, confidence_threshold, area_threshold):
        """筛选检测结果"""
        # 置信度筛选
        filtered = [d for d in detections if d['confidence'] >= confidence_threshold / 100.0]
        
        if not filtered:
            return []
        
        # 面积筛选（百分位）
        areas = [d['area'] for d in filtered]
        areas_sorted = sorted(areas)
        cutoff_index = int(len(areas_sorted) * (area_threshold / 100.0))
        area_min = areas_sorted[cutoff_index] if cutoff_index < len(areas_sorted) else areas_sorted[0]
        
        filtered = [d for d in filtered if d['area'] >= area_min]
        
        return filtered
    
    def _generate_colors(self, count):
        """生成随机颜色列表"""
        # 预定义一些好看的颜色
        nice_colors = [
            (255, 0, 0),    # 红
            (0, 255, 0),    # 绿
            (0, 0, 255),    # 蓝
            (255, 255, 0),  # 黄
            (255, 0, 255),  # 品红
            (0, 255, 255),  # 青
            (255, 128, 0),  # 橙
            (128, 0, 255),  # 紫
            (0, 128, 255),  # 天蓝
            (255, 0, 128),  # 玫红
        ]
        
        # 如果数量超过预定义颜色，循环使用
        return nice_colors
    
    def update_confidence(self, value):
        """更新置信度"""
        self.confidence_threshold = value
        
        # 如果有处理后的图像，需要重新从原始检测结果重新绘制
        # 注意：这里需要保存原始的detections而不是results
        if hasattr(self, 'raw_detections') and self.last_frame is not None:
            self.showing_processed = True  # 标记正在显示处理后图像
            self.processed_image = self.visualize_direct_results(
                self.last_frame.copy(),
                self.raw_detections,
                self.confidence_threshold,
                self.area_threshold
            )
            self.display_image(self.processed_image)
    
    def update_area_filter(self, value):
        """更新面积筛选"""
        self.area_threshold = value
        
        # 如果有处理后的图像，需要重新从原始检测结果重新绘制
        if hasattr(self, 'raw_detections') and self.last_frame is not None:
            self.showing_processed = True  # 标记正在显示处理后图像
            self.processed_image = self.visualize_direct_results(
                self.last_frame.copy(),
                self.raw_detections,
                self.confidence_threshold,
                self.area_threshold
            )
            self.display_image(self.processed_image)
    
    # ========== 数据保存 ==========
    def save_data(self):
        """保存数据"""
        if self.processed_image is None or self.last_frame is None:
            QMessageBox.warning(self.ui, "错误", "请先处理图像")
            return
        
        # 生成ID
        record_id = str(uuid.uuid4().int)[:8]
        
        # 保存图像
        import os
        paths = self.config_manager.get_paths_config()
        
        # 直接保存图像（相机数据格式已经适合保存）
        cv2.imwrite(os.path.join(paths['images_folder'], f"{record_id}.jpg"), self.last_frame)
        cv2.imwrite(os.path.join(paths['processed_folder'], f"{record_id}.jpg"), self.processed_image)
        
        # 提取结果
        result_text = self.ui.home_page.label_count.text()
        count = int(result_text) if result_text else 0
        
        avg_length_text = self.ui.home_page.label_avg_length.text().replace(' cm', '')
        avg_length = float(avg_length_text) if avg_length_text else 0
        
        avg_width_text = self.ui.home_page.label_avg_width.text().replace(' cm', '')
        avg_width = float(avg_width_text) if avg_width_text else 0
        
        thousand_weight_text = self.ui.home_page.label_thousand_weight.text().replace(' g', '')
        thousand_weight = float(thousand_weight_text) if thousand_weight_text else 0
        
        # 获取品种信息
        variety_code = self.ui.home_page.input_variety_code.text().strip()
        
        # 检查品种编号是否为空
        if not variety_code:
            QMessageBox.warning(self.ui, "提示", "请输入品种编号！")
            return
        
        # 创建记录
        record = self.data_manager.create_record_template(
            record_id=record_id,
            model_name=self.model_name,
            variety_code=variety_code,
            count=count,
            avg_length=avg_length,
            avg_width=avg_width,
            weight=self.current_weight,
            thousand_seed_weight=thousand_weight,
            confidence_threshold=self.confidence_threshold,
            area_threshold=self.area_threshold
        )
        
        # 保存记录
        self.data_manager.save_record(record)
        
        # 清空结果
        self.ui.home_page.clear_result_display()
        self.processed_image = None
        self.ui.home_page.button_save_info.setEnabled(False)
        
        # 清空品种编号输入框
        self.ui.home_page.input_variety_code.clear()
        self.ui.home_page.input_variety_code.setFocus()  # 聚焦到输入框方便下次输入
        
        # 自动恢复实时预览
        if self.camera.is_open:
            self.start_preview()
        
        # 刷新数据页面
        self.ui.data_page.load_data()
        
        QMessageBox.information(self.ui, "成功", "数据已保存")
    
    # ========== 显示工具 ==========
    def display_image(self, image):
        """显示图像"""
        if image is None:
            return
        
        widget = self.ui.home_page.widget_display
        pixmap = self.camera.image_to_pixmap(image, widget.width(), widget.height())
        if pixmap:
            widget.setPixmap(pixmap)
    
    # ========== 清理 ==========
    def close_device(self):
        """关闭所有设备"""
        self.camera.close_device()
        self.balance_manager.disconnect()


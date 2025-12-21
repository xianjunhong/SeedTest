"""
相机基类
封装海康相机的基础操作，供考种和图像采集模块继承
"""
import cv2
import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap

from frank.hikModule.MvCameraControl_class import MvCamera
from frank.hikModule.MvErrorDefine_const import MV_OK
from frank.hikModule.CameraParams_const import MV_ACCESS_Exclusive
from frank.hikModule.CameraParams_header import MVCC_INTVALUE
from frank.handleModule.tools import cam_tool
from frank.handleModule.CamOperation_class import CameraOperation


def align_roi_params(offset_x, offset_y, width, height, max_width, max_height, alignment=4):
    """
    对齐 ROI 参数以满足海康相机要求
    
    海康相机的 ROI 参数通常需要满足对齐要求（4或8的倍数）
    
    Args:
        offset_x, offset_y: ROI 偏移量
        width, height: ROI 尺寸
        max_width, max_height: 相机最大分辨率
        alignment: 对齐字节数（默认4）
    
    Returns:
        (aligned_offset_x, aligned_offset_y, aligned_width, aligned_height)
    """
    # 向下对齐到 alignment 的倍数
    def align_down(value, align):
        return (value // align) * align
    
    # offset 向下对齐（确保不会越界）
    aligned_offset_x = align_down(offset_x, alignment)
    aligned_offset_y = align_down(offset_y, alignment)
    
    # width/height 向下对齐（确保 offset + size 不超过最大值）
    # 先计算可用的最大尺寸
    max_available_width = max_width - aligned_offset_x
    max_available_height = max_height - aligned_offset_y
    
    # 将 width/height 对齐，但不超过可用空间
    aligned_width = min(align_down(width, alignment), align_down(max_available_width, alignment))
    aligned_height = min(align_down(height, alignment), align_down(max_available_height, alignment))
    
    # 确保最小尺寸（至少64像素）
    aligned_width = max(aligned_width, 64)
    aligned_height = max(aligned_height, 64)
    
    print(f"🔧 ROI参数对齐:")
    print(f"   原始: offset=({offset_x}, {offset_y}), size=({width}×{height})")
    print(f"   对齐后: offset=({aligned_offset_x}, {aligned_offset_y}), size=({aligned_width}×{aligned_height})")
    
    return aligned_offset_x, aligned_offset_y, aligned_width, aligned_height


class CameraThread(QThread):
    """相机取流线程"""
    image_update = pyqtSignal(np.ndarray)  # 图像更新信号
    error_occurred = pyqtSignal(str)       # 错误信号
    
    def __init__(self, cam):
        super().__init__()
        self.cam = cam
        self.running = False
    
    def run(self):
        """线程运行"""
        self.running = True
        
        while self.running:
            try:
                # 获取图像
                ret, frame = cam_tool.get_image(self.cam)
                
                # 检查返回值
                if ret is None:
                    self.error_occurred.emit("相机返回值异常")
                    break
                
                if ret == MV_OK and frame is not None:
                    self.image_update.emit(frame)
                elif ret != MV_OK:
                    # 继续尝试，不立即退出
                    continue
                    
            except Exception as e:
                self.error_occurred.emit(f"取流错误: {str(e)}")
                break
    
    def stop(self):
        """停止线程"""
        self.running = False
        self.wait()


class CameraBase:
    """
    相机基类
    封装海康相机的基础操作
    """
    
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.deviceList = None
        self.cam = None
        self.cam_thread = None
        self.obj_cam_operation = None
        self.is_open = False
        self.last_frame = None
        
        # 加载配置
        self._load_config()
    
    def _load_config(self):
        """加载配置"""
        camera_config = self.config_manager.get_camera_config()
        roi_config = self.config_manager.get_roi_config()
        
        self.exposure_time = camera_config['exposure_time']
        self.gain = camera_config['gain']
        self.frame_rate = camera_config['frame_rate']
        self.cm_per_pixel = camera_config['cm_per_pixel']
        
        self.roi_offset_x = roi_config['offset_x']
        self.roi_offset_y = roi_config['offset_y']
        self.roi_width = roi_config['width']
        self.roi_height = roi_config['height']
        self.reverse_x = roi_config['reverse_x']
        self.reverse_y = roi_config['reverse_y']
    
    def enum_devices(self):
        """
        枚举相机设备
        返回: (success, message, device_list)
        """
        self.deviceList = cam_tool.enum_devices()
        
        if self.deviceList is None:
            return False, "未检测到相机", []
        
        dev_list = cam_tool.identify_different_devices(self.deviceList)
        return True, "相机枚举成功", dev_list
    
    def open_device(self, device_index):
        """
        打开相机设备
        device_index: 设备索引
        返回: (success, message)
        """
        if self.is_open:
            return False, "相机已打开"
        
        if device_index < 0 or self.deviceList is None:
            return False, "请先枚举相机"
        
        try:
            # 创建相机对象
            self.cam, _ = cam_tool.creat_camera(self.deviceList, device_index)
            
            # 打开设备
            ret = self.cam.MV_CC_OpenDevice(MV_ACCESS_Exclusive, 0)
            if ret != MV_OK:
                return False, f"打开相机失败: {cam_tool.ToHexStr(ret)}"
            
            # 创建相机操作对象
            self.obj_cam_operation = CameraOperation(self.cam, self.deviceList, device_index, True)
            
            # 设置 ROI（添加更多错误处理）
            print(f"设置ROI: offset=({self.roi_offset_x}, {self.roi_offset_y}), size=({self.roi_width}x{self.roi_height})")
            
            # 先尝试获取相机的最大分辨率
            try:
                from frank.hikModule.CameraParams_header import MVCC_INTVALUE
                
                stParam = MVCC_INTVALUE()
                ret1 = self.cam.MV_CC_GetIntValue("WidthMax", stParam)
                if ret1 == MV_OK:
                    max_width = stParam.nCurValue
                else:
                    # 从配置文件读取默认分辨率
                    camera_config = self.config_manager.get_camera_config()
                    max_width = camera_config.get('resolution_width', 4000)
                
                stParam = MVCC_INTVALUE()
                ret2 = self.cam.MV_CC_GetIntValue("HeightMax", stParam)
                if ret2 == MV_OK:
                    max_height = stParam.nCurValue
                else:
                    # 从配置文件读取默认分辨率
                    camera_config = self.config_manager.get_camera_config()
                    max_height = camera_config.get('resolution_height', 3000)
                
                print(f"📷 相机最大分辨率: {max_width} × {max_height}")
                
                # 检查并调整ROI参数
                adjusted = False
                
                if self.roi_width > max_width:
                    self.roi_width = max_width
                    print(f"⚠️  ROI宽度超限，调整为: {self.roi_width}")
                    adjusted = True
                
                if self.roi_height > max_height:
                    self.roi_height = max_height
                    print(f"⚠️  ROI高度超限，调整为: {self.roi_height}")
                    adjusted = True
                
                if self.roi_offset_x + self.roi_width > max_width:
                    self.roi_offset_x = 0
                    print(f"⚠️  ROI X偏移超限，重置为: 0")
                    adjusted = True
                
                if self.roi_offset_y + self.roi_height > max_height:
                    self.roi_offset_y = 0
                    print(f"⚠️  ROI Y偏移超限，重置为: 0")
                    adjusted = True
                
                if adjusted:
                    print(f"✅ 调整后的ROI参数: offset=({self.roi_offset_x}, {self.roi_offset_y}), size=({self.roi_width} × {self.roi_height})")
                else:
                    print(f"✅ ROI参数正常")
                    
            except Exception as e:
                print(f"⚠️  获取相机最大分辨率失败: {e}，使用配置文件中的值")
            
            # 对齐 ROI 参数（海康相机要求参数是4的倍数）
            aligned_offset_x, aligned_offset_y, aligned_width, aligned_height = align_roi_params(
                self.roi_offset_x, self.roi_offset_y,
                self.roi_width, self.roi_height,
                max_width, max_height,
                alignment=4  # 海康相机通常要求4字节对齐
            )
            
            # 更新为对齐后的参数
            self.roi_offset_x = aligned_offset_x
            self.roi_offset_y = aligned_offset_y
            self.roi_width = aligned_width
            self.roi_height = aligned_height
            
            ret = self.obj_cam_operation.set_roi(
                aligned_offset_x, aligned_offset_y, 
                aligned_width, aligned_height,
                self.reverse_x, self.reverse_y
            )
            
            if ret != MV_OK:
                self.close_device()
                return False, f"设置ROI失败: {cam_tool.ToHexStr(ret)} (请检查ROI参数是否超出相机范围)"
            
            # 设置相机参数
            ret = self.obj_cam_operation.Set_parameter(self.frame_rate, self.exposure_time, self.gain)
            if ret != MV_OK:
                self.close_device()
                return False, f"设置参数失败: {cam_tool.ToHexStr(ret)}"
            
            self.is_open = True
            return True, "相机打开成功"
        
        except Exception as e:
            self.close_device()
            return False, f"打开相机异常: {str(e)}"
    
    def start_grabbing(self):
        """
        开始取流
        返回: (success, message)
        """
        if not self.is_open:
            return False, "相机未打开"
        
        if self.cam_thread and self.cam_thread.running:
            return False, "相机已在取流"
        
        try:
            # 开始取流
            ret = cam_tool.start_grab(self.cam)
            
            # 检查返回值
            if ret is None:
                return False, "开始取流失败: 返回值为空"
            
            if ret != 0 and ret != MV_OK:
                return False, f"开始取流失败: {cam_tool.ToHexStr(ret)}"
            
            # 启动线程
            self.cam_thread = CameraThread(self.cam)
            self.cam_thread.start()
            
            return True, "开始取流"
        
        except Exception as e:
            return False, f"取流异常: {str(e)}"
    
    def stop_grabbing(self):
        """
        停止取流
        返回: (success, message)
        """
        if self.cam_thread:
            self.cam_thread.stop()
            self.cam.MV_CC_StopGrabbing()
            self.cam_thread = None
            return True, "停止取流"
        return True, "相机未在取流"
    
    def close_device(self):
        """
        关闭相机
        返回: (success, message)
        """
        if not self.is_open:
            return True, "相机未打开"
        
        # 停止取流
        self.stop_grabbing()
        
        # 关闭设备
        if self.cam:
            self.cam.MV_CC_CloseDevice()
            self.cam = None
        
        self.obj_cam_operation = None
        self.is_open = False
        
        return True, "相机已关闭"
    
    def capture_image(self):
        """
        拍摄一张图像
        返回: (success, image)
        """
        if not self.is_open:
            return False, None
        
        try:
            ret, frame = cam_tool.get_image(self.cam)
            
            # 检查返回值
            if ret is None:
                return False, None
            
            if ret == MV_OK and frame is not None:
                self.last_frame = frame.copy()
                return True, frame
            else:
                return False, None
                
        except Exception as e:
            print(f"拍摄异常: {e}")
            return False, None
    
    def set_parameters(self, frame_rate=None, exposure_time=None, gain=None):
        """
        设置相机参数
        返回: (success, message)
        """
        if not self.is_open or not self.obj_cam_operation:
            return False, "相机未打开"
        
        # 使用当前值或新值
        frame_rate = frame_rate if frame_rate is not None else self.frame_rate
        exposure_time = exposure_time if exposure_time is not None else self.exposure_time
        gain = gain if gain is not None else self.gain
        
        ret = self.obj_cam_operation.Set_parameter(frame_rate, exposure_time, gain)
        if ret != MV_OK:
            return False, f"设置参数失败: {cam_tool.ToHexStr(ret)}"
        
        # 更新配置
        self.frame_rate = frame_rate
        self.exposure_time = exposure_time
        self.gain = gain
        
        return True, "参数设置成功"
    
    def get_max_resolution(self):
        """
        获取相机的最大分辨率
        返回: (width, height) 或 (None, None)
        """
        if not self.cam:
            return None, None
        
        try:
            stParam = MVCC_INTVALUE()
            ret1 = self.cam.MV_CC_GetIntValue("WidthMax", stParam)
            max_width = stParam.nCurValue if ret1 == MV_OK else None
            
            stParam = MVCC_INTVALUE()
            ret2 = self.cam.MV_CC_GetIntValue("HeightMax", stParam)
            max_height = stParam.nCurValue if ret2 == MV_OK else None
            
            return max_width, max_height
        except Exception as e:
            print(f"获取最大分辨率失败: {e}")
            return None, None
    
    @staticmethod
    def image_to_pixmap(image, target_width, target_height):
        """
        将图像转换为 QPixmap
        image: numpy array (RGB格式，来自cam_tool.get_image的COLOR_BAYER_RG2RGB转换)
        target_width, target_height: 目标显示尺寸
        返回: QPixmap
        """
        if image is None:
            return None
        
        # 缩放图像
        img_resized = cam_tool.scale_img(image, target_width, target_height)
        
        # 转换为 QImage
        h, w, ch = img_resized.shape
        bytes_per_line = w * ch
        # 使用Format_RGB888并调用rgbSwapped()（与之前正确显示的版本一致）
        qt_image = QImage(img_resized.data, w, h, bytes_per_line, QImage.Format_RGB888)
        
        return QPixmap.fromImage(qt_image.rgbSwapped())


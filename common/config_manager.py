"""
配置管理器
负责读取和保存 config.ini 配置文件
"""
import configparser
import os


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_path='config.ini'):
        self.config_path = config_path
        self.config = configparser.ConfigParser()
        self.load()
    
    def load(self):
        """加载配置文件"""
        if os.path.exists(self.config_path):
            self.config.read(self.config_path, encoding='utf-8')
        else:
            # 创建默认配置
            self._create_default_config()
            self.save()
    
    def save(self):
        """保存配置文件"""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            self.config.write(f)
    
    def _create_default_config(self):
        """创建默认配置"""
        # 相机配置
        self.config['Camera'] = {
            'resolution_width': '4000',
            'resolution_height': '3000',
            'exposure_time': '50000',
            'gain': '0',
            'frame_rate': '30.0',
            'cm_per_pixel': '0.0057'
        }
        
        # ROI 配置
        self.config['ROI'] = {
            'offset_x': '0',
            'offset_y': '0',
            'width': '4000',
            'height': '3000',
            'reverse_x': 'True',
            'reverse_y': 'True'
        }
        
        # 天平配置
        self.config['Balance'] = {
            'port': 'COM3',
            'baudrate': '9600',
            'timeout': '1.0'
        }
        
        # 检测配置
        self.config['Detection'] = {
            'default_confidence': '25.0',
            'default_area_filter': '5.0',
            'inference_confidence': '0.25'
        }
        
        # 路径配置
        self.config['Paths'] = {
            'models_folder': 'models',
            'model_mapping_file': 'models/model_mapping.csv',
            'images_folder': 'data/images',
            'processed_folder': 'data/processed',
            'data_file': 'data/records.json'
        }
    
    # ========== 相机配置 ==========
    def get_camera_config(self):
        """获取相机配置"""
        return {
            'resolution_width': self.config.getint('Camera', 'resolution_width'),
            'resolution_height': self.config.getint('Camera', 'resolution_height'),
            'exposure_time': self.config.getfloat('Camera', 'exposure_time'),
            'gain': self.config.getfloat('Camera', 'gain'),
            'frame_rate': self.config.getfloat('Camera', 'frame_rate'),
            'cm_per_pixel': self.config.getfloat('Camera', 'cm_per_pixel')
        }
    
    def set_camera_config(self, **kwargs):
        """设置相机配置"""
        for key, value in kwargs.items():
            if key in self.config['Camera']:
                self.config['Camera'][key] = str(value)
        self.save()
    
    # ========== ROI 配置 ==========
    def get_roi_config(self):
        """获取 ROI 配置"""
        return {
            'offset_x': self.config.getint('ROI', 'offset_x'),
            'offset_y': self.config.getint('ROI', 'offset_y'),
            'width': self.config.getint('ROI', 'width'),
            'height': self.config.getint('ROI', 'height'),
            'reverse_x': self.config.getboolean('ROI', 'reverse_x'),
            'reverse_y': self.config.getboolean('ROI', 'reverse_y')
        }
    
    def set_roi_config(self, offset_x, offset_y, width, height, reverse_x=None, reverse_y=None):
        """设置 ROI 配置"""
        self.config['ROI']['offset_x'] = str(offset_x)
        self.config['ROI']['offset_y'] = str(offset_y)
        self.config['ROI']['width'] = str(width)
        self.config['ROI']['height'] = str(height)
        if reverse_x is not None:
            self.config['ROI']['reverse_x'] = str(reverse_x)
        if reverse_y is not None:
            self.config['ROI']['reverse_y'] = str(reverse_y)
        self.save()
    
    # ========== 天平配置 ==========
    def get_balance_config(self):
        """获取天平配置"""
        return {
            'port': self.config.get('Balance', 'port'),
            'baudrate': self.config.getint('Balance', 'baudrate'),
            'timeout': self.config.getfloat('Balance', 'timeout')
        }
    
    def set_balance_config(self, port=None, baudrate=None, timeout=None):
        """设置天平配置"""
        if port:
            self.config['Balance']['port'] = port
        if baudrate:
            self.config['Balance']['baudrate'] = str(baudrate)
        if timeout:
            self.config['Balance']['timeout'] = str(timeout)
        self.save()
    
    # ========== 检测配置 ==========
    def get_detection_config(self):
        """获取检测配置"""
        return {
            'default_confidence': self.config.getfloat('Detection', 'default_confidence'),
            'default_area_filter': self.config.getfloat('Detection', 'default_area_filter'),
            'inference_confidence': self.config.getfloat('Detection', 'inference_confidence')
        }
    
    def set_detection_config(self, **kwargs):
        """设置检测配置"""
        for key, value in kwargs.items():
            if key in self.config['Detection']:
                self.config['Detection'][key] = str(value)
        self.save()
    
    # ========== 路径配置 ==========
    def get_paths_config(self):
        """获取路径配置"""
        return {
            'models_folder': self.config.get('Paths', 'models_folder'),
            'model_mapping_file': self.config.get('Paths', 'model_mapping_file'),
            'images_folder': self.config.get('Paths', 'images_folder'),
            'processed_folder': self.config.get('Paths', 'processed_folder'),
            'data_file': self.config.get('Paths', 'data_file')
        }
    
    def get(self, section, option, fallback=None):
        """通用获取方法"""
        return self.config.get(section, option, fallback=fallback)
    
    def getint(self, section, option, fallback=None):
        """获取整数"""
        return self.config.getint(section, option, fallback=fallback)
    
    def getfloat(self, section, option, fallback=None):
        """获取浮点数"""
        return self.config.getfloat(section, option, fallback=fallback)
    
    def getboolean(self, section, option, fallback=None):
        """获取布尔值"""
        return self.config.getboolean(section, option, fallback=fallback)


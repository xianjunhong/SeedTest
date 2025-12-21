"""
模型管理器
负责模型的扫描、加载、推理和结果处理
"""
import os
import csv
import numpy as np
from ultralytics import YOLO
from PyQt5.QtCore import QThread, pyqtSignal


class ModelLoaderThread(QThread):
    """模型加载线程"""
    model_loaded = pyqtSignal(object)  # 模型加载成功
    load_failed = pyqtSignal(str)      # 模型加载失败
    
    def __init__(self, model_path):
        super().__init__()
        self.model_path = model_path
    
    def run(self):
        """加载模型"""
        try:
            model = YOLO(self.model_path)
            # 模型预热
            dummy_img = np.zeros((640, 640, 3), dtype=np.uint8)
            model.predict(dummy_img, verbose=False)
            self.model_loaded.emit(model)
        except Exception as e:
            self.load_failed.emit(f"模型加载失败: {str(e)}")


class ModelManager:
    """模型管理器"""
    
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.models_folder = config_manager.get_paths_config()['models_folder']
        self.mapping_file = config_manager.get_paths_config()['model_mapping_file']
        self.current_model = None
        self.current_model_name = None
        self.current_model_type = None
    
    def scan_models(self):
        """
        扫描模型文件夹，返回模型列表
        返回格式: [(model_file, display_name, model_type), ...]
        """
        if not os.path.exists(self.models_folder):
            os.makedirs(self.models_folder)
            return []
        
        # 读取映射文件
        model_mapping = self._load_model_mapping()
        
        # 扫描 .pt 文件
        model_files = [f for f in os.listdir(self.models_folder) if f.endswith('.pt')]
        
        models = []
        for model_file in model_files:
            # 获取显示名称
            display_name = model_mapping.get(model_file, model_file.replace('.pt', ''))
            
            # 判断模型类型
            model_type = self._detect_model_type(model_file)
            
            models.append((model_file, display_name, model_type))
        
        return models
    
    def _load_model_mapping(self):
        """加载模型映射文件"""
        mapping = {}
        
        if os.path.exists(self.mapping_file):
            try:
                with open(self.mapping_file, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    for row in reader:
                        if len(row) >= 2:
                            mapping[row[0]] = row[1]
            except Exception as e:
                print(f"读取映射文件失败: {e}")
        
        return mapping
    
    def _detect_model_type(self, model_file):
        """
        根据文件名判断模型类型
        返回: 'obb', 'det', 'seg'
        """
        filename_lower = model_file.lower()
        
        if 'obb' in filename_lower:
            return 'obb'
        elif 'seg' in filename_lower:
            return 'seg'
        else:
            return 'det'
    
    def load_model(self, model_file):
        """
        加载模型（同步）
        返回: (success, message, model)
        """
        model_path = os.path.join(self.models_folder, model_file)
        
        if not os.path.exists(model_path):
            return False, f"模型文件不存在: {model_path}", None
        
        try:
            model = YOLO(model_path)
            # 模型预热
            dummy_img = np.zeros((640, 640, 3), dtype=np.uint8)
            model.predict(dummy_img, verbose=False)
            
            self.current_model = model
            self.current_model_name = model_file
            self.current_model_type = self._detect_model_type(model_file)
            
            return True, "模型加载成功", model
        except Exception as e:
            return False, f"模型加载失败: {str(e)}", None
    
    
    def get_current_model_info(self):
        """获取当前模型信息"""
        return {
            'name': self.current_model_name,
            'type': self.current_model_type,
            'loaded': self.current_model is not None
        }


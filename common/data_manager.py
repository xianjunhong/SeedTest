"""
数据管理器
负责数据的保存、加载、导出
"""
import json
import os
from datetime import datetime
import pandas as pd


class DataManager:
    """数据管理器"""
    
    def __init__(self, config_manager):
        self.config_manager = config_manager
        paths = config_manager.get_paths_config()
        self.data_file = paths['data_file']
        self.images_folder = paths['images_folder']
        self.processed_folder = paths['processed_folder']
        
        # 确保文件夹存在
        self._ensure_folders()
        
        # 确保数据文件存在
        self._ensure_data_file()
    
    def _ensure_folders(self):
        """确保必要的文件夹存在"""
        for folder in [self.images_folder, self.processed_folder]:
            if not os.path.exists(folder):
                os.makedirs(folder)
    
    def _ensure_data_file(self):
        """确保数据文件存在"""
        if not os.path.exists(self.data_file):
            # 创建父目录
            directory = os.path.dirname(self.data_file)
            if directory:
                os.makedirs(directory, exist_ok=True)
            
            # 创建空 JSON 文件
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=4)
    
    def load_records(self):
        """
        加载所有记录
        返回: list of dict
        """
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载数据失败: {e}")
            return []
    
    def save_record(self, record):
        """
        保存一条记录
        record: dict，包含所有考种数据
        """
        # 加载现有数据
        records = self.load_records()
        
        # 添加新记录
        records.append(record)
        
        # 保存
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(records, f, ensure_ascii=False, indent=4)
    
    def delete_record(self, record_id):
        """
        删除一条记录
        record_id: 记录的唯一ID
        返回: (success, message)
        """
        try:
            # 加载数据
            records = self.load_records()
            
            # 找到要删除的记录
            record_to_delete = None
            for record in records:
                if record.get('id') == record_id:
                    record_to_delete = record
                    break
            
            if not record_to_delete:
                return False, "记录不存在"
            
            # 删除图像文件
            image_path = os.path.join(self.images_folder, f"{record_id}.jpg")
            processed_path = os.path.join(self.processed_folder, f"{record_id}.jpg")
            
            if os.path.exists(image_path):
                os.remove(image_path)
            if os.path.exists(processed_path):
                os.remove(processed_path)
            
            # 从列表中删除
            records = [r for r in records if r.get('id') != record_id]
            
            # 保存
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(records, f, ensure_ascii=False, indent=4)
            
            return True, "删除成功"
        
        except Exception as e:
            return False, f"删除失败: {str(e)}"
    
    def delete_all_records(self):
        """
        删除所有记录
        返回: (success, message)
        """
        try:
            # 清空数据文件
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=4)
            
            # 清空图像文件夹（可选）
            # 如果不想删除图像，注释掉下面的代码
            for folder in [self.images_folder, self.processed_folder]:
                if os.path.exists(folder):
                    for file in os.listdir(folder):
                        file_path = os.path.join(folder, file)
                        if os.path.isfile(file_path):
                            os.remove(file_path)
            
            return True, "所有数据已清空"
        
        except Exception as e:
            return False, f"清空失败: {str(e)}"
    
    def export_to_excel(self, output_path):
        """
        导出数据到 Excel
        output_path: 输出文件路径
        返回: (success, message)
        """
        try:
            records = self.load_records()
            
            if not records:
                return False, "没有数据可导出"
            
            # 如果文件已存在，先尝试删除（允许覆盖）
            if os.path.exists(output_path):
                try:
                    os.remove(output_path)
                except PermissionError:
                    return False, f"导出失败: 文件已被打开，请先关闭文件\n{output_path}"
                except Exception as e:
                    return False, f"导出失败: 无法删除旧文件\n{str(e)}"
            
            # 转换为 DataFrame
            df = pd.DataFrame(records)
            
            # 调整列顺序
            desired_columns = [
                'id', 'timestamp', 'model_name', 'variety_code', 'count', 
                'avg_length', 'avg_width', 'weight', 'thousand_seed_weight',
                'image_path', 'processed_image_path'
            ]
            
            # 只保留存在的列
            columns = [col for col in desired_columns if col in df.columns]
            df = df[columns]
            
            # 导出
            if output_path.endswith('.csv'):
                df.to_csv(output_path, index=False, encoding='utf-8-sig')
            else:
                df.to_excel(output_path, index=False, engine='openpyxl')
            
            return True, f"导出成功: {output_path}"
        
        except PermissionError as e:
            return False, f"导出失败: 文件已被打开，请先关闭文件\n{output_path}"
        except Exception as e:
            return False, f"导出失败: {str(e)}"
    
    def create_record_template(self, record_id, model_name, variety_code, count, avg_length, avg_width, 
                               weight, thousand_seed_weight, confidence_threshold, area_threshold):
        """
        创建记录模板
        返回: dict
        """
        now = datetime.now()
        timestamp = now.strftime('%Y-%m-%d %H:%M:%S')
        
        image_path = os.path.abspath(os.path.join(self.images_folder, f"{record_id}.jpg"))
        processed_path = os.path.abspath(os.path.join(self.processed_folder, f"{record_id}.jpg"))
        
        return {
            'id': record_id,
            'timestamp': timestamp,
            'model_name': model_name,
            'variety_code': variety_code,
            'count': count,
            'avg_length': round(avg_length, 2),
            'avg_width': round(avg_width, 2),
            'weight': round(weight, 2),
            'thousand_seed_weight': round(thousand_seed_weight, 2),
            'confidence_threshold': confidence_threshold,
            'area_threshold': area_threshold,
            'image_path': image_path,
            'processed_image_path': processed_path
        }


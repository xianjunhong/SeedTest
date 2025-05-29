from dataclasses import dataclass, field
from enum import Enum

import cv2
import requests
import time
import base64
import json


TOKEN = "56a2bb0e0b2e702e057d28f98f2161c8"  # 放在类定义之前
class TaskStatus(Enum):
    WAITING = "waiting"
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"

@dataclass
class DetectionResult:
    bbox: list = field(default_factory=list)  # 改为使用默认工厂函数
    embedding: str = None
    scores: list = None
    status: TaskStatus = TaskStatus.PENDING

class TrexAPI:
    def __init__(self, token):
        self.base_url = "https://api.deepdataspace.com/v2"
        self.headers = {
            "Token": token,
            "Content-Type": "application/json"
        }
    
    def create_task(self, payload):
        url = f"{self.base_url}/task/trex/detection"
        response = requests.post(url, json=payload, headers=self.headers)
        return response.json()
    
    def get_task_status(self, task_uuid):
        url = f"{self.base_url}/task_status/{task_uuid}"
        response = requests.get(url, headers=self.headers)
        return response.json()


class Trex:
    def __init__(self, image, prompt, threshold=0.4):
        self.api = TrexAPI(TOKEN)
        self.image = image  # 注意，这里改成了 image 是 cv2读进来的numpy数组
        self.prompt = self._build_prompt(prompt)
        self.threshold = threshold
        self.result = DetectionResult()

    def _encode_image(self):
        """把OpenCV读进来的numpy图片编码成base64"""
        try:
            # 将 numpy数组 编码成 JPEG 格式的内存缓存
            success, encoded_image = cv2.imencode('.jpg', self.image)
            if not success:
                raise RuntimeError("Image encoding failed: cv2.imencode failed")

            # 再进行 base64 编码
            b64_string = base64.b64encode(encoded_image.tobytes()).decode()
            return "data:image/jpeg;base64," + b64_string
        except Exception as e:
            raise RuntimeError(f"Image encoding failed: {str(e)}")

    def _build_prompt(self, prompt_input):
        """支持 tuple、list[tuple]、embedding字符串三种"""
        if isinstance(prompt_input, tuple):
            return {
                "type": "visual_images",
                "visual_images": [{
                    "interactions": [{"type": "rect", "rect": prompt_input}]
                }]
            }
        elif isinstance(prompt_input, list):
            interactions = [{"type": "rect", "rect": rect} for rect in prompt_input]
            return {
                "type": "visual_images",
                "visual_images": [{
                    "interactions": interactions
                }]
            }
        elif isinstance(prompt_input, str):
            return {
                "type": "embedding",
                "embedding": prompt_input
            }
        else:
            raise ValueError(f"Unsupported prompt type: {type(prompt_input)}")

    def run_async(self):
        """异步启动任务"""
        try:
            payload = {
                "model": "T-Rex-2.0",
                "image": self._encode_image(),
                "targets": ["bbox", "embedding"],
                "prompt": self.prompt
            }
            response = self.api.create_task(payload)

            # 美化打印！
            print("Create Task Response:")
            print(json.dumps(response, indent=2, ensure_ascii=False))

            if response.get("code") == 0:
                self.result.status = TaskStatus.PENDING
                self.task_uuid = response["data"]["task_uuid"]
                return True
            return False
        except Exception as e:
            self.result.status = TaskStatus.FAILED
            raise RuntimeError(f"Task creation failed: {str(e)}")

    def poll_result(self, timeout=10, interval=1):
        """轮询任务结果"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            response = self.api.get_task_status(self.task_uuid)
            
            status = response["data"]["status"].lower()  # 统一转小写
            self.result.status = TaskStatus(status)
            
            # 修改判断条件
            if self.result.status == TaskStatus.SUCCESS:
                self._parse_result(response)
                return True
            elif self.result.status in [TaskStatus.FAILED]:
                raise RuntimeError(f"API任务异常，状态: {status}")
                
            time.sleep(interval)
        raise TimeoutError("Task execution timed out")

    def _parse_result(self, response):
        """解析API响应"""
        result = response["data"]["result"]
        self.result.embedding = result.get("embedding")
        
        # 解析检测结果
        self.result.bbox = [
            obj["bbox"] for obj in result["objects"]
            if obj["score"] > self.threshold
        ]
        self.result.scores = [
            obj["score"] for obj in result["objects"]
            if obj["score"] > self.threshold
        ]



if __name__ == "__main__":
    img = cv2.imread("output_with_rect.jpg")  # 这里提前用OpenCV读

    detector = Trex(
        image=img,                   # 改了，不是路径，是读好的图
        prompt=(388, 784, 728, 1100),
        threshold=0.5
    )

    
    if detector.run_async():
        try:
            detector.poll_result()
            print("检测结果:", detector.result.bbox)
            # 绘制出来
            img = cv2.imread(image_path)
            for box in detector.result.bbox:
                x1, y1, x2, y2 = map(int, box)  # 或者直接 int(box[0]), int(box[1]), ...
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)

            cv2.imshow("Image with Rectangle", img)
            # 等待按键（0 表示无限等待）
            cv2.waitKey(0)

            # 关闭所有 OpenCV 窗口
            cv2.destroyAllWindows()
            print("Embedding:", detector.result.embedding)
        except Exception as e:
            print(f"检测失败: {str(e)}")



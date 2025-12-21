"""
天平管理器
负责天平的连接、数据读取和异常检测
"""
import serial
import serial.tools.list_ports
from PyQt5.QtCore import QThread, pyqtSignal
import time


class BalanceThread(QThread):
    """天平数据读取线程"""
    data_received = pyqtSignal(str)  # 正常数据信号
    error_occurred = pyqtSignal(str)  # 错误信号
    connection_lost = pyqtSignal()   # 连接丢失信号
    
    def __init__(self, port, baudrate=9600, timeout=1.0):
        super().__init__()
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial_connection = None
        self.running = False
        self.last_weight = 0.0
        self.error_count = 0
        self.max_errors = 5  # 最大错误次数
    
    def run(self):
        """线程运行"""
        try:
            self.serial_connection = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout
            )
            self.running = True
            self.error_count = 0
            
            # 有些天平需要发送命令才会返回数据
            try:
                # 尝试常见的查询命令
                self.serial_connection.write(b'S\r\n')  # 获取重量
                time.sleep(0.1)
            except:
                pass
            
            loop_count = 0
            last_report = time.time()
            
            while self.running:
                try:
                    loop_count += 1
                    waiting = self.serial_connection.in_waiting
                    
                    # 每5秒发送查询命令（某些天平需要）
                    if time.time() - last_report > 5:
                        last_report = time.time()
                        try:
                            self.serial_connection.write(b'S\r\n')
                        except:
                            pass
                    
                    if waiting > 0:
                        # 使用 read_until 读取到 = 为止（保证读取完整数据包）
                        try:
                            raw_data = self.serial_connection.read_until(b'=')
                            line = raw_data.decode('utf-8', errors='ignore').strip()
                        except:
                            line = ""
                        
                        if line:
                            # 尝试解析重量数据
                            weight = self._parse_weight(line)
                            
                            if weight is not None:
                                # 只检测负数异常
                                if weight < 0:
                                    self.error_occurred.emit(f"天平数据异常：负数 {weight}g")
                                
                                self.last_weight = weight
                                self.data_received.emit(f"{weight:.2f}")
                                self.error_count = 0  # 重置错误计数
                            else:
                                # 解析失败
                                self.error_count += 1
                                if self.error_count > self.max_errors:
                                    self.error_occurred.emit(f"天平数据解析失败次数过多")
                    
                    time.sleep(0.1)  # 100ms 读取一次
                    
                except serial.SerialException as e:
                    self.error_occurred.emit(f"串口错误: {str(e)}")
                    self.connection_lost.emit()
                    break
                except Exception as e:
                    self.error_count += 1
                    if self.error_count > self.max_errors:
                        self.error_occurred.emit(f"读取错误: {str(e)}")
                        break
        
        except Exception as e:
            self.error_occurred.emit(f"天平连接失败: {str(e)}")
        finally:
            self.close()
    
    def _parse_weight(self, data):
        """
        解析重量数据
        天平格式: 数据是倒序的，如 '0292.50=' 表示 5.292g
        需要去掉 '='，然后反转字符串
        """
        try:
            # 去掉所有 '=' 符号
            data = data.strip('=')
            
            # 如果数据为空，返回 None
            if not data:
                return None
            
            # 反转字符串 (关键步骤!)
            data = data[::-1]
            
            # 转换为浮点数
            weight = float(data)
            return weight
        except ValueError:
            return None
    
    def zero_balance(self):
        """天平清零"""
        if self.serial_connection and self.serial_connection.is_open:
            try:
                # 发送清零命令（根据你的天平协议调整）
                # 常见清零命令: 'T\r\n', 'Z\r\n', 'TARE\r\n'
                self.serial_connection.write(b'T\r\n')
                time.sleep(0.2)
            except Exception as e:
                self.error_occurred.emit(f"清零失败: {str(e)}")
    
    def stop(self):
        """停止线程"""
        self.running = False
        self.wait()
    
    def close(self):
        """关闭串口"""
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()


class BalanceManager:
    """天平管理器"""
    
    def __init__(self):
        self.balance_thread = None
        self.is_connected = False
        self.current_weight = 0.0
    
    @staticmethod
    def scan_ports():
        """
        扫描可用串口
        返回格式: ["COM3 - USB Serial Port", "COM5 - Arduino"]
        """
        ports = serial.tools.list_ports.comports()
        port_list = []
        for port in ports:
            # 格式: "COM3 - USB Serial Port (描述信息)"
            if port.description and port.description != 'n/a':
                port_str = f"{port.device} - {port.description}"
            else:
                port_str = port.device
            port_list.append(port_str)
        return port_list
    
    @staticmethod
    def get_port_name(port_string):
        """
        从格式化的串口字符串中提取实际的串口名
        例如: "COM3 - USB Serial Port" -> "COM3"
        """
        if " - " in port_string:
            return port_string.split(" - ")[0]
        return port_string
    
    def connect(self, port, baudrate=9600, timeout=1.0):
        """连接天平"""
        if self.is_connected:
            return False, "天平已连接"
        
        try:
            self.balance_thread = BalanceThread(port, baudrate, timeout)
            self.is_connected = True
            return True, "天平连接成功"
        except Exception as e:
            return False, f"天平连接失败: {str(e)}"
    
    def start(self):
        """开始读取数据"""
        if self.balance_thread:
            self.balance_thread.start()
    
    def disconnect(self):
        """断开天平连接"""
        if self.balance_thread:
            self.balance_thread.stop()
            self.balance_thread = None
        self.is_connected = False
        self.current_weight = 0.0
    
    def zero(self):
        """天平清零"""
        if self.balance_thread:
            self.balance_thread.zero_balance()
    
    def get_weight(self):
        """获取当前重量"""
        return self.current_weight


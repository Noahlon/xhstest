# logger.py
# 统一日志模块 - 支持录制时间显示（格式：分:秒:帧）

import time
import threading

class RecordingLogger:
    """
    录制日志类
    时间格式: MM:SS:FF (分:秒:帧)
    帧率: 30fps，帧范围 00-29
    示例: 03:02:22 表示 3分2秒22帧
    """
    
    def __init__(self, fps: int = 30):
        """
        初始化日志器
        :param fps: 帧率，默认30
        """
        self.fps = fps
        self._start_time = None
        self._lock = threading.Lock()
    
    def start(self):
        """开始计时"""
        with self._lock:
            self._start_time = time.time()
    
    def stop(self):
        """停止计时"""
        with self._lock:
            self._start_time = None
    
    def reset(self):
        """重置计时器"""
        self.stop()
    
    def get_time(self) -> str:
        """
        获取当前录制时间
        :return: 格式 MM:SS:FF
        """
        if self._start_time is None:
            return "00:00:00"
        
        elapsed = time.time() - self._start_time
        
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)
        frames = int((elapsed - int(elapsed)) * self.fps)
        frames = min(frames, self.fps - 1)  # 确保不超过最大帧
        
        return f"{minutes:02d}:{seconds:02d}:{frames:02d}"
    
    def get_elapsed_seconds(self) -> float:
        """获取经过的秒数"""
        if self._start_time is None:
            return 0.0
        return time.time() - self._start_time
    
    def log(self, message: str, device_id: str = "", app_name: str = ""):
        """
        打印日志
        :param message: 日志消息
        :param device_id: 设备ID（可选）
        :param app_name: 应用名称（可选）
        """
        with self._lock:
            time_str = self.get_time()
            
            if device_id and app_name:
                print(f"[{time_str}] [{device_id} {app_name}] {message}")
            elif device_id:
                print(f"[{time_str}] [{device_id}] {message}")
            else:
                print(f"[{time_str}] {message}")


# ============== 全局实例（方便直接使用） ==============
_global_logger = RecordingLogger(fps=30)

def start_recording():
    """开始录制计时"""
    _global_logger.start()

def stop_recording():
    """停止录制计时"""
    _global_logger.stop()

def reset_recording():
    """重置录制计时"""
    _global_logger.reset()

def get_recording_time() -> str:
    """获取录制时间 MM:SS:FF"""
    return _global_logger.get_time()

def log(message: str, device_id: str = "", app_name: str = ""):
    """打印带时间的日志"""
    _global_logger.log(message, device_id, app_name)


# 保存日志

# ============== 使用示例 ==============
if __name__ == "__main__":
    # 测试示例
    start_recording()
    
    log("测试开始")
    time.sleep(1.5)
    log("操作1完成", "device-001", "抖音")
    time.sleep(2.3)
    log("操作2完成", "device-001", "抖音")
    time.sleep(0.5)
    log("操作3完成", "device-002", "快手")
    
    print(f"\n当前录制时间: {get_recording_time()}")
    
    stop_recording()
    log("测试结束")

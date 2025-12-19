import subprocess
import time
import os
import signal
import sys
from concurrent.futures import ThreadPoolExecutor

# 配置
RECORD_LIMIT_TIME = 60 * 10  # ADB限制最长录制180秒
PHONE_SAVE_PATH = "/sdcard/screen_record.mp4" # 手机端临时存储路径
# 获取当前时间
datetime = time.strftime("%Y%m%d_%H%M%S")
PC_SAVE_DIR = f"./records/{datetime}/" # 电脑端保存路径

# 全局变量
executor = None
recording_futures = []
current_devices = []



def start_recording(serial):
    """在指定设备上开始录制"""
    print(f"[{serial}] 开始录制...")
    # --time-limit 指定最大时长，--verbose 显示信息
    cmd = f"adb -s {serial} shell screenrecord --time-limit {RECORD_LIMIT_TIME} {PHONE_SAVE_PATH}"
    subprocess.Popen(cmd, shell=True)

def stop_recording(serial):
    """发送信号停止录制 (模拟 Ctrl+C的效果，否则视频可能损坏)"""
    print(f"[{serial}] 正在停止录制并保存...")
    # 使用 pkill -2 (SIGINT) 发送中断信号，让 screenrecord 正常结束并写入文件尾
    cms = subprocess.run(f"adb -s {serial} root", shell=True)
    subprocess.Popen(f"adb -s {serial} shell pkill -9 -f screenrecord", shell=True)
def get_devices():
    """获取已连接设备的序列号列表"""
    result = subprocess.run(["adb", "devices"], capture_output=True, text=True)
    lines = result.stdout.strip().split("\n")[1:]
    devices = [line.split("\t")[0] for line in lines if "device" in line]
    # 结束原来的录制进程，防止冲突
    for dev in devices:
        subprocess.run(f"adb -s {dev} shell pkill -9 -f screenrecord", shell=True)
    return devices
def pull_video(serial):
    """将视频从手机拉取到电脑"""
    if not os.path.exists(PC_SAVE_DIR):
        os.makedirs(PC_SAVE_DIR)
    
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"{serial}_{timestamp}.mp4"
    pc_path = os.path.join(PC_SAVE_DIR, filename)
    
    print(f"[{serial}] 正在导出视频到: {pc_path}")
    cmd = f"adb -s {serial} pull {PHONE_SAVE_PATH} {pc_path}"
    subprocess.run(cmd, shell=True)
    
    # 清理手机上的文件
    subprocess.run(f"adb -s {serial} shell rm {PHONE_SAVE_PATH}", shell=True)


# 启动所有录制
def start_all_recordings():
    global recording_futures, current_devices, executor
    current_devices = get_devices()
      # 使用线程池同时启动录制
    executor = ThreadPoolExecutor(max_workers=len(current_devices))
    try:
        # 启动录制任务
        for dev in current_devices:
            recording_futures.append(executor.submit(start_recording, dev))
    except Exception as e:
        print(f"启动录制时出错: {e}")
        # 确保所有线程都被取消
        for future in recording_futures:
            future.cancel()
        raise
    print("启动所有设备录制...")

# 停止所有录制
def stop_all_recordings():
    global recording_futures, executor
    print("停止所有设备录制...")
    for dev in current_devices:
        stop_recording(dev)
    
    for future in recording_futures:
        future.result()  # 等待每个线程完成
    time.sleep(2)  # 额外等待2秒确保文件写入完成
    for dev in current_devices:
        pull_video(dev)
    
    executor.shutdown(wait=True)
    sys.exit(0)
    
def main():
    devices = get_devices()
    if not devices:
        print("未检测到设备！")
        return

    print(f"检测到 {len(devices)} 台设备: {devices}")
    print(">>> 按 Ctrl + C 停止录制 <<<")

    # 使用线程池同时启动录制
    executor = ThreadPoolExecutor(max_workers=len(devices))
    futures = []
    
    try:
        # 启动录制任务
        for dev in devices:
            futures.append(executor.submit(start_recording, dev))

        
        # 保持主线程运行，等待用户中断
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n接收到停止指令，正在处理...")
        
        # 1. 发送停止命令给所有手机
        for dev in devices:
            stop_recording(dev)
        
        # 2. 等待录制进程彻底结束 (稍微延时确保文件写入完成)
        print("等待录制进程结束...")
        for future in futures:
            future.result()  # 等待每个线程完成
        
        time.sleep(2)  # 额外等待2秒确保文件写入完成
        # 3. 导出视频
        for dev in devices:
            pull_video(dev)
            
        print("\n所有任务完成！")

        # 强制退出线程池
        executor.shutdown(wait=False)
        sys.exit(0)

if __name__ == "__main__":
    main()
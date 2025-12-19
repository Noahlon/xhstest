import subprocess
import os
import sys
from concurrent.futures import ThreadPoolExecutor

# === 配置部分 ===
SOURCE_PATH = "/sdcard/DCIM/ScreenRecorder/"  # 手机源目录
BASE_OUTPUT_DIR = "./records"                 # 电脑保存根目录
MAX_WORKERS = 10                              # 最大并发数量（根据USB口数量调整）

# 应用包名映射 (优先级从上到下)
TARGET_APPS = [
    {"name": "抖音", "package": "com.ss.android.ugc.aweme"},
    {"name": "小红书", "package": "com.xingin.xhs"},
    {"name": "快手", "package": "com.smile.gifmaker"}
]

def run_adb_command(cmd_list):
    """运行ADB命令并返回标准输出"""
    try:
        # 使用 utf-8 编码读取，防止中文乱码
        result = subprocess.run(cmd_list, capture_output=True, text=True, encoding='utf-8')
        return result.stdout.strip()
    except Exception as e:
        print(f"执行命令错误: {e}")
        return ""

def get_usb_devices():
    """获取所有USB连接的设备序列号"""
    output = run_adb_command(["adb", "devices", "-l"])
    devices = []
    
    lines = output.split('\n')
    for line in lines:
        if "device " in line and "usb:" in line:
            parts = line.split()
            serial = parts[0]
            print(f"[系统] 发现 USB 设备: {serial}")
            devices.append(serial)
    return devices

def get_devices():
    """获取所有连接的设备序列号"""
    output = run_adb_command(["adb", "devices", "-l"])
    devices = []
    
    lines = output.split('\n')
    for line in lines:
        if "device " in line:
            parts = line.split()
            serial = parts[0]
            print(f"[系统] 发现设备: {serial}")
            devices.append(serial)
    return devices
def check_installed_app(serial):
    """检测设备安装的目标应用"""
    installed_packages = run_adb_command(["adb", "-s", serial, "shell", "pm", "list", "packages", "-3"])
    
    for app in TARGET_APPS:
        if app["package"] in installed_packages:
            return app["name"]
    return None

def get_file_list(serial, remote_path):
    """获取远程目录下的文件列表，并过滤隐藏文件"""
    cmd = ["adb", "-s", serial, "shell", "ls", remote_path]
    output = run_adb_command(cmd)
    
    if "No such file" in output or "Not a directory" in output:
        return []

    file_list = []
    lines = output.splitlines()
    for filename in lines:
        filename = filename.strip()
        if not filename:
            continue
        # 过滤隐藏文件
        if filename.startswith('.'):
            continue
        file_list.append(filename)
        
    return file_list

def process_device_task(serial):
    """
    单个设备的处理逻辑（将在独立线程中运行）
    """
    prefix = f"[{serial}]" #用于日志区分
    print(f"{prefix} 开始检测应用...")
    
    app_name = check_installed_app(serial)
    
    if not app_name:
        print(f"{prefix} 未安装目标应用，跳过。")
        return

    print(f"{prefix} 检测到应用: {app_name}，正在获取文件列表...")
    
    # 获取文件列表
    files_to_copy = get_file_list(serial, SOURCE_PATH)
    
    if not files_to_copy:
        print(f"{prefix} 目录为空或不存在: {SOURCE_PATH}")
        return

    # 创建目标目录 (os.makedirs with exist_ok=True 是线程安全的)
    target_dir = os.path.join(BASE_OUTPUT_DIR, app_name)
    os.makedirs(target_dir, exist_ok=True)
    
    print(f"{prefix} 发现 {len(files_to_copy)} 个文件，准备下载到 {target_dir}")

    success_count = 0
    for filename in files_to_copy:
        remote_file = f"{SOURCE_PATH.rstrip('/')}/{filename}"
        local_file = os.path.join(target_dir, filename)

        # 检查本地是否已存在（防止不同手机有同名文件导致的文件冲突警告）
        # 注意：如果一定要覆盖，可以去掉这个if，但多线程写同一个文件会损坏文件
        if os.path.exists(local_file):
            # 获取文件大小对比，如果一样则跳过，不一样则覆盖（简单逻辑）
            pass 

        print(f"{prefix} 正在拉取: {filename}")
        
        # 执行 adb pull
        cmd = ["adb", "-s", serial, "pull", remote_file, local_file]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        
        if proc.returncode == 0:
            success_count += 1
        else:
            print(f"{prefix} [失败] {filename}: {proc.stderr.strip()}")

    print(f"{prefix} 任务完成。成功复制: {success_count}/{len(files_to_copy)}")

def main():
    print("=== ADB 多设备并发导出工具 ===")
    
    # 1. 获取设备列表
    devices = get_devices()
    
    if not devices:
        print("未检测到 USB 连接的设备。")
        return

    print(f"准备处理 {len(devices)} 台设备...\n")

    # 2. 使用线程池并发处理
    # max_workers 决定了同时有多少个 adb pull 进程在跑
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # 将每个设备的任务提交给线程池
        executor.map(process_device_task, devices)

    print("\n=== 所有设备处理线程已结束 ===")

if __name__ == "__main__":
    main()

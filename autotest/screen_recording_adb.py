import subprocess
import os
import threading
from typing import Dict


# 记录每台设备的录制线程，方便需要时等待
record_threads: Dict[str, threading.Thread] = {}


def start_record(device_id: str, filename: str, duration: int):
    print(f"[{device_id}] 开始录制 {filename}，时长 {duration} 秒")
    cmd = [
        "adb", "-s", device_id,
        "shell", "screenrecord",
        "--time-limit", str(duration),
        f"/sdcard/{filename}"
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    if result.returncode != 0:
        print(f"[{device_id}] 录制命令出错: {result.stderr}")
    else:
        print(f"[{device_id}] 录制结束: {filename}")

    


def copy_record(device_id: str, filename: str, local_dir: str = "./records", delete_remote: bool = True):
    # 打印复制录制信息
    print(f"[{device_id}] 开始复制 {filename} 到本地 {local_dir}")
    # 如果目录不存在则创建
    """
    只负责复制操作：将录制好的文件从设备拷贝到电脑，可选删除手机上的文件。
    :param device_id: adb devices 显示的设备序列号
    :param filename: 手机上的文件名（如 "抖音.mp4"）
    :param local_dir: 录制文件在电脑上的保存目录
    :param delete_remote: 是否在复制后删除手机上的文件
    """
    remote_path = f"/sdcard/{filename}"
    os.makedirs(local_dir, exist_ok=True)

    local_path = os.path.join(local_dir, f"{device_id}_{filename}")

    # 确保录制线程结束（防止边写边拉），如果你在外面已经 sleep 过，也可以删掉这几行
    t = record_threads.get(device_id)
    if t is not None:
        t.join()  # 等录制线程结束

    print(f"[{device_id}] 开始拷贝 {remote_path} 到本地 {local_path}")
    pull_cmd = ["adb", "-s", device_id, "pull", remote_path, local_path]
    result = subprocess.run(pull_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    if result.returncode == 0:
        print(f"[{device_id}] 录制文件已拷贝到: {local_path}")
    else:
        print(f"[{device_id}] 拷贝失败: {result.stderr}")
        return

    if delete_remote:
        rm_cmd = ["adb", "-s", device_id, "shell", "rm", remote_path]
        subprocess.run(rm_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"[{device_id}] 已删除手机上的文件: {remote_path}")


if __name__ == "__main__":
    import autotest.id_phone_relation as idphone   # 你的模块名就这样的话可以保留

    detected_devices = idphone.detect_short_video_apps()
    print("检测到的设备和应用信息：", detected_devices)

    duration = 10  # 所有设备统一录制 10 秒，如果要每个不同可以做一个 dict

    # 1）同时启动录制
    for app_key, dev in detected_devices.items():
        device_id = dev.get("id") or ""
        app_name = dev.get("appName") or app_key

        # 跳过没有设备 id 的项（比如你打印中 kuaishou 是空的）
        if not device_id:
            print(f"[{app_key}] 未检测到设备 id，跳过录制")
            continue

        start_record(device_id, f"{app_name}.mp4", duration)

    # 2）等待所有录制结束
    # 如果你希望简单粗暴一点，也可以直接 time.sleep(duration + 5)
    for device_id, t in record_threads.items():
        t.join()

    # 3）统一复制到电脑
    for app_key, dev in detected_devices.items():
        device_id = dev.get("id") or ""
        app_name = dev.get("appName") or app_key
        if not device_id:
            continue
        copy_record(device_id, f"{app_name}.mp4", local_dir="./records")

import subprocess
import json

# 目标 APP 包名列表
APP_PACKAGES = {
    "douyin": [  # 抖音
        "com.ss.android.ugc.aweme",
        "com.ss.android.ugc.aweme.lite",
    ],
    "kuaishou": [  # 快手
        "com.smile.gifmaker",
        "com.kuaishou.nebula",
    ],
    "xhs": [  # 小红书
        "com.xingin.xhs",
    ],
}


def _run_cmd(cmd):
    return subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True)


def _get_devices():
    """获取当前已连接设备 id 列表"""
    out = _run_cmd(["adb", "devices"])
    devices = []
    for line in out.splitlines():
        line = line.strip()
        if not line or line.startswith("List of devices"):
            continue
        parts = line.split()
        if len(parts) >= 2 and parts[1] == "device":
            devices.append(parts[0])
    return devices


def _get_installed_packages(device_id):
    """获取指定设备已安装包名集合"""
    out = _run_cmd(["adb", "-s", device_id, "shell", "pm", "list", "packages"])
    pkgs = set()
    for line in out.splitlines():
        line = line.strip()
        if line.startswith("package:"):
            pkgs.add(line[len("package:"):])
    return pkgs


def detect_short_video_apps():
    """
    检测当前通过 adb 连接的设备中：
      - 哪台装了 抖音 / 快手 / 小红书
    返回结构示例：
    {
      "douyin":   {"id": "deviceA", "path": "com.ss.android.ugc.aweme"},
      "kuaishou": {"id": "deviceB", "path": "com.smile.gifmaker"},
      "xhs":      {"id": "deviceC", "path": "com.xingin.xhs"}
    }
    如未检测到某个 app，则对应为 {"id": "", "path": ""}.
    """
    result = {
        "douyin":   {"id": "", "path": "", "appName": "抖音" },
        "kuaishou": {"id": "", "path": "", "appName": "快手" },
        "xhs":      {"id": "", "path": "", "appName": "小红书" },
    }

    devices = _get_devices()
    if not devices:
        return result  # 没设备直接返回空结构

    # 标记是否已经在某个设备上找到该 app（只记录第一次出现的设备）
    found = {key: False for key in APP_PACKAGES.keys()}

    for dev in devices:
        try:
            pkgs = _get_installed_packages(dev)
        except subprocess.CalledProcessError:
            continue

        for key, pkg_list in APP_PACKAGES.items():
            if found[key]:
                continue  # 已经找到过了，就不再覆盖
            for pkg in pkg_list:
                if pkg in pkgs:
                    result[key]["id"] = dev
                    result[key]["path"] = pkg
                    found[key] = True
                    break

    return result


if __name__ == "__main__":
    info = detect_short_video_apps()
    # 如需真正的 JSON 字符串：
    print(json.dumps(info, ensure_ascii=False, indent=2))

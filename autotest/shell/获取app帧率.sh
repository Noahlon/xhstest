#!/bin/bash
PKG=com.kuaishou.nebula
ACTIVITY=.homepage.HomeActivity   # 按你查到的实际类名替换

# 取 adb devices 的第一个设备（排除表头和空行）
DEVICE=$(adb devices | awk 'NR>1 && $2=="device" {print $1; exit}')

if [ -z "$DEVICE" ]; then
  echo "未检测到已连接的设备（adb devices 为空或无 device 状态）。"
  exit 1
fi

echo "当前使用设备: $DEVICE"

echo ">>> 清进程"
adb -s "$DEVICE" shell am force-stop "$PKG"

echo ">>> 启动 App"
adb -s "$DEVICE" shell am start-activity -W -n "$PKG/$ACTIVITY" > launch_time.txt &

# 等 500ms 让 App 开始渲染
sleep 0.5

echo ">>> 开始抓帧"
adb -s "$DEVICE" shell dumpsys gfxinfo "$PKG" framestats > gfx_framestats.txt

echo "✅ 完成，执行 python parse_gfx.py 分析"

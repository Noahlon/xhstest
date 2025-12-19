#!/bin/bash

echo "🔍 正在唤醒所有已连接的设备..."

for serial in $(adb devices | grep -w "device$" | awk '{print $1}'); do
    echo "⚡ 唤醒设备: $serial"
    adb -s "$serial" shell input keyevent 224
done

echo "✅ 所有设备唤醒命令已发送。"

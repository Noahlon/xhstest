#!/usr/bin/env bash

# 先杀掉已有进程
pkill -f appium
pkill -f weditor

# 参数说明：
# 不传参数或参数为 1 => 启动 weditor
# 参数为 2           => 启动 appium

if [ "$1" = "2" ]; then
    appium & >> ./log/appium.log
    echo "Appium started."
else
    # 默认或 1 都启动 weditor
    weditor & >> ./log/weditor.log
    echo "WEditor started."
fi

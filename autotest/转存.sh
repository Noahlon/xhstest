# !/bin/bash

filepath=$1

# 获取第二个参数
filename=${filepath##*/}


adb -s $device_id pull $filepath ./$filename.mp4


# 获取传入的参数
device_id=$1

# 获取第二个参数
filename=$2
# 录制时间
record_time=$3

filepath="/sdcard/$filename.mp4"

adb -s $device_id shell screenrecord $filepath --time-limit $record_time 

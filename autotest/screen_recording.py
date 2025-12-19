# coding: utf-8
#
import time
import uiautomator2 as u2

# 开始录制
def start_recording(d):
    d.swipe(0.9, 0.01,0.95, 0.95,0.5)  
    time.sleep(2)

    d.click(0.26, 0.755)
    time.sleep(2)

    d.click(0.576, 0.789)
    print("开始录制屏幕")

# 停止录制
def stop_recording(d):

    d.click(0.778, 0.792)
    time.sleep(1)
    d.click(0.778, 0.792)   
    print("停止录制屏幕")



if __name__ == "__main__":
    d = u2.connect()
    start_recording(d)
    time.sleep(10)  # 录制 10 秒
    stop_recording(d) 


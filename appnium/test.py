"""
open_douyin_fixed.py   —— 仅 30 行，真机即插即跑
Python 3.8+ | Appium Server ≥2.0 | pip install Appium-Python-Client
"""

from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ---------- 1. 填你自己的设备 ---------- 
UDID      = "8e576b56"          # ← adb devices 查到的 device-id
DEVICE_NM = "Xiaomi 14"         # ← 随意，但不要空


options = UiAutomator2Options().load_capabilities({
    "platformName": "Android",
    "appium:automationName": "UiAutomator2",
    "appium:deviceName": DEVICE_NM,
    "appium:udid": UDID,
    "appium:appPackage": "com.ss.android.ugc.aweme",
    "appium:appActivity": "com.ss.android.ugc.aweme.main.MainActivity",
    "appium:noReset": True,
    "appium:newCommandTimeout": 600,
    "appium:forceAppLaunch": True,   # 保证冷启
    "appium:shouldTerminateApp": True # 先杀旧进程
})

    
# ---------- 计时开始 ----------
driver = webdriver.Remote("http://localhost:4723", options=options)

# ---------- 明确等待「首页任意视频卡片」出现 ----------
# 抖音 27.9 主界面第一个视频 Item 的 resource-id（稳定）
t0 = time.time()          # Appium 开始连接
# 元素
VIDEO_ITEM_ID = "com.ss.android.ugc.aweme:id/qyl"   # 可用 Appium Inspector 核对
VIDEO_ITEM_ID2 = "com.ss.android.ugc.aweme:id/u80"  # 有时会变更为这个 ID

直播="com.ss.android.ugc.aweme:id/1_0"  # 直播卡片 ID
直播2="com.ss.android.ugc.aweme:id/dmh"
直播3="com.ss.android.ugc.aweme:id/j-r"
直播4="com.ss.android.ugc.aweme:id/kiv"
首页 = '//*[@resource-id="com.ss.android.ugc.aweme:id/root_view"]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.RelativeLayout[1]/android.widget.RelativeLayout[1]'
wait = WebDriverWait(driver, 30)                     # 最多给 30 s

try:
    wait.until(EC.presence_of_element_located(
        (AppiumBy.ID, VIDEO_ITEM_ID))) or wait.until(EC.presence_of_element_located(
        (AppiumBy.ID, VIDEO_ITEM_ID2)))
    t1 = time.time()
    delta_ms = (t1 - t0) * 1000
    print(f"✅ 抖音主界面已加载，总耗时：{delta_ms:.0f} ms")
except Exception as e:
    print("❌ 等待超时/元素变更：", e)
finally:
    print("测试结束，关闭 Appium Session")


# 下拉刷新
def swipe_up(driver=driver):
    for _ in range(3):
        driver.swipe(500, 1000, 500, 300, 800)

        print("下拉刷新一次")
        # 等待 2 秒再继续
        time.sleep(2) 
# 点击首页
def click_home(driver=driver):
    driver.find_element(AppiumBy.XPATH, 首页).click()
    print("点击首页")
    time.sleep(2)
swipe_up()
click_home()

driver.quit()
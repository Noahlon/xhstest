import time
import threading
import uiautomator2 as u2
import 屏幕录制 as sr
import id与手机的关系 as idphone


time_sleep = 5      # 等待时间
watch_time = 10     # 观看视频时间
# case 间隔时间
case_interval = 5
wait_time_pic = 20  # 上传图片等待时间
wait_time_video = 60 # 上传视频等待时间
# 搜索列表
search_list = ["日本", "上海"]

def run_test_on_device(device_id: str, test_app: str ,app_name: str, barrier: threading.Barrier):
    """
    在单台设备上执行完整测试流程的函数（给线程调用）
    :param device_id: adb 设备 id，比如 "10.23.170.154:43651" 或 "emulator-5554"
    :param test_app:  测试 app 包名，比如 "com.ss.android.ugc.aweme"
    """
    print(f"[{device_id}] 测试开始，app: {test_app}")

    # 每个线程里自己创建 uiautomator2 连接
    d = u2.connect(device_id)

    # 停止所有应用
    def stop_all_apps():
        time.sleep(2)
        d.app_stop_all()
        time.sleep(5)
    # 下面是原脚本中的函数，改成内部函数以使用 d 和 test_app
    def first_swipe():
        d.app_start(test_app)
        time.sleep(time_sleep)

    
    def cold_start():
        for i in range(3):
            if test_app == "com.xingin.xhs":
                d.swipe(0.5, 0.8, 0.5, 0.3, 0.1)
                d.swipe(0.5, 0.8, 0.5, 0.3, 0.1)

            d.swipe(0.5, 0.8, 0.5, 0.3, 0.2)
            print(f"[{device_id}] 冷启下拉刷新第{i+1}次")
            time.sleep(time_sleep)

    def click_home():
        d.click(0.117, 0.955)
        d.click(0.117, 0.955)
        time.sleep(time_sleep)

    def swipe_down():
        for i in range(3):
            d.swipe(0.5, 0.3, 0.5, 0.8, 0.2)
            print(f"[{device_id}] 首页上拉刷新第{i+1}次")
            time.sleep(time_sleep)
            d.click(0.658, 0.309)
            time.sleep(watch_time)
            d.swipe(0.02, 0.5, 0.98, 0.5, 0.2)
            time.sleep(1)

    def swipe_up():
        for i in range(3):
            d.swipe(0.5, 0.8, 0.2, 0.3, 0.1)
            d.swipe(0.5, 0.8, 0.2, 0.3, 0.1)
            time.sleep(time_sleep)
            d.click(0.658, 0.309)
            time.sleep(watch_time)
            d.swipe(0.02, 0.5, 0.98, 0.5, 0.2)
            time.sleep(1)
            print(f"[{device_id}] 首页下滑刷新第{i+1}次")
    # 视频内流
    def watch_video():
        print("视频内流1"+ test_app)
        d.click(0.658, 0.309)
        time.sleep(watch_time)
        print("视频内流2"+ test_app)
        d.swipe(0.5, 0.8, 0.5, 0.3, 0.2)
        time.sleep(watch_time)
        print("视频内流3"+ test_app)
        d.swipe(0.5, 0.8, 0.5, 0.3, 0.2)
        time.sleep(watch_time)
        d.swipe(0.02, 0.5, 0.98, 0.5, 0.2)
        time.sleep(1)


        
    def search():
        print("搜索视频1")
        d.click(0.906, 0.064)
        time.sleep(2)

        d.send_keys(search_list[0], clear=True)
        time.sleep(2)


        d.click(0.906, 0.064)
        time.sleep(time_sleep)
        # 如果是快手，需要多点一次视频
        if test_app == "com.smile.gifmaker":
            # d(text="视频").click()
            d.click(0.265, 0.121)
            time.sleep(3)
        d.click(0.658, 0.309)
        time.sleep(watch_time)
        d.swipe(0.02, 0.5, 0.98, 0.5, 0.2)
        time.sleep(1)
        d.click(0.5, 0.064)
        print("搜索视频2")
        d.send_keys(search_list[1], clear=True)
        time.sleep(2)
        d.click(0.906, 0.064)
        time.sleep(time_sleep)
        # 如果是快手，需要多点一次视频
        if test_app == "com.smile.gifmaker":
            # d(text="视频").click()
            d.click(0.39, 0.122)    
            time.sleep(3)

        d.click(0.658, 0.309)
        time.sleep(watch_time)
        d.swipe(0.02, 0.5, 0.98, 0.5, 0.2)
        time.sleep(1)
        d.swipe(0.02, 0.5, 0.98, 0.5, 0.2)
        time.sleep(1)
        d.swipe(0.02, 0.5, 0.98, 0.5, 0.2)
        time.sleep(1)
        if test_app == "com.smile.gifmaker":
            d.press("back")
            time.sleep(2)

    def personal_page():
        print("个人主页")
        d(text="我").click()
        time.sleep(time_sleep)
    # 上传图片
    def upload_pic():
        print("上传图片")
        # 这里添加上传逻辑
        d.click(0.494, 0.957)
        time.sleep(1)
        # 抖音逻辑
        if test_app == "com.ss.android.ugc.aweme":
            d.click(0.778, 0.849)
            time.sleep(1)
        elif test_app == "com.smile.gifmaker":   # 快手逻辑
            d(text="相册").click()
        elif test_app == "com.xingin.xhs":
            d(text="从相册选择").click()    # 小红书逻辑
        time.sleep(1)
        if test_app == "com.ss.android.ugc.aweme":
            d(text="图片").click()
        else:
            d(text="照片").click()
        time.sleep(1)
        time.sleep(1)
        d.swipe(0.5, 0.8, 0.5, 0.1, 0.2)
        time.sleep(3)
        d.click(0.533, 0.699)
        time.sleep(1)
        d(text="下一步").click()
        time.sleep(1)
        d(text="下一步").click()
        time.sleep(1)
        if test_app == "com.ss.android.ugc.aweme":
            d(text="发作品").click()
        elif test_app == "com.smile.gifmaker":
            d(text="发布").click()
        elif test_app == "com.xingin.xhs":
            d(text="发布笔记").click()
        time.sleep(wait_time_pic)
        d.press("back")
        time.sleep(2)
    # 上传视频
    def upload_video():
        print("上传视频")
        # 这里添加上传视频逻辑
        d.click(0.494, 0.957)
        time.sleep(1)
        
        # 抖音逻辑
        if test_app == "com.ss.android.ugc.aweme":
            d.click(0.778, 0.849)
            time.sleep(1)
        elif test_app == "com.smile.gifmaker":   # 快手逻辑
            d(text="相册").click()
        elif test_app == "com.xingin.xhs":
            d(text="从相册选择").click()    # 小红书逻辑
        # d(text="相册").click()
        time.sleep(1)
        d(text="视频").click()
        time.sleep(1)
        d.swipe(0.5, 0.8, 0.5, 0.1, 0.2)
        time.sleep(3)
        d.click(0.533, 0.699)
        time.sleep(1)
        d(text="下一步").click()
        time.sleep(1)
        d(text="下一步").click()
        time.sleep(1)
        if test_app == "com.ss.android.ugc.aweme":
            d(text="发作品").click()
        elif test_app == "com.smile.gifmaker":
            d(text="发布").click()
        elif test_app == "com.xingin.xhs":
            d(text="发布笔记").click()
        time.sleep(wait_time_video)
        d.press("back")
        time.sleep(2)
    """
    def start_test():
        time.sleep(3)
        sr.start_recording(d)
        time.sleep(3)  # 录制 10 秒
        first_swipe()
        cold_start()
        click_home()
        swipe_down()
        swipe_up()
        watch_video()
        search()
        personal_page()
        upload_pic()
        upload_video()
    """
    def start_test():
        # 运行case列表
        cases= [
            stop_all_apps,
            first_swipe,
            cold_start,
            click_home,
            swipe_down,
            swipe_up,
            watch_video,
            search,
            personal_page,
            upload_pic,
            upload_video,
        ]
        for case in cases:
            print(f"[{device_id} {app_name}] 准备运行 {case.__name__}")
            barrier.wait()  # 等待其他线程到达此点
            case()
            time.sleep(2)

    def end_test():
        sr.stop_recording(d)
        d.app_stop(test_app)
        print(f"[{device_id}] 测试结束，关闭应用")

    # 真正执行测试
    try:
        start_test()
    except Exception as e:
        print(f"[{device_id}] 测试过程中出错: {e}")
    finally:
        end_test()



def main():
   # 获取设备与 app 信息
    device_info = idphone.detect_short_video_apps()
    print("检测到的设备和应用信息：", device_info)

    tasks = []
    threads = []

    # 收集要测试的 (id, app_path)
    for device in device_info:
        if device_info[device]["id"] and device_info[device]["path"]:
            tasks.append((device_info[device]["id"], device_info[device]["path"], device_info[device]["appName"]))

    if not tasks:
        print("没有检测到可测试的设备与应用")
        return  


       # 所有设备共用一个 Barrier，用于步骤同步
    barrier = threading.Barrier(len(tasks))

    for device_id, app_path, app_name in tasks:
        t = threading.Thread(
            target=run_test_on_device,
            args=(device_id, app_path, app_name, barrier),  # 传 barrier 进去
            name=f"{app_path}-{device_id}",
            daemon=False
        )
        threads.append(t)
    # 启动所有线程
    for t in threads:
        t.start()

    # 等待所有线程结束
    for t in threads:
        t.join()

    print("所有设备测试完成。")


if __name__ == "__main__":
    main()

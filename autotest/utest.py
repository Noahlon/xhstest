import json
import time
import threading
import uiautomator2 as u2
import screen_recording as sr
import id_phone_relation as idphone
from logger import  RecordingLogger

time_sleep = 5      # 等待时间
watch_time = 10     # 观看视频时间
# case 间隔时间
case_interval = 5
wait_time_pic = 20  # 上传图片等待时间
wait_time_video = 60 # 上传视频等待时间
# 搜索列表
search_list = ["日本", "上海"]
# 录制时间
recording_duration = 60 * 7  # 录制时长，单位秒
# 当前场景变量
current_scene = "上海测试"


datas = []


class RecordingLogger:
    """
    录制日志类
    时间格式: MM:SS:FF (分:秒:帧)
    帧率: 30fps，帧范围 00-29
    示例: 03:02:22 表示 3分2秒22帧
    """
    
    def __init__(self, fps: int = 30):
        """
        初始化日志器
        :param fps: 帧率，默认30
        """
        self.fps = fps
        self._start_time = None
        self._lock = threading.Lock()
    
    def start(self):
        """开始计时"""
        with self._lock:
            self._start_time = time.time()
    
    def stop(self):
        """停止计时"""
        with self._lock:
            self._start_time = None
    
    def reset(self):
        """重置计时器"""
        self.stop()
    
    def get_time(self) -> str:
        """
        获取当前录制时间
        :return: 格式 MM:SS:FF
        """
        if self._start_time is None:
            return "00:00:00"
        
        elapsed = time.time() - self._start_time
        
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)
        frames = int((elapsed - int(elapsed)) * self.fps)
        frames = min(frames, self.fps - 1)  # 确保不超过最大帧
        
        return f"{minutes:02d}:{seconds:02d}:{frames:02d}"
    
    def get_elapsed_seconds(self) -> float:
        """获取经过的秒数"""
        if self._start_time is None:
            return 0.0
        return time.time() - self._start_time
    
    def log(self, message: str, device_id: str = "", app_name: str = ""):
        """
        打印日志
        :param message: 日志消息
        :param device_id: 设备ID（可选）
        :param app_name: 应用名称（可选）
        """
        with self._lock:
            time_str = self.get_time()
            
            if device_id and app_name:
                print(f"[{time_str}] [{device_id} {app_name}] {message}")
            elif device_id:
                print(f"[{time_str}] [{device_id}] {message}")
            else:
                print(f"[{time_str}] {message}")
        datas.append({
            "time": time_str,
            "device_id": device_id,
            "app_name": app_name,
            "message": message,
        })

def run_test_on_device(device_id: str, test_app: str ,app_name: str, barrier: threading.Barrier, logger: RecordingLogger):
    """
    在单台设备上执行完整测试流程的函数（给线程调用）
    :param device_id: adb 设备 id，比如 "10.23.170.154:43651" 或 "emulator-5554"
    :param test_app:  测试 app 包名，比如 "com.ss.android.ugc.aweme"
    """
    print(f"[{device_id}] 测试开始，app: {test_app}")

    # 每个线程里自己创建 uiautomator2 连接
    d = u2.connect(device_id)

    # 停止所有应用
    def init():
        logger.log(f"[{device_id} {app_name}] 初始化测试环境")
        time.sleep(2)
        d.app_stop_all()
        time.sleep(5)
    # 下面是原脚本中的函数，改成内部函数以使用 d 和 test_app
    def first_start():
        d.app_start(test_app)
        time.sleep(time_sleep)
    def play_current_video_or_note(test_app):
        clicked = False

        if test_app == "com.ss.android.ugc.aweme":  # 抖音
            element = d(resourceId="com.ss.android.ugc.aweme:id/c65")
            if element.exists:
                element[0].click()
                clicked = True

        elif test_app == "com.xingin.xhs":  # 小红书
            video_elements = d(descriptionStartsWith="视频")
            for item in video_elements:
                desc = item.info.get('contentDescription', '')
                if desc and desc != "视频" and len(desc) >= 4:
                    item.click()
                    clicked = True
                    break

        else:  # 其他 App，尝试点击固定坐标（可能是笔记封面）
            d.click(0.658, 0.309)
            clicked = True  # 假设这个点击总是有效

        if clicked:
            time.sleep(watch_time)
            return True
        else:
            return False

    
    def cold_start():  
        if test_app == "com.xingin.xhs":
            d.swipe(0.5, 0.8, 0.5, 0.3, 0.1)
            d.swipe(0.5, 0.8, 0.5, 0.3, 0.1)

        d.swipe(0.5, 0.8, 0.5, 0.3, 0.2)
        time.sleep(time_sleep)

    def click_home():
        # 如果是抖音，只点击一次
        if test_app == "com.ss.android.ugc.aweme":
            d.click(0.117, 0.955)
            time.sleep(time_sleep)
            return
        # 快手和小红书点击两次 
        d.click(0.117, 0.955)
        d.click(0.117, 0.955)
        time.sleep(time_sleep)

    def swipe_down():
        d.swipe(0.5, 0.3, 0.5, 0.8, 0.2)
        time.sleep(time_sleep)
        d.click(0.658, 0.309)
        time.sleep(watch_time)
        d.swipe(0.02, 0.5, 0.98, 0.5, 0.2)
        time.sleep(1)

    def swipe_up():
        d.swipe(0.5, 0.8, 0.2, 0.3, 0.1)
        time.sleep(time_sleep)
        d.click(0.658, 0.309)
        time.sleep(watch_time)
        d.swipe(0.02, 0.5, 0.98, 0.5, 0.2)
        time.sleep(1)
    # 视频内流
    def watch_video():
        # 抖音
        play_current_video_or_note(test_app)
        
        d.swipe(0.5, 0.8, 0.5, 0.3, 0.05)
        time.sleep(watch_time)
        d.swipe(0.5, 0.8, 0.5, 0.3, 0.05)
        time.sleep(watch_time)
        # 返回
        d.press("back")
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
    # 判断图片或视频是否上传成功
    def wait_for_publish_success(timeout=30, interval=0.1) -> bool:
        # 抖音
        text = "发布成功"
        if test_app == "com.ss.android.ugc.aweme":
            text = "发布成功"
        elif test_app == "com.xingin.xhs": # 小红书
            text = "发布成功！.."
        elif test_app == "com.smile.gifmaker": # 快手
            text = "作品发布成功，分享至"
        start = time.time()
        while time.time() - start < timeout:
            if d(text=text).exists(timeout=0):   # 立即判断
                print("✅ 发布成功")
                return True
            time.sleep(interval)
        print("❌ 发布失败（等待超时）")
        return False
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
        # 等待发布成功
        wait_for_publish_success(wait_time_pic)
        
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
        # 等待发布成功
        wait_for_publish_success(wait_time_video)
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
            first_start,
            # cold_start,
            # cold_start,
            # cold_start,
            # click_home,
            # swipe_down,
            # swipe_down,
            # swipe_down,
            # swipe_up,
            # swipe_up,
            # swipe_up,
            # watch_video,
            # watch_video,
            # watch_video,
            # search,
            # personal_page,
            # upload_pic,
            upload_video,
        ]
        init()
        time.sleep(3)
        barrier.wait()  # 等待其他线程准备好
        sr.start_recording(d)
        # sradb.start_record(device_id, f"{app_name}.mp4", 300)
        logger.start()
        
        time.sleep(3)  # 录制 10 秒
        for case in cases:
            logger.log(f"[{device_id} {app_name}] 准备运行 {case.__name__}")
            barrier.wait()  # 等待其他线程到达此点
            logger.log(f"[{device_id} {app_name}] 运行 {case.__name__} 开始")
            datas.append({
                "time": logger.get_time(),
                "case_name": case.__name__,
                "app_name": app_name,
                "type": "start"
            })
            try:
                case()
            except Exception as e:
                logger.log(f"[{device_id} {app_name}] 运行 {case.__name__} 出错: {e}")
            datas.append({
                "time": logger.get_time(),
                "case_name": case.__name__,
                "app_name": app_name,
                "type": "end"
            })
            time.sleep(2)
            logger.log(f"[{device_id} {app_name}] 运行 {case.__name__} 完成")

    def end_test():
        logger.stop()
        sr.stop_recording(d)
        # sradb.copy_record(device_id, f"{app_name}.mp4", local_dir=f"./records/{current_scene}")
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
    count = 0
    for device in device_info:
        if device_info[device]["id"] and device_info[device]["path"]:
            print(f"设备: {device}, ID: {device_info[device]['id']}, 应用: {device_info[device]['appName']}, 包名: {device_info[device]['path']}")
            count += 1
    # 测试的设备的数量
    print(f"测试的设备数量：{count} 个")

    # 初始化日志记录器
    logger = RecordingLogger(fps=30)

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
            args=(device_id, app_path, app_name, barrier, logger),  # 传 barrier 和 logger 进去
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
    
    # 打印JSON
    print(json.dumps(datas, indent=4, ensure_ascii=False))

    print("所有设备测试完成。")


if __name__ == "__main__":
    main()

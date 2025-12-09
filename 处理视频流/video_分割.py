#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
macOS: 在视频中查找「小图片」的所有出现（位置不固定，全帧匹配）
自动去重抖动，返回时间点列表（秒）
"""

import cv2
import numpy as np
import os

def imread_utf8(path):
    """兼容 macOS 中文路径"""
    if not os.path.exists(path):
        raise FileNotFoundError(f"❌ 文件不存在: {path}")
    img = cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError(f"❌ 图像解码失败: {path}")
    return img

def find_template_all(video_path, template_path, threshold=0.75, min_gap=1.0):
    """
    返回 template 在 video 中每次「独立出现」的时间（秒）
    min_gap: 两次「不同出现」的最小时间间隔（秒），避免同一画面多帧重复
    """
    # 读取模板（小图）
    tmpl_bgr = imread_utf8(template_path)
    tmpl_gray = cv2.cvtColor(tmpl_bgr, cv2.COLOR_BGR2GRAY)
    h, w = tmpl_gray.shape  # 小图的高、宽

    # 打开视频
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise FileNotFoundError(f"无法打开视频: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    min_gap_frames = int(min_gap * fps)  # 最少隔多少帧算「新一次」

    timestamps = []          # 存出现的时间（秒）
    last_match_frame = -9999 # 上一次匹配的帧号（初始化为很早）

    frame_idx = 0
    print(f"🎞 视频: {os.path.basename(video_path)}")
    print(f"🧩 模板尺寸: {w}x{h}  阈值: {threshold}  最小间隔: {min_gap}s")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # 在当前帧的「全图」上滑窗匹配小模板
        res = cv2.matchTemplate(gray_frame, tmpl_gray, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(res)   # 只关心最大值

        if max_val >= threshold:
            # 如果距离上一次匹配帧 >= min_gap_frames，就算一次「新出现」
            if frame_idx - last_match_frame >= min_gap_frames:
                time_sec = frame_idx / fps
                timestamps.append(round(time_sec, 2))
                last_match_frame = frame_idx
                print(f"  ✅ {time_sec:6.2f}s  score={max_val:.3f}  loc={max_loc}")

        frame_idx += 1

    cap.release()
    return timestamps

# ============== 你只需要改这里！ ==============
if __name__ == "__main__":
    # 👇 改成你自己的绝对路径（macOS 格式）
    VIDEO_PATH      = "test.mp4"          # 例: /Users/jack/Movies/sample.mp4
    TEMPLATE_PATH   = "图片样本/首刷开始.png"              # 你的「小图片」路径

    THRESHOLD = 0.75   # 相似度阈值 (0~1)，可下调到 0.7 试试
    MIN_GAP   = 1.0    # 秒，同一画面防抖间隔

    # 展开 ~
    VIDEO_PATH    = os.path.expanduser(VIDEO_PATH)
    TEMPLATE_PATH = os.path.expanduser(TEMPLATE_PATH)

    # 检查文件
    if not os.path.exists(VIDEO_PATH):
        print("❌ 视频文件不存在:", VIDEO_PATH)
        exit(1)
    if not os.path.exists(TEMPLATE_PATH):
        print("❌ 模板文件不存在:", TEMPLATE_PATH)
        exit(1)

    # 开始查找
    times = find_template_all(VIDEO_PATH, TEMPLATE_PATH, THRESHOLD, MIN_GAP)

    # 输出结果
    print("\n🎉 匹配到的时间点（秒）:")
    if times:
        for i, t in enumerate(times, 1):
            print(f"{i:2d}. {t:6.2f}s")
    else:
        print("（无）未找到匹配")

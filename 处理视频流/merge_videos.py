#!/usr/bin/env python3
"""
merge_videos.py
三竖屏视频，高1080，水平排列，中间等宽间隙，间隙色=rgb(191,226,233)，输出1920x1080
"""

import subprocess
from pathlib import Path
import json

OUT_W, OUT_H = 1920, 1080
GAP_COLOR = "0xBFE2E9"  # rgb(191,226,233)

def get_video_size(path: str) -> tuple:
    """返回 (width, height)"""
    cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height",
        "-of", "json",
        path
    ]
    info = json.loads(subprocess.run(cmd, capture_output=True, text=True, check=True).stdout)
    w = info['streams'][0]['width']
    h = info['streams'][0]['height']
    return w, h

def to_seconds(ts: str) -> float:
    h, m, s = ts.split(":")
    s, ms = (s.split(".") + ["0"])[:2]
    s = s.split('.')[0]  # 去掉可能的亚秒
    return int(h)*3600 + int(m)*60 + int(s) + float('0.' + ms.ljust(3,'0')[:3])*1

def merge_videos(
    input1, start1, end1,
    input2, start2, end2,
    input3, start3, end3,
    output,
    max_duration=None
):
    for p in [input1, input2, input3]:
        if not Path(p).is_file():
            raise FileNotFoundError(f"文件不存在: {p}")

    Path(output).parent.mkdir(parents=True, exist_ok=True)

    # 计算各视频缩放后宽度
    def scaled_w(path):
        w, h = get_video_size(path)
        new_w = int(w * OUT_H / h)
        new_w += new_w % 2  # 偶数
        return new_w


    # start增加 提前1秒，end延时1秒
    def adjust_time(ts, delta):
        total_sec = to_seconds(ts) + delta
        if total_sec < 0:
            total_sec = 0
        h = int(total_sec // 3600)
        m = int((total_sec % 3600) // 60)
        s = total_sec % 60
        ms = int((s - int(s)) * 1000)
        s = int(s)
        return f"{h:02}:{m:02}:{s:02}.{ms:03}" 
    start1 = adjust_time(start1, -1)
    end1 = adjust_time(end1, 1)
    start2 = adjust_time(start2, -1)
    end2 = adjust_time(end2, 1)
    start3 = adjust_time(start3, -1)
    end3 = adjust_time(end3, 1)

    w1 = scaled_w(input1)
    w2 = scaled_w(input2)
    w3 = scaled_w(input3)
    total_w = w1 + w2 + w3

    if total_w > OUT_W:
        raise ValueError(f"三视频总宽 {total_w} > {OUT_W}，无法加间隙")

    gap = (OUT_W - total_w) // 2
    gap = gap if gap % 2 == 0 else gap + 1

    # x 坐标
    x1 = 0
    x2 = w1 + gap
    x3 = x2 + w2 + gap

    print(f"缩放后宽: {w1},{w2},{w3} | 间隙: {gap}px | 位置: {x1},{x2},{x3}")

    d1 = to_seconds(end1) - to_seconds(start1)
    d2 = to_seconds(end2) - to_seconds(start2)
    d3 = to_seconds(end3) - to_seconds(start3)
    if max_duration is None:
        max_duration = max(d1, d2, d3)

    filter_complex = (
        f"color=c={GAP_COLOR}:s={OUT_W}x{OUT_H},fps=30[bg];"
        f"[0:v]scale={w1}:{OUT_H}:force_original_aspect_ratio=disable,setsar=1[v0];"
        f"[1:v]scale={w2}:{OUT_H}:force_original_aspect_ratio=disable,setsar=1[v1];"
        f"[2:v]scale={w3}:{OUT_H}:force_original_aspect_ratio=disable,setsar=1[v2];"
        f"[bg][v0]overlay=x={x1}:y=0[bg1];"
        f"[bg1][v1]overlay=x={x2}:y=0[bg2];"
        f"[bg2][v2]overlay=x={x3}:y=0[outv]"
    )

    cmd = [
        "ffmpeg", "-y",
        "-ss", start1, "-to", end1, "-i", input1,
        "-ss", start2, "-to", end2, "-i", input2,
        "-ss", start3, "-to", end3, "-i", input3,
        "-filter_complex", filter_complex,
        "-map", "[outv]",
        "-t", str(max_duration),
        "-c:v", "libx264", "-crf", "23", "-preset", "fast",
        "-fflags", "+genpts",
        output
    ]
    # 打印完整命令行供调试
    print("完整命令行:", " ".join(cmd))
    subprocess.run(cmd, check=True)

    
    return output

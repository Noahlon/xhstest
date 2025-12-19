# parse_gfx.py
import re

with open("gfx.txt") as f:
    data = f.read()

# 提取所有 Vsync 时间戳（纳秒）
matches = re.findall(r'^\d+,(\d+),', data, re.MULTILINE)
times = [int(x) for x in matches if x.strip()]

# 换成毫秒
times_ms = [t / 1_000_000 for t in times]

# 计算帧间隔
intervals = [j - i for i, j in zip(times_ms, times_ms[1:])]

# 过滤异常值（>30ms 或 <5ms）
valid = [i for i in intervals if 5 <= i <= 30]

if valid:
    avg_fps = 1000 / (sum(valid) / len(valid))
    print(f"平均 FPS: {avg_fps:.1f}，总帧数: {len(times)}")
else:
    print("没抓到有效帧")

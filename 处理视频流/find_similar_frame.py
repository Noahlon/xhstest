import cv2
from skimage.metrics import structural_similarity as ssim
import numpy as np
import os

def find_most_similar_frame(video_path, target_img_path, output_path="best_match.jpg"):
    # 读取目标图像（灰度）
    target_img = cv2.imread(target_img_path)
    if target_img is None:
        print(f"❌ 无法读取目标图像: {target_img_path}")
        return

    target_gray = cv2.cvtColor(target_img, cv2.COLOR_BGR2GRAY)
    target_resized = None  # 用于尺寸对齐

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"❌ 无法打开视频: {video_path}")
        return

    best_score = -1
    best_frame = None
    best_frame_index = -1
    frame_count = 0

    print("🔍 正在逐帧比对视频...")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # 转为灰度
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # 如果目标图和当前帧尺寸不同，resize 到相同（以目标图为基准）
        if target_resized is None:
            # 以目标图尺寸为准，统一尺寸
            h, w = target_gray.shape
            gray_frame = cv2.resize(gray_frame, (w, h))

        # 计算 SSIM 相似度（值越接近1越相似）
        try:
            score, _ = ssim(target_gray, gray_frame, full=True)
        except ValueError:
            # 尺寸不一致时报错，强制 resize
            h, w = target_gray.shape
            resized = cv2.resize(gray_frame, (w, h))
            score, _ = ssim(target_gray, resized, full=True)

        if score > best_score:
            best_score = score
            best_frame = frame.copy()
            best_frame_index = frame_count

        frame_count += 1

        # 可选：显示进度
        if frame_count % 100 == 0:
            print(f"  已处理 {frame_count} 帧...")

    cap.release()

    if best_frame is not None:
        cv2.imwrite(output_path, best_frame)
        print(f"\n✅ 找到最匹配帧！")
        print(f"📸 帧序号: {best_frame_index}")
        print(f"🎯 相似度 (SSIM): {best_score:.4f}")
        print(f"🖼️ 已保存为: {os.path.abspath(output_path)}")
    else:
        print("❌ 未找到有效匹配帧。")

# ========================
# 👇 使用示例
# ========================
if __name__ == "__main__":
    # 请替换为你的文件路径
    TARGET_IMAGE = "target.jpg"      # 你要匹配的图
    VIDEO_FILE = "video.mp4"         # 要搜索的视频
    OUTPUT_IMAGE = "best_match.jpg"  # 输出结果

    # 检查文件是否存在
    if not os.path.exists(TARGET_IMAGE):
        print(f"❌ 目标图像不存在: {TARGET_IMAGE}")
    elif not os.path.exists(VIDEO_FILE):
        print(f"❌ 视频文件不存在: {VIDEO_FILE}")
    else:
        find_most_similar_frame(VIDEO_FILE, TARGET_IMAGE, OUTPUT_IMAGE)

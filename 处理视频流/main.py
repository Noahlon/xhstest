#!/usr/bin/env python3
"""
FastAPI 接口：
POST /merge
{
  "input1": "/abs/a.mp4", "start1": "00:00:11.733", "end1": "00:00:43.733",
  "input2": "...", "start2": "...", "end2": "...",
  "input3": "...", "start3": "...", "end3": "...",
  "output": "/tmp/results/final.mp4",          # 可选，默认 ./output.mp4
  "max_duration": 35.5                         # 可选，秒
}
返回:
{
  "status": "ok",
  "output_path": "/tmp/results/final.mp4",
  "download_url": "http://127.0.0.1:8000/files/final.mp4"
}

支持：CORS 跨域访问
"""

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from merge_videos import merge_videos  # 假设你已有这个函数

app = FastAPI(title="Video Merge Service")

# ---------- CORS 跨域配置 ----------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境建议改成具体域名，如 ["https://your-frontend.com"]
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有 HTTP 方法（GET, POST, OPTIONS 等）
    allow_headers=["*"],  # 允许所有请求头
)

# ---------- 请求体 ----------
class MergeRequest(BaseModel):
    input1: str
    start1: str
    end1: str
    input2: str
    start2: str
    end2: str
    input3: str
    start3: str
    end3: str
    output: str = "./output.mp4"          # 默认输出路径
    max_duration: float | None = None

# ---------- 合并接口 ----------
@app.post("/merge")
def do_merge(req: MergeRequest):
    # 打印请求参数
    print(req.model_dump())
    try:
        real_path = merge_videos(
            req.input1, req.start1, req.end1,
            req.input2, req.start2, req.end2,
            req.input3, req.start3, req.end3,
            req.output,
            req.max_duration
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"合成失败: {e}")

    # 返回供下载的 URL（相对路径）
    filename = os.path.basename(real_path)
    download_url = f"/files/{urllib.parse.quote(filename)}"  # URL 编码文件名，防止中文或空格问题

    return {
        "status": "ok",
        "output_path": real_path,
        "download_url": download_url
    }

# ---------- 静态文件下载 ----------
from fastapi.staticfiles import StaticFiles
import urllib.parse  # 确保导入

# 挂载静态目录，用于下载生成的视频文件
app.mount("/files", StaticFiles(directory="."), name="files")  # 当前目录

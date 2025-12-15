import os
import urllib.parse
from pydantic import BaseModel
from merge_videos import merge_videos  # 复用你已有的函数

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
    output: str = "./output.mp4"
    max_duration: float | None = None


def merge_videos_handler(req_data: dict | MergeRequest) -> dict:
    """
    功能等价于原来的 FastAPI POST /merge 接口逻辑。

    参数:
        req_data: 可以是 dict（与原来接口 JSON 一致），也可以是 MergeRequest 实例

    返回:
        {
          "status": "ok",
          "output_path": "...",
          "download_url": "/files/xxx.mp4"
        }
        出错会抛出异常（由调用方决定如何处理）
    """
    # 如果传入的是 dict，则先用 Pydantic 校验并转成对象
    if isinstance(req_data, dict):
        req = MergeRequest(**req_data)
    else:
        req = req_data  # 已是 MergeRequest

    # 打印请求参数，便于调试
    print(req.model_dump())

    # 调用原有的 merge_videos 函数
    real_path = merge_videos(
        req.input1, req.start1, req.end1,
        req.input2, req.start2, req.end2,
        req.input3, req.start3, req.end3,
        req.output,
        req.max_duration
    )

    # 生成下载 URL（与 FastAPI 接口保持一致）
    filename = os.path.basename(real_path)
    download_url = f"/files/{urllib.parse.quote(filename)}"

    return {
        "status": "ok",
        "output_path": real_path,
        "download_url": download_url
    }

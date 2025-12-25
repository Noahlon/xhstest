#!/usr/bin/env python3
"""
macOS / Linux 环境变量：
export KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
export MODEL="gpt-3.5-turbo"
export BASE_URL="https://api.openai.com/v1"
"""

import os
from openai import OpenAI

# ---------- 工具 ----------
def _getenv_or_raise(name: str) -> str:
    v = os.getenv(name)
    if not v:
        raise RuntimeError(f"环境变量 {name} 未设置")
    return v.rstrip("/")          # 去掉可能误加的尾部斜杠


# ---------- 主逻辑 ----------
def chat_once(prompt: str = "Hi") -> str:
    api_key  = _getenv_or_raise("KEY")
    model    = _getenv_or_raise("MODEL")
    base_url = _getenv_or_raise("BASE_URL")
    # 打印调试信息
    print(f"Using model={model}, base_url={base_url}")

    client = OpenAI(api_key=api_key, base_url=base_url, timeout=30.0)

    rsp = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=64,
    )
    return rsp.choices[0].message.content


# ---------- 测试入口 ----------
def main():
    try:
        answer = chat_once("你好，介绍一下你自己。")
        print(">>>", answer)
    except Exception as e:
        print("ERROR:", e)


if __name__ == "__main__":
    main()

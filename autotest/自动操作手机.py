import uiautomator2 as u2
import traceback
import textwrap
import os
import time
import re

# 假设 config.py 中包含这些配置
# 如果没有 config.py，请手动在这里替换为实际值
from config import client, KIMI_MODEL, SYSTEM_PROMPT, ERROR_ANALYSIS_PROMPT

# ============ 工具函数：清洗代码字符串 ============
def clean_llm_code(text: str) -> str:
    # 1. 移除 DeepSeek R1 可能产生的 <think> 标签
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    
    # 2. 尝试提取 ```python 代码块
    pattern = r"```(?:python)?(.*?)```"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    
    # 3. 如果没有代码块，尝试移除行首的 "Here is..." 等废话
    # 简单策略：找到第一个 import 或 d( 或 d. 出现的位置
    lines = text.split('\n')
    valid_lines = []
    started = False
    for line in lines:
        stripped = line.strip()
        # 只要行首看起来像代码，就开始保留
        if (stripped.startswith('import ') or 
            stripped.startswith('d.') or 
            stripped.startswith('d(') or 
            stripped.startswith('if ') or 
            stripped.startswith('try:') or
            stripped.startswith('#')):
            started = True
        
        if started:
            valid_lines.append(line)
    
    if valid_lines:
        return '\n'.join(valid_lines).strip()
    
    return text.strip()

# ============ 1. 错误分析与修复 ============
def analyze_error_with_llm(user_instruction: str, code: str, error_trace: str) -> str:
    """
    将用户指令 + 原始代码 + 异常信息发送给大模型，请其返回“修正后的代码”。
    """
    print(">>> 正在请求 AI 修复代码...")
    content = (
        f"用户的原始需求如下：\n"
        f"{user_instruction}\n\n"
        f"你之前生成的 Python 代码如下：\n"
        f"{code}\n\n"
        f"执行这段代码时出现的异常信息如下（Python traceback）：\n"
        f"{error_trace}\n\n"
        f"请根据以上信息，分析错误原因，并返回一段修正后的完整 Python 代码。"
        f"不要解释原因，直接返回代码。"
    )

    try:
        resp = client.chat.completions.create(
            model=KIMI_MODEL,
            messages=[
                {"role": "system", "content": ERROR_ANALYSIS_PROMPT},
                {"role": "user", "content": content},
            ],
            temperature=0.1,
            max_tokens=1024, # 稍微调大一点，防止代码截断
        )
        new_code = resp.choices[0].message.content or ""
        return clean_llm_code(new_code)
    except Exception as e:
        print(f"请求修复代码时发生错误: {e}")
        return ""

# ============ 2. 连接手机 ============
def connect_device(device_id=None):
    """
    device_id 为空时，自动连接第一个设备或 WiFi 设备。
    """
    try:
        if device_id:
            d = u2.connect(device_id)
        else:
            d = u2.connect()
        print(f"已连接设备：{d.device_info.get('serial', 'Unknown')}")
        # 唤醒屏幕并解锁（可选）
        d.screen_on()
        return d
    except Exception as e:
        print(f"连接设备失败: {e}")
        return None

# ============ 3. 调用 Kimi 生成代码 ============
def generate_code_from_nl(instruction: str) -> str:
    """
    用自然语言描述手机操作，返回一段 Python 代码（字符串）
    """
    print(">>> 正在生成操作代码...")
    try:
        resp = client.chat.completions.create(
            model=KIMI_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": instruction},
            ],
            temperature=0.1,
            max_tokens=1024,
        )
        code = resp.choices[0].message.content
        return clean_llm_code(code)
    except Exception as e:
        print(f"生成代码请求失败: {e}")
        return ""

# ============ 4. 执行生成的代码（带重试机制） ============
def exec_generated_code(d, code: str, user_instruction: str, max_retries=3):
    """
    在已经连接好的 device d 上执行生成的 Python 代码。
    如果报错，自动调用 analyze_error_with_llm 进行修复并重试。
    """
    # 可以在这里预置 import，防止模型忘记写
    pre_imports = "import time\nimport uiautomator2 as u2\n"
    
    # 只要代码里没有 import time，就加进去（简单判断）
    if "import time" not in code:
        code = pre_imports + code

    # 执行环境
    global_env = {
        "d": d, 
        "u2": u2, 
        "time": time, 
        "os": os
    }
    local_env = {}

    current_code = code
    attempt = 0

    while attempt <= max_retries:
        print(f"\n====== 执行代码 (尝试次数: {attempt + 1}) ======\n")
        print(textwrap.indent(current_code, "    "))
        print("\n============================================\n")

        try:
            # 这里的 exec 会直接在当前进程执行代码
            exec(current_code, global_env, local_env)
            print(">>> 代码执行成功！")
            return # 执行成功，退出函数

        except Exception:
            print("!!! 执行代码时出现异常 !!!")
            error_trace = traceback.format_exc()
            print(error_trace)

            attempt += 1
            if attempt > max_retries:
                print(f">>> 已达到最大重试次数 ({max_retries})，停止重试。")
                break
            
            # 调用 LLM 进行修复
            fixed_code = analyze_error_with_llm(user_instruction, current_code, error_trace)
            
            if not fixed_code:
                print(">>> AI 未能返回修复后的代码，终止执行。")
                break
            
            # 更新代码，准备下一次循环执行
            current_code = fixed_code
            # 再次检查 import time
            if "import time" not in current_code:
                current_code = pre_imports + current_code

# ============ 5. 交互主循环 ============
def main():
    d = connect_device() 
    if not d:
        print("未找到设备，请检查 USB 连接或 adb devices。")
        return

    while True:
        try:
            user_input = input("\n请输入要让手机执行的操作（输入 exit 退出）：\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit", "q"):
            break

        # 1) 调大模型生成代码
        code = generate_code_from_nl(user_input)
        
        if not code:
            print("生成代码为空，请重试。")
            continue

        # 2) 执行生成的代码（包含错误自动修复逻辑）
        exec_generated_code(d, code, user_input, max_retries=2)

    print("已退出。")

if __name__ == "__main__":
    main()

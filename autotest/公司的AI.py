import requests
import json

# 通用配置
base_headers = {
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'content-type': 'application/json',
    'origin': 'https://ai.devops.xiaohongshu.com',
    'priority': 'u=1, i',
    'qstoken': 'AITf6fa1944d61666fe37a5c6e3b9dc8f6c', # 敏感信息
    'sec-ch-ua': '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
    # Cookie 非常长，这里直接作为字符串放入 Header
    'Cookie': 'a1=199d1630a368cdlie4j1n82of6dmefdviwpw1x16130000409865; webId=68d366ea1f253dd1d267c8705dcf7a5d; gid=yjjfyKqJd43fyjjfyKq80ECyqKYSf13d4VyIUKyYJliKfEq86difhy88848jYK28i4ydS0J8; porch_beaker_session_id=ff55bf3144ba60719db7898743e08beb4712be5fgAJ9cQAoWAMAAABfaWRxAVggAAAAMGZlNThjODg1MzBlNDU2NTg2MmFiZmM2ZjU0YjY2YmJxAlgOAAAAX2FjY2Vzc2VkX3RpbWVxA0rg0+loWAoAAABleHBpcmVkX2F0cQRK4HpgaVgNAAAAcG9yY2gtdXNlci1pZHEFWBgAAAA2OGU5YmEwNjI3OTMwMDAwMDAwMDAwMDBxBlgQAAAAcG9yY2gtYXV0aC10b2tlbnEHWEEAAABmZjkwNTlkNGUxZDc0ZGVhYjNhZGY1YzU2ZDc4MmI3MS1lNTA0ZTcxMDlhZjFjMWQ5NmJlMjM4MTc2MDE0OTAyNnEIWA4AAABfY3JlYXRpb25fdGltZXEJSuDT6Wh1Lg==; e-sso-user-id=68e9ba062793000000000000; _porch_uuid=172069826424847; access-token-docs.xiaohongshu.com=internal.docs.AT-81b93aa1baf34358a99e440c252ba9d3-ec8b7037b1168d947bc48a1760156767; access-token-city.xiaohongshu.com=internal.xhsoa.AT-31d51d3ca19c49e3b685736913db5ead-eb87c1983e67b236df35e61760407873; common-internal-access-token-prod=AT-31d51d3ca19c49e3b685736913db5ead-eb87c1983e67b236df35e61760407873; abRequestId=68d366ea1f253dd1d267c8705dcf7a5d; portal-guide=done; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%2210000062515%22%2C%22%24device_id%22%3A%2219a478afbe4b37-04323a389baa13-1d525631-1484784-19a478afbe52f3c%22%2C%22props%22%3A%7B%7D%2C%22first_id%22%3A%2219a478afbe4b37-04323a389baa13-1d525631-1484784-19a478afbe52f3c%22%7D; web_session=040069b6f3ed4471b9f21b163c3b4b78ca9a16; xsecappid=xhs-pc-web; webBuild=5.0.6; loadts=1765791470765; websectiga=29098a4cf41f76ee3f8db19051aaa60c0fc7c5e305572fec762da32d457d76ae; unread={%22ub%22:%22693bdc77000000001f00eea0%22%2C%22ue%22:%22693aa1c2000000001e00fe5a%22%2C%22uc%22:25}; acw_tc=0a42198d17659632967015638e43d7079aa3b7887e105ca1161857f8b88466'
}

# ==========================================
# 请求 1: 初始化/发送用户消息
# API: /api/chatbot/v1/message/chat
# ==========================================
url_msg_chat = 'https://ai.devops.xiaohongshu.com/api/chatbot/v1/message/chat'
headers_1 = base_headers.copy()
headers_1['accept'] = 'application/json'

payload_1 = {
    "father_uuid": None,
    "conversation_uuid": None,
    "bot": "Gemini-3-Pro-preview-Gemini-3-Pro-preview",
    "chat_info": {
        "role": "user",
        "content": [
            {
                "content_type": "text",
                "content_detail": "中国科技大学怎么样",
                "content_meta": {}
            }
        ]
    }
}

print("--- 发送请求 1: 初始化消息 ---")
try:
    response_1 = requests.post(url_msg_chat, headers=headers_1, json=payload_1)
    print(f"状态码: {response_1.status_code}")
    print(f"响应: {response_1.text[:200]}...") # 只打印前200字符
except Exception as e:
    print(f"请求 1 失败: {e}")


# ==========================================
# 请求 2: 获取 LLM 回复 (流式)
# API: /api/chatbot/v1/chat/completions
# ==========================================
url_completions = 'https://ai.devops.xiaohongshu.com/api/chatbot/v1/chat/completions'
headers_2 = base_headers.copy()
headers_2['accept'] = 'text/event-stream'  # 注意这里接受流

payload_2 = {
    "query": "中国科技大学怎么样",
    "bot": "Gemini-3-Pro-preview-Gemini-3-Pro-preview",
    "history": [
        {
            "role": "user",
            "content": [
                {
                    "text": "中国科技大学怎么样"
                }
            ]
        }
    ],
    "generation_kwargs": {
        "stream": True
    },
    "websearch": [],
    "thinking": True
}

print("\n--- 发送请求 2: 获取生成回复 (Stream) ---")
try:
    # stream=True 允许我们处理长连接响应
    response_2 = requests.post(url_completions, headers=headers_2, json=payload_2, stream=True)
    print(f"状态码: {response_2.status_code}")
    
    # 简单读取流数据（实际场景可能需要解析 SSE 格式）
    # 这里只读取前几行演示连接成功
    for i, line in enumerate(response_2.iter_lines()):
        if i > 5: break 
        if line:
            print(f"Stream Line: {line.decode('utf-8')}")
except Exception as e:
    print(f"请求 2 失败: {e}")


# ==========================================
# 请求 3: 保存助手(AI)的回复
# API: /api/chatbot/v1/message/chat
# ==========================================
# 注意：payload_3 非常大，通常包含从请求 2 中获取的完整生成内容
# 为了代码整洁，这里省略了具体的 thoughtSignature 乱码内容，
# 实际运行时请确保 payload 完整性，或者动态填入请求 2 的结果。

print("\n--- 发送请求 3: 保存 AI 回复 ---")
headers_3 = base_headers.copy()
headers_3['accept'] = 'application/json'

# 这里的 content 和 meta 数据非常长，直接使用 CURL 中的结构
payload_3 = {
    "father_uuid": "4d972567-8e09-455d-9f31-c2d08949e226", # 这些 UUID 通常是动态生成的
    "conversation_uuid": "2cd1261c-5003-479f-8184-45cf29c1e70d",
    "bot": "Gemini-3-Pro-preview-Gemini-3-Pro-preview",
    "chat_info": {
        "role": "assistant",
        "meta": {
            "model": "gemini-3-pro-preview",
            "msg_id": "QndCae3nKMndjMwPr5ThwAg",
            "usage": {
                "promptTokenCount": 4,
                "candidatesTokenCount": 1096,
                "totalTokenCount": 2405,
                "trafficType": "ON_DEMAND",
                "promptTokensDetails": [{"modality": "TEXT", "tokenCount": 4}],
                "candidatesTokensDetails": [{"modality": "TEXT", "tokenCount": 1096}],
                "thoughtsTokenCount": 1305
            },
            "index": 0,
            "completion_start_time": "2025-12-17T17:26:30.372320",
            "thoughtSignature": "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"
        }
    }
}
# 请求 1: 初始化/发送用户消息
# API: /api/chatbot/v1/message/chat
# ==========================================
url_msg_chat = 'https://ai.devops.xiaohongshu.com/api/chatbot/v1/message/chat'
headers_1 = base_headers.copy()
headers_1['accept'] = 'application/json'

payload_1 = {
    "father_uuid": None,
    "conversation_uuid": None,
    "bot": "Gemini-3-Pro-preview-Gemini-3-Pro-preview",
    "chat_info": {
        "role": "user",
        "content": [
            {
                "content_type": "text",
                "content_detail": "中国科技大学怎么样",
                "content_meta": {}
            }
        ]
    }
}

print("--- 发送请求 1: 初始化消息 ---")
try:
    response_1 = requests.post(url_msg_chat, headers=headers_1, json=payload_1)
    print(f"状态码: {response_1.status_code}")
    print(f"响应: {response_1.text[:200]}...") # 只打印前200字符
except Exception as e:
    print(f"请求 1 失败: {e}")


# ==========================================
# 请求 2: 获取 LLM 回复 (流式)
# API: /api/chatbot/v1/chat/completions
# ==========================================
url_completions = 'https://ai.devops.xiaohongshu.com/api/chatbot/v1/chat/completions'
headers_2 = base_headers.copy()
headers_2['accept'] = 'text/event-stream'  # 注意这里接受流

payload_2 = {
    "query": "中国科技大学怎么样",
    "bot": "Gemini-3-Pro-preview-Gemini-3-Pro-preview",
    "history": [
        {
            "role": "user",
            "content": [
                {
                    "text": "中国科技大学怎么样"
                }
            ]
        }
    ],
    "generation_kwargs": {
        "stream": True
    },
    "websearch": [],
    "thinking": True
}

print("\n--- 发送请求 2: 获取生成回复 (Stream) ---")
try:
    # stream=True 允许我们处理长连接响应
    response_2 = requests.post(url_completions, headers=headers_2, json=payload_2, stream=True)
    print(f"状态码: {response_2.status_code}")
    
    # 简单读取流数据（实际场景可能需要解析 SSE 格式）
    # 这里只读取前几行演示连接成功
    for i, line in enumerate(response_2.iter_lines()):
        if i > 5: break 
        if line:
            print(f"Stream Line: {line.decode('utf-8')}")
except Exception as e:
    print(f"请求 2 失败: {e}")


# ==========================================
# 请求 3: 保存助手(AI)的回复
# API: /api/chatbot/v1/message/chat
# ==========================================
# 注意：payload_3 非常大，通常包含从请求 2 中获取的完整生成内容
# 为了代码整洁，这里省略了具体的 thoughtSignature 乱码内容，
# 实际运行时请确保 payload 完整性，或者动态填入请求 2 的结果。

print("\n--- 发送请求 3: 保存 AI 回复 ---")
headers_3 = base_headers.copy()
headers_3['accept'] = 'application/json'

# 这里的 content 和 meta 数据非常长，直接使用 CURL 中的结构
payload_3 = {
    "father_uuid": "4d972567-8e09-455d-9f31-c2d08949e226", # 这些 UUID 通常是动态生成的
    "conversation_uuid": "2cd1261c-5003-479f-8184-45cf29c1e70d",
    "bot": "Gemini-3-Pro-preview-Gemini-3-Pro-preview",
    "chat_info": {
        "role": "assistant",
        "meta": {
            "model": "gemini-3-pro-preview",
            "msg_id": "QndCae3nKMndjMwPr5ThwAg",
            "usage": {
                "promptTokenCount": 4,
                "candidatesTokenCount": 1096,
                "totalTokenCount": 2405,
                "trafficType": "ON_DEMAND",
                "promptTokensDetails": [{"modality": "TEXT", "tokenCount": 4}],
                "candidatesTokensDetails": [{"modality": "TEXT", "tokenCount": 1096}],
                "thoughtsTokenCount": 1305
            },
            "index": 0,
            "completion_start_time": "2025-12-17T17:26:30.372320",
            "thoughtSignature": "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",
            "finish_reason": "STOP"
        },
        "name": None,
        "content": [
            {
                "think": "**Analyzing the Task's Core**\n\nI'm focused on breaking down the request: the subject is USTC, and the task is a question, so I need to understand exactly what is being asked about the university. I'm currently working to pinpoint the scope of the \"question\" about USTC to best formulate my response.\n\n\n**Refining the Approach**\n\nI'm now prioritizing the structure of my response. It seems best to organize it around key aspects: reputation, academic rigor (including research), campus culture, and finally, pros/cons. I'm also considering the implied audience and framing my language accordingly.\n\n\n**Organizing Key Features**\n\nI'm synthesizing the core facts, and currently, I'm trying to decide how to best group the information. I'm leaning towards sections covering reputation and rankings, academic strengths (with a focus on key disciplines and research), campus culture, the location's impact, career prospects, and then a summary with pros and cons. I feel this structure would provide a balanced overview.\n\n\n**Detailing the Content**\n\nI'm now drafting the content, section by section. The introduction is set, and I've fleshed out the \"Academic Strength\" section, focusing on core disciplines, research strengths (quantum computing, fusion energy), and faculty. I've also completed the \"Study Atmosphere\" section, covering the \"hardcore\" reputation and cultural aspects of studying at USTC.\n\n\n**Reviewing the Details**\n\nI'm now putting the finishing touches on the \"Career/Further Studies\" and \"Location\" sections. I've highlighted the alumni networks and domestic opportunities, and I've also balanced the pros and cons of Hefei as a location, adding a bit about the city's tech hub status. After this I'll be summarizing the key aspects.\n\n\n**Summarizing the Core Points**\n\nI'm now consolidating the key findings. I'm extracting and structuring the pros and cons, specifically highlighting the benefits of USTC\'s top-tier education, research resources, and the distinctive \"100% freedom to change majors\" policy. Simultaneously, I'm noting potential downsides like the location, rigorous workload, and gender imbalance to provide a balanced view."
            },
            {
                "text": "中国科学技术大学（简称“中科大”或“USTC”）是中国顶尖的大学之一，也是著名的“C9联盟”成员。\n\n要评价中科大怎么样，可以用一句话概括：**它是中国最像“加州理工学院”的大学——规模小、精英化、理科极强、学风极其硬核。**\n\n以下从学术地位、学习氛围、出路、地理位置和优缺点五个维度为您详细分析：\n\n### 1. 学术地位与硬实力\n*   **顶级头衔：** 985、211、“双一流”A类建设高校，华东五校之一，C9联盟成员。\n*   **中科院直属：** 这是中科大最大的后台。它隶属于中国科学院，拥有“全院办校、所系结合”的独特优势。很多老师就是中科院的顶尖研究员，学生去中科院各研究所实习、做科研非常方便。\n*   **王牌专业：** 物理学、化学、天文学、地球物理学、核科学等**基础理科**在国内几乎是数一数二的水平。近年来在**量子通信、人工智能、高温超导**等前沿领域更是世界领先（例如潘建伟院士团队）。\n*   **精英教育：** 中科大坚持不扩招，每年本科招生人数很少（约1800-2000人），保证了极高的人均资源拥有率。\n\n### 2. 学习氛围与校园文化\n*   **“不要命的上科大”：** 这是一句流传很广的话。中科大的学风在国内是出了名的严谨和扎实。这里没有太多的花哨活动，大部分学生都非常沉得下心来搞学习、做科研。\n*   **转专业自由：** 这是中科大最大的招生亮点之一。**全校本科生享有100%自主选择专业的权利**，门槛极低。这意味着你不用担心被调剂到不喜欢的冷门专业，进了校门可以再选。\n*   **少年班：** 中科大的少年班和创新试点班是国内最早也是最成功的英才教育模式，汇聚了大量智商超群的天才少年。\n\n### 3. 毕业出路\n*   **深造率极高：** 中科大又被称为“科学家的摇篮”。本科毕业生的深造率（读研/博）常年位居全国高校前列（通常在70%-80%以上）。\n*   **“美国名校预备役”：** 在国际学术界，USTC的本科学位含金量极高，美国顶尖大学非常认可中科大的学生。因此，中科大的出国留学（尤其是去美国全奖读博）的比例和质量非常高，校友遍布华尔街和硅谷。\n*   **就业：** 虽然学校偏重理科，但理工科的逻辑思维和数学基础让毕业生在互联网、金融量化、高科技企业极其抢手。\n\n### 4. 地理位置（争议点）\n*   **坐标安徽合肥：** 相比于北京（清北）、上海（复交），合肥在城市的繁华程度、国际化视野和商业实习机会上确实稍逊一筹。\n*   **利弊分析：**\n    *   **弊：** 想要在本科期间去顶级外企、投行、大厂实习，不如京沪便利；娱乐生活相对单调。\n    *   **利：** 合肥是国家综合性科学中心，对中科大倾尽全市之力支持，科研环境极佳。且因为诱惑少、房价相对友好，更适合潜心修学。\n\n### 5. 总结：中科大适合什么样的人？\n\n**它的优点：**\n*   国内顶级的理科教育，数理基础打得极牢。\n*   学风纯粹，校友圈层智商极高，攀比的是学术而非物质。\n*   转专业政策对学生最友好。\n*   人均科研经费和资源极高。\n\n**它的挑战（缺点）：**\n*   课业压力巨大，GPA竞争激烈，如果想混日子或者心理抗压能力差，会非常痛苦。\n*   男女比例失衡（男生多），脱单难度相对较大。\n*   非一线城市，对于想走“金融/商业/传媒”等强城市依赖型路线的学生，地缘优势不如京沪。\n\n**结论：**\n如果你**热爱科学、有志于科研、数理化基础好、或者想以后出国深造**，中科大是除了清华北大之外的**最优选**，甚至在某些理科领域优于清北。但如果你向往丰富多彩的都市生活、想尽早进入商业社会搞钱，中科大可能不是最适合你的“游乐场”。"
            }
        ]
    }
}

try:
    response_3 = requests.post(url_msg_chat, headers=headers_3, json=payload_3)
    print(f"状态码: {response_3.status_code}")
    print(f"响应: {response_3.text[:200]}...")
except Exception as e:
    print(f"请求 3 失败: {e}")
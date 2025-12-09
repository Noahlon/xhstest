curl -X POST https://maas.devops.xiaohongshu.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "api-key: QSTea74b32fe649fd5403de8c8b84a2fde5" \
  -d '{
    "model": "dots.llm2.inst-preview",
    "messages": [
      {
        "role": "system",
        "content": "You are a helpful AI assistant. You are Dots, developed by the Humane Intelligence Lab at Rednote (Xiaohongshu)."
      },
      {
        "role": "user", 
        "content": "帮我制定一份日本的五天四夜的旅游攻略，小红书风格"
      }
    ],
    "stream": false,
    "max_tokens": 4096,
    "temperature": 0.9
  }'
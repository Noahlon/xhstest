from ollama import chat
from ollama import ChatResponse

response: ChatResponse = chat(model='qwen2.5vl:3b', messages=[
  {
    'role': 'user',
    'content': '天空是什么颜色？，直接回答',
  },
])
print(response['message']['content'])
# or access fields directly from the response object
print(response.message.content)
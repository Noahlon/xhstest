const chatHistory = document.getElementById('chat-history');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const readPageBtn = document.getElementById('read-page-btn');

let pageContext = ""; // 存储网页内容

// 自动滚动到底部
function scrollToBottom() {
  chatHistory.scrollTop = chatHistory.scrollHeight;
}

// 修改：appendMessage 现在返回创建的 div 元素，以便后续更新内容
function appendMessage(text, type) {
  const div = document.createElement('div');
  div.classList.add('message', type);
  div.textContent = text;
  chatHistory.appendChild(div);
  scrollToBottom();
  return div; // 返回 DOM 元素
}

// 获取当前 Tab 的文本内容 (保持不变)
async function getCurrentTabContent() {
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!tab) return null;

    const result = await chrome.scripting.executeScript({
      target: { tabId: tab.id },
      func: () => document.body.innerText
    });

    if (result && result[0] && result[0].result) {
      let content = result[0].result.trim();
      if (content.length > 5000) {
        content = content.substring(0, 5000) + "...(内容过长已截断)";
      }
      return content;
    }
  } catch (err) {
    console.error("无法读取网页内容:", err);
    appendMessage("无法读取该网页内容（可能是Chrome内部页面或权限不足）。", "system");
  }
  return null;
}

// 处理 "读取网页" 按钮 (保持不变)
readPageBtn.addEventListener('click', async () => {
  readPageBtn.textContent = "读取中...";
  readPageBtn.disabled = true;
  
  const content = await getCurrentTabContent();
  if (content) {
    pageContext = content;
    appendMessage("✅ 已获取网页内容，您可以针对此页面提问了。", "system");
  }
  
  readPageBtn.textContent = "📄 读取当前网页内容";
  readPageBtn.disabled = false;
});

// --- 重写：流式调用 LLM API ---
async function fetchLLMResponse(message, context) {
  const config = await chrome.storage.sync.get(['apiUrl', 'apiKey', 'modelName']);
  
  if (!config.apiKey) {
    appendMessage("请先在插件设置中配置 API Key。", "system");
    return;
  }

  let messages = [];
  if (context) {
    messages.push({
      role: "system",
      content: `以下是用户当前浏览的网页内容:\n\n${context}\n\n请根据以上内容回答用户问题。`
    });
  }
  messages.push({ role: "user", content: message });

  const baseUrl = config.apiUrl.replace(/\/$/, '');
  const url = `${baseUrl}/chat/completions`; 

  console.log("请求 URL:", url);
  console.log("使用模型:", config.modelName || "gpt-3.5-turbo");

  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${config.apiKey}`
      },
      body: JSON.stringify({
        model: config.modelName || "gpt-3.5-turbo",
        messages: messages,
        temperature: 0.7,
        stream: true // 1. 开启流式输出
      })
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`请求失败 (${response.status}): ${errorText.substring(0, 100)}...`);
    }

    // 2. 创建一个空的 AI 消息框，准备接收数据
    const messageDiv = appendMessage("", "ai");
    let fullText = "";

    // 3. 设置读取器
    const reader = response.body.getReader();
    const decoder = new TextDecoder("utf-8");
    let buffer = ""; // 用于处理并不完整的 JSON 数据包

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      // 解码二进制块
      const chunk = decoder.decode(value, { stream: true });
      buffer += chunk;

      // API 返回的数据可能像这样： data: {...} \n\n data: {...}
      // 我们需要按换行符分割处理
      const lines = buffer.split('\n');
      
      // 这里的逻辑是：最后一行可能是不完整的，留到下一次循环处理
      buffer = lines.pop(); 

      for (const line of lines) {
        const trimmedLine = line.trim();
        if (!trimmedLine.startsWith('data: ')) continue;
        
        const jsonStr = trimmedLine.replace('data: ', '');
        
        if (jsonStr === '[DONE]') {
          console.log("流传输结束");
          return;
        }

        try {
          const data = JSON.parse(jsonStr);
          // 在流式模式下，内容通常在 choices[0].delta.content 中
          const delta = data.choices[0].delta;
          if (delta && delta.content) {
            fullText += delta.content;
            
            // 4. 实时更新 UI
            messageDiv.textContent = fullText; 
            // 如果希望支持 Markdown，可以使用 messageDiv.innerHTML = marked.parse(fullText);
            
            scrollToBottom();
          }
        } catch (e) {
          console.error("JSON 解析错误 (忽略此行):", e, jsonStr);
        }
      }
    }

  } catch (error) {
    console.error(error);
    appendMessage(`错误: ${error.message}`, "system");
  }
}

// 发送消息处理 (保持不变，只是 fetchLLMResponse 现在是流式的)
async function handleSend() {
  const text = userInput.value.trim();
  if (!text) return;

  appendMessage(text, "user");
  userInput.value = '';
  sendBtn.disabled = true;
  sendBtn.textContent = "生成中..."; // 修改提示文字

  await fetchLLMResponse(text, pageContext);

  sendBtn.disabled = false;
  sendBtn.textContent = "发送";
}

sendBtn.addEventListener('click', handleSend);
userInput.addEventListener('keypress', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    handleSend();
  }
});

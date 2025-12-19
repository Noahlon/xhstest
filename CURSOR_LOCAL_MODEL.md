# Cursor 本地模型配置指南

## 快速配置步骤

### 1. 确保本地模型服务正在运行

#### 使用 Ollama（推荐）
```bash
# 安装 Ollama（如果还没安装）
# macOS: brew install ollama
# 或访问 https://ollama.ai

# 启动 Ollama 服务
ollama serve

# 在另一个终端拉取模型（可选）
ollama pull qwen2.5vl:3b
```

#### 使用 LM Studio
1. 下载并安装 LM Studio
2. 启动本地服务器（通常在 `http://localhost:1234`）

### 2. 在 Cursor 中配置本地模型

#### 方法 A: 通过设置界面（推荐）

1. **打开 Cursor 设置**
   - macOS: `Cmd + ,`
   - Windows/Linux: `Ctrl + ,`

2. **进入 AI 设置**
   - 搜索 "AI" 或 "Model"
   - 或直接导航到 `Settings > Features > AI`

3. **配置模型提供商**
   - 找到 "Model Provider" 或 "AI Provider"
   - 选择 "Custom" 或 "OpenAI Compatible"

4. **填写配置信息**
   ```
   API Base URL: http://localhost:11434/v1  (Ollama)
   或
   API Base URL: http://localhost:1234/v1  (LM Studio)
   
   Model Name: qwen2.5vl:3b  (根据你的模型调整)
   
   API Key: 留空或填写任意值（本地服务通常不需要）
   ```

#### 方法 B: 通过 Cursor 配置文件

创建或编辑 `~/.cursor/config.json`（macOS/Linux）或 `%APPDATA%\Cursor\config.json`（Windows）：

```json
{
  "ai": {
    "provider": "custom",
    "apiBase": "http://localhost:11434/v1",
    "model": "qwen2.5vl:3b",
    "apiKey": ""
  }
}
```

#### 方法 C: 使用环境变量

在 `~/.zshrc` 或 `~/.bashrc` 中添加：

```bash
export CURSOR_MODEL_API_BASE=http://localhost:11434/v1
export CURSOR_MODEL_NAME=qwen2.5vl:3b
```

然后重启 Cursor。

### 3. 验证配置

1. 在 Cursor 中打开任意文件
2. 使用 `Cmd/Ctrl + L` 打开 AI 聊天
3. 输入测试问题，看是否能正常响应

## 常见问题

### Q: Cursor 无法连接到本地模型？
A: 
1. 确认本地服务正在运行：`curl http://localhost:11434/v1/models` (Ollama)
2. 检查防火墙设置
3. 确认端口号正确

### Q: 如何切换回云端模型？
A: 在设置中将 Provider 改回 "OpenAI" 或 "Anthropic"

### Q: 支持哪些本地模型服务？
A: 
- ✅ Ollama（推荐，最简单）
- ✅ LM Studio
- ✅ 任何兼容 OpenAI API 的服务（如 vLLM、text-generation-webui）

### Q: 如何测试本地模型连接？
A: 使用项目中的测试脚本：

```bash
# 测试 Ollama
cd ollama
python ollamatest.py
```

## 推荐配置

### 开发场景推荐模型

- **代码补全**: `qwen2.5:7b` 或 `codellama:7b`
- **代码理解**: `qwen2.5:14b` 或 `deepseek-coder:6.7b`
- **多模态**: `qwen2.5vl:3b` 或 `llava:7b`

### 性能优化

- 使用 GPU 加速（如果可用）
- 调整模型大小以平衡速度和性能
- 考虑使用量化模型（如 `qwen2.5:7b-q4_0`）

## 相关文件

- `ollama/ollamatest.py` - Ollama 测试示例
- `autotest/config.py` - Kimi API 配置示例
- `爬虫/config.py` - 爬虫使用的模型配置


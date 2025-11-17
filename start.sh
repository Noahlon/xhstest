#!/bin/bash

# 设置端口号
PORT=8001

echo "=== 检查端口 $PORT 占用情况 ==="

# 检查端口是否被占用
PID=$(lsof -ti :$PORT)

if [ -n "$PID" ]; then
    echo "端口 $PORT 被进程 $PID 占用"
    echo "正在终止进程 $PID..."
    
    # 尝试正常终止
    kill $PID 2>/dev/null
    
    # 等待2秒检查是否成功终止
    sleep 2
    
    # 检查进程是否仍然存在
    if ps -p $PID > /dev/null 2>&1; then
        echo "正常终止失败，尝试强制终止..."
        kill -9 $PID 2>/dev/null
        sleep 1
    fi
    
    # 最终确认
    if lsof -ti :$PORT > /dev/null 2>&1; then
        echo "错误: 无法终止占用端口 $PORT 的进程"
        exit 1
    else
        echo "成功终止进程 $PID"
    fi
else
    echo "端口 $PORT 未被占用"
fi

echo -e "\n=== 启动 Python CGI HTTP 服务器 ==="
echo "服务器将在 http://localhost:$PORT 启动"
echo "按 Ctrl+C 停止服务器"

# 启动 Python 服务器
python3 -m http.server $PORT --cgi
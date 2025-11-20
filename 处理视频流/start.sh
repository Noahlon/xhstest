#!/bin/bash

PORT=8000

# 检查端口是否被占用
PID=$(lsof -ti tcp:${PORT})

if [ -n "$PID" ]; then
    echo "端口 $PORT 已被占用，正在结束进程 $PID..."
    kill -9 $PID
    sleep 1
fi

echo "启动 uvicorn 服务..."
uvicorn main:app --host 0.0.0.0 --port $PORT --reload
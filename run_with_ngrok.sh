#!/bin/bash
# 启动 FastAPI 服务
uvicorn app:app --host 0.0.0.0 --port 8000 &

# 启动 ngrok 隧道，将本地 8000 端口暴露到公网
ngrok http 8000

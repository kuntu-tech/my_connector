#!/usr/bin/env python3
"""
启动 Analysis API 服务的脚本
"""
import uvicorn
import os
from dotenv import load_dotenv

def main():
    """启动 API 服务"""
    # 加载环境变量
    load_dotenv()
    
    # 检查必要的环境变量
    required_vars = ["OPENAI_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"警告: 以下环境变量未设置: {', '.join(missing_vars)}")
        print("API 可能无法正常工作")
    
    # 启动服务器
    print("启动 AI Analysis API 服务...")
    print("API 文档地址: http://localhost:8000/docs")
    print("健康检查地址: http://localhost:8000/health")
    print("分析接口地址: http://localhost:8000/analyze")
    
    uvicorn.run(
        "analysis_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()

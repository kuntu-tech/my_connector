#!/usr/bin/env python3
"""
启动 BI Analysis API 服务的脚本
"""
import uvicorn
import os
from dotenv import load_dotenv

def main():
    """启动 API 服务"""
    # 加载环境变量
    load_dotenv()
    
    # 检查必要的环境变量
    required_vars = ["OPENAI_API_KEY", "SUPABASE_PROJECT_ID", "SUPABASE_ACCESS_TOKEN"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    print("=" * 60)
    print("BI Analysis API 环境变量检查")
    print("=" * 60)
    print(f"OPENAI_API_KEY: {'已设置' if os.getenv('OPENAI_API_KEY') else '未设置'}")
    print(f"SUPABASE_PROJECT_ID: {'已设置' if os.getenv('SUPABASE_PROJECT_ID') else '未设置'}")
    print(f"SUPABASE_ACCESS_TOKEN: {'已设置' if os.getenv('SUPABASE_ACCESS_TOKEN') else '未设置'}")
    print(f"USER_NAME: {os.getenv('USER_NAME', 'huimin')}")
    print(f"DATA_REVIEW_RESULT: {os.getenv('DATA_REVIEW_RESULT', 'true')}")
    print(f"ENVIRONMENT: {os.getenv('ENVIRONMENT', 'production')}")
    print("=" * 60)
    
    if missing_vars:
        print(f"警告: 以下环境变量未设置: {', '.join(missing_vars)}")
        print("API 可能无法正常工作")
    
    # 启动服务器
    print("启动 BI Analysis API 服务...")
    print("API 文档地址: http://localhost:8000/docs")
    print("健康检查地址: http://localhost:8000/health")
    print("分析接口地址: http://localhost:8000/analyze")
    
    # 获取端口，Render 会通过环境变量 PORT 指定端口
    port = int(os.environ.get("PORT", 8000))
    
    # 检查是否为开发环境
    is_development = os.environ.get("ENVIRONMENT", "production") == "development"
    
    uvicorn.run(
        "app:app",  # 使用 BI Analysis API
        host="0.0.0.0",
        port=port,
        reload=is_development,  # 只在开发环境启用热重载
        log_level="info"
    )

if __name__ == "__main__":
    main()


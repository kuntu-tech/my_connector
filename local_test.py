#!/usr/bin/env python3
"""
本地测试 AI 分析接口
"""
import os
import sys
import json
import requests
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_analysis_api():
    """测试 AI 分析接口"""
    
    # 从环境变量获取配置
    openai_api_key = os.getenv('OPENAI_API_KEY')
    supabase_project_url = os.getenv('SUPABASE_PROJECT_URL')
    supabase_access_token = os.getenv('SUPABASE_ACCESS_TOKEN')
    user_name = os.getenv('USER_NAME', 'huimin')
    data_review_result = os.getenv('DATA_REVIEW_RESULT', 'true').lower() == 'true'
    
    print("环境变量检查:")
    print(f"  OPENAI_API_KEY: {'已配置' if openai_api_key else '未配置'}")
    print(f"  SUPABASE_PROJECT_URL: {'已配置' if supabase_project_url else '未配置'}")
    print(f"  SUPABASE_ACCESS_TOKEN: {'已配置' if supabase_access_token else '未配置'}")
    print(f"  USER_NAME: {user_name}")
    print(f"  DATA_REVIEW_RESULT: {data_review_result}")
    print()
    
    # 检查必要的环境变量
    if not openai_api_key:
        print("错误: OPENAI_API_KEY 未配置")
        return False
    
    if not supabase_project_url:
        print("错误: SUPABASE_PROJECT_URL 未配置")
        return False
    
    if not supabase_access_token:
        print("错误: SUPABASE_ACCESS_TOKEN 未配置")
        return False
    
    # 准备测试数据
    test_data = {
        "analysis_type": "schema",
        "supabase_project_url": supabase_project_url,
        "supabase_access_token": supabase_access_token,
        "user_name": user_name,
        "data_review_result": data_review_result,
        "openai_api_key": openai_api_key
    }
    
    print("开始测试 AI 分析接口...")
    print(f"测试数据: {json.dumps(test_data, indent=2, ensure_ascii=False)}")
    print()
    
    try:
        # 导入并测试本地 API
        print("导入本地 API 模块...")
        from analysis_api import app
        from fastapi.testclient import TestClient
        
        # 创建测试客户端
        client = TestClient(app)
        
        # 测试健康检查
        print("测试健康检查接口...")
        health_response = client.get("/health")
        print(f"  状态码: {health_response.status_code}")
        print(f"  响应: {health_response.json()}")
        print()
        
        # 测试配置检查
        print("测试配置检查接口...")
        config_response = client.get("/config")
        print(f"  状态码: {config_response.status_code}")
        print(f"  响应: {config_response.json()}")
        print()
        
        # 测试分析接口
        print("测试分析接口...")
        analysis_response = client.post("/analyze", json=test_data)
        print(f"  状态码: {analysis_response.status_code}")
        
        if analysis_response.status_code == 200:
            print("  分析接口测试成功!")
            result = analysis_response.json()
            print(f"  响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
        else:
            print("  分析接口测试失败!")
            print(f"  错误: {analysis_response.text}")
            return False
        
        print()
        print("所有测试通过!")
        return True
        
    except ImportError as e:
        print(f"导入错误: {e}")
        print("请确保安装了所有必要的依赖: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"测试失败: {e}")
        return False

if __name__ == "__main__":
    print("开始本地 AI 分析接口测试")
    print("=" * 50)
    
    success = test_analysis_api()
    
    print("=" * 50)
    if success:
        print("本地测试完成，可以安全推送到服务器!")
    else:
        print("本地测试失败，请修复问题后再推送!")
        sys.exit(1)

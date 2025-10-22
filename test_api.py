#!/usr/bin/env python3
"""
测试 Analysis API 的脚本
"""
import requests
import json
import time
from typing import Dict, Any

API_BASE_URL = "http://localhost:8000"

def test_health_check():
    """测试健康检查端点"""
    print("=== 测试健康检查 ===")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            print("✅ 健康检查通过")
            print(f"响应: {response.json()}")
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 健康检查错误: {e}")

def test_config():
    """测试配置端点"""
    print("\n=== 测试配置信息 ===")
    try:
        response = requests.get(f"{API_BASE_URL}/config")
        if response.status_code == 200:
            print("✅ 配置信息获取成功")
            print(f"响应: {response.json()}")
        else:
            print(f"❌ 配置信息获取失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 配置信息获取错误: {e}")

def test_analyze_schema():
    """测试 Schema 分析"""
    print("\n=== 测试 Schema 分析 ===")
    
    request_data = {
        "analysis_type": "schema",
        "supabase_project_url": "https://mcp.supabase.com/mcp?project_ref=yzcdbefleociqdpxsqjt",
        "supabase_access_token": "your_token_here",  # 请替换为实际的 token
        "user_name": "test_user",
        "data_review_result": True
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/analyze",
            json=request_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ Schema 分析请求成功")
            result = response.json()
            print(f"分析类型: {result['analysis_type']}")
            print(f"执行时间: {result['execution_time']:.2f}秒")
            print(f"生成文件: {result['files_generated']}")
        else:
            print(f"❌ Schema 分析失败: {response.status_code}")
            print(f"错误信息: {response.text}")
    except Exception as e:
        print(f"❌ Schema 分析错误: {e}")

def test_analyze_market():
    """测试市场分析"""
    print("\n=== 测试市场分析 ===")
    
    request_data = {
        "analysis_type": "market",
        "supabase_project_url": "https://mcp.supabase.com/mcp?project_ref=yzcdbefleociqdpxsqjt",
        "supabase_access_token": "your_token_here",  # 请替换为实际的 token
        "user_name": "test_user",
        "data_review_result": True
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/analyze",
            json=request_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ 市场分析请求成功")
            result = response.json()
            print(f"分析类型: {result['analysis_type']}")
            print(f"执行时间: {result['execution_time']:.2f}秒")
            print(f"生成文件: {result['files_generated']}")
        else:
            print(f"❌ 市场分析失败: {response.status_code}")
            print(f"错误信息: {response.text}")
    except Exception as e:
        print(f"❌ 市场分析错误: {e}")

def test_results_list():
    """测试结果列表端点"""
    print("\n=== 测试结果列表 ===")
    try:
        response = requests.get(f"{API_BASE_URL}/results")
        if response.status_code == 200:
            print("✅ 结果列表获取成功")
            result = response.json()
            print(f"文件数量: {result['count']}")
            print(f"文件列表: {result['files']}")
        else:
            print(f"❌ 结果列表获取失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 结果列表获取错误: {e}")

def main():
    """主测试函数"""
    print("开始测试 AI Analysis API...")
    print(f"API 基础地址: {API_BASE_URL}")
    print("=" * 50)
    
    # 测试各个端点
    test_health_check()
    test_config()
    test_analyze_schema()
    test_analyze_market()
    test_results_list()
    
    print("\n" + "=" * 50)
    print("测试完成！")
    print("\n💡 提示:")
    print("1. 请确保 API 服务正在运行 (python start_api.py)")
    print("2. 请替换测试中的 'your_token_here' 为实际的 Supabase access token")
    print("3. 访问 http://localhost:8000/docs 查看完整的 API 文档")

if __name__ == "__main__":
    main()

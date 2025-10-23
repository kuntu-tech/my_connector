#!/usr/bin/env python3
"""
BI Analysis API 测试脚本
"""
import requests
import json
import time

# API 基础 URL
BASE_URL = "http://localhost:8000"

def test_health_check():
    """测试健康检查接口"""
    print("测试健康检查接口...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"健康检查失败: {e}")
        return False

def test_config():
    """测试配置接口"""
    print("\n测试配置接口...")
    try:
        response = requests.get(f"{BASE_URL}/config")
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"配置检查失败: {e}")
        return False

def test_analyze():
    """测试分析接口"""
    print("\n测试分析接口...")
    
    # 测试数据
    test_data = {
        "analysis_type": "schema",
        "supabase_project_id": "test_project_id",
        "supabase_access_token": "test_token",
        "user_name": "test_user",
        "data_review_result": True,
        "openai_api_key": "test_key"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/analyze",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"分析成功: {result['message']}")
            print(f"执行时间: {result['execution_time']:.2f}秒")
        else:
            print(f"分析失败: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"分析测试失败: {e}")
        return False

def test_results():
    """测试结果接口"""
    print("\n测试结果接口...")
    try:
        response = requests.get(f"{BASE_URL}/results")
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"结果测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("BI Analysis API 测试")
    print("=" * 60)
    
    # 等待服务启动
    print("等待服务启动...")
    time.sleep(2)
    
    # 运行测试
    tests = [
        ("健康检查", test_health_check),
        ("配置检查", test_config),
        ("结果列表", test_results),
        ("分析接口", test_analyze),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        success = test_func()
        results.append((test_name, success))
    
    # 输出测试结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    for test_name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{test_name}: {status}")
    
    total_tests = len(results)
    passed_tests = sum(1 for _, success in results if success)
    
    print(f"\n总计: {passed_tests}/{total_tests} 测试通过")
    
    if passed_tests == total_tests:
        print("🎉 所有测试通过！")
    else:
        print("⚠️  部分测试失败，请检查服务状态")

if __name__ == "__main__":
    main()


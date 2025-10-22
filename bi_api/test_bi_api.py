#!/usr/bin/env python3
"""
BI API 测试脚本
"""
import requests
import json
import time
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()

# API 基础URL
BASE_URL = "http://localhost:8000"

def test_health_check():
    """测试健康检查端点"""
    print("=" * 50)
    print("测试健康检查端点")
    print("=" * 50)
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"健康检查失败: {e}")
        return False

def test_config():
    """测试配置端点"""
    print("=" * 50)
    print("测试配置端点")
    print("=" * 50)
    
    try:
        response = requests.get(f"{BASE_URL}/config")
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"配置检查失败: {e}")
        return False

def test_schema_analysis():
    """测试Schema分析"""
    print("=" * 50)
    print("测试Schema分析")
    print("=" * 50)
    
    # 从环境变量获取配置
    request_data = {
        "analysis_type": "schema",
        "supabase_project_id": os.getenv("SUPABASE_PROJECT_ID", "yzcdbefleociqdpxsqjt"),
        "supabase_access_token": os.getenv("SUPABASE_ACCESS_TOKEN", "sbp_82dc8d631fde6e235ec5b7d4792b8d6fb66ad5cf"),
        "user_name": os.getenv("USER_NAME", "huimin"),
        "data_review_result": True,
        "openai_api_key": os.getenv("OPENAI_API_KEY")
    }
    
    try:
        print("发送请求数据:")
        print(json.dumps(request_data, indent=2, ensure_ascii=False))
        
        response = requests.post(
            f"{BASE_URL}/analyze",
            json=request_data,
            timeout=300  # 5分钟超时
        )
        
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"分析成功!")
            print(f"执行时间: {result.get('execution_time', 0):.2f}秒")
            print(f"生成文件: {result.get('files_generated', [])}")
            print(f"结果摘要: {result.get('message', '')}")
            return True
        else:
            print(f"分析失败: {response.text}")
            return False
            
    except Exception as e:
        print(f"Schema分析测试失败: {e}")
        return False

def test_complete_analysis():
    """测试完整分析流程"""
    print("=" * 50)
    print("测试完整分析流程")
    print("=" * 50)
    
    # 从环境变量获取配置
    request_data = {
        "analysis_type": "all",
        "supabase_project_id": os.getenv("SUPABASE_PROJECT_ID", "yzcdbefleociqdpxsqjt"),
        "supabase_access_token": os.getenv("SUPABASE_ACCESS_TOKEN", "sbp_82dc8d631fde6e235ec5b7d4792b8d6fb66ad5cf"),
        "user_name": os.getenv("USER_NAME", "huimin"),
        "data_review_result": True,
        "openai_api_key": os.getenv("OPENAI_API_KEY")
    }
    
    try:
        print("发送完整分析请求...")
        print(json.dumps(request_data, indent=2, ensure_ascii=False))
        
        response = requests.post(
            f"{BASE_URL}/analyze",
            json=request_data,
            timeout=600  # 10分钟超时
        )
        
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"完整分析成功!")
            print(f"执行时间: {result.get('execution_time', 0):.2f}秒")
            print(f"生成文件: {result.get('files_generated', [])}")
            print(f"结果摘要: {result.get('message', '')}")
            
            # 显示分析结果的结构
            results = result.get('results', {})
            print(f"分析结果包含: {list(results.keys())}")
            
            return True
        else:
            print(f"完整分析失败: {response.text}")
            return False
            
    except Exception as e:
        print(f"完整分析测试失败: {e}")
        return False

def test_results_endpoints():
    """测试结果管理端点"""
    print("=" * 50)
    print("测试结果管理端点")
    print("=" * 50)
    
    try:
        # 测试列出结果
        response = requests.get(f"{BASE_URL}/results")
        print(f"列出结果状态码: {response.status_code}")
        if response.status_code == 200:
            results = response.json()
            print(f"结果文件数量: {results.get('count', 0)}")
            print(f"结果文件: {results.get('files', [])}")
            
            # 如果有文件，测试获取特定文件
            files = results.get('files', [])
            if files:
                filename = files[0]
                print(f"测试获取文件: {filename}")
                file_response = requests.get(f"{BASE_URL}/results/{filename}")
                print(f"获取文件状态码: {file_response.status_code}")
                if file_response.status_code == 200:
                    file_data = file_response.json()
                    print(f"文件大小: {file_data.get('size', 0)} 字符")
                    print(f"最后修改: {file_data.get('last_modified', '')}")
        
        return True
        
    except Exception as e:
        print(f"结果管理测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("BI API 测试开始")
    print("=" * 60)
    
    tests = [
        ("健康检查", test_health_check),
        ("配置检查", test_config),
        ("Schema分析", test_schema_analysis),
        ("结果管理", test_results_endpoints),
        # ("完整分析", test_complete_analysis),  # 注释掉，因为耗时较长
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n正在运行: {test_name}")
        try:
            if test_func():
                print(f"✅ {test_name} 通过")
                passed += 1
            else:
                print(f"❌ {test_name} 失败")
        except Exception as e:
            print(f"❌ {test_name} 异常: {e}")
    
    print("\n" + "=" * 60)
    print(f"测试完成: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过!")
    else:
        print("⚠️  部分测试失败，请检查API服务")

if __name__ == "__main__":
    main()

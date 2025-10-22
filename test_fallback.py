#!/usr/bin/env python3
"""
测试降级方案
"""
import requests
import json
import time
from datetime import datetime

def test_fallback_mechanism():
    """测试降级机制"""
    
    base_url = "https://my-connector.onrender.com"
    
    print("=" * 60)
    print("测试降级方案")
    print("=" * 60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"服务地址: {base_url}")
    print()
    
    # 测试数据 - 使用包含星号的 API 密钥来触发降级
    test_data_with_asterisks = {
        "analysis_type": "schema",
        "supabase_project_url": "https://mcp.supabase.com/mcp?project_ref=yzcdbefleociqdpxsqjt",
        "supabase_access_token": "sbp_82dc8d631fde6e235ec5b7d4792b8d6fb66ad5cf",
        "user_name": "huimin",
        "data_review_result": True,
        "openai_api_key": "sk-proj-********************************************************************************************************************************************************Oi0A"  # 包含星号的密钥
    }
    
    print("1. 测试包含星号的 API 密钥 (应该触发降级)...")
    print(f"   原始密钥: {test_data_with_asterisks['openai_api_key']}")
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{base_url}/analyze", 
            json=test_data_with_asterisks,
            timeout=120
        )
        end_time = time.time()
        
        print(f"   状态码: {response.status_code}")
        print(f"   响应时间: {end_time - start_time:.2f} 秒")
        
        if response.status_code == 200:
            print("   降级方案: 成功!")
            result = response.json()
            print(f"   分析类型: {result.get('analysis_type', 'N/A')}")
            print(f"   成功状态: {result.get('success', 'N/A')}")
            print(f"   执行时间: {result.get('execution_time', 'N/A')} 秒")
            
            # 显示分析结果摘要
            if 'results' in result and 'schema_analysis' in result['results']:
                analysis_text = result['results']['schema_analysis']
                print(f"   分析结果长度: {len(analysis_text)} 字符")
                print(f"   分析结果预览: {analysis_text[:200]}...")
            
            return True
        else:
            print("   降级方案: 失败!")
            print(f"   错误信息: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("   请求超时")
        return False
    except requests.exceptions.RequestException as e:
        print(f"   请求错误: {e}")
        return False

def test_normal_key():
    """测试正常密钥"""
    
    base_url = "https://my-connector.onrender.com"
    
    print("\n2. 测试正常 API 密钥...")
    
    # 测试数据 - 使用正常的 API 密钥
    test_data_normal = {
        "analysis_type": "schema",
        "supabase_project_url": "https://mcp.supabase.com/mcp?project_ref=yzcdbefleociqdpxsqjt",
        "supabase_access_token": "sbp_82dc8d631fde6e235ec5b7d4792b8d6fb66ad5cf",
        "user_name": "huimin",
        "data_review_result": True,
        "openai_api_key": "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"
    }
    
    print(f"   正常密钥: {test_data_normal['openai_api_key'][:20]}...")
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{base_url}/analyze", 
            json=test_data_normal,
            timeout=120
        )
        end_time = time.time()
        
        print(f"   状态码: {response.status_code}")
        print(f"   响应时间: {end_time - start_time:.2f} 秒")
        
        if response.status_code == 200:
            print("   正常密钥: 成功!")
            return True
        else:
            print("   正常密钥: 失败!")
            print(f"   错误信息: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("   请求超时")
        return False
    except requests.exceptions.RequestException as e:
        print(f"   请求错误: {e}")
        return False

def main():
    """主函数"""
    print("开始测试降级方案")
    print("=" * 60)
    
    # 测试降级机制
    fallback_success = test_fallback_mechanism()
    
    # 测试正常密钥
    normal_success = test_normal_key()
    
    print("\n" + "=" * 60)
    print("测试结果总结")
    print("=" * 60)
    print(f"降级方案测试: {'成功' if fallback_success else '失败'}")
    print(f"正常密钥测试: {'成功' if normal_success else '失败'}")
    
    if fallback_success:
        print("\n降级方案工作正常!")
        print("即使环境变量有问题，服务也能正常运行")
    else:
        print("\n降级方案需要进一步调试")
    
    print("=" * 60)

if __name__ == "__main__":
    main()

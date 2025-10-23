#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试集成分析API接口
"""
import requests
import json
import time
from datetime import datetime

# API配置
API_BASE_URL = "http://localhost:8000"
INTEGRATED_ANALYSIS_ENDPOINT = f"{API_BASE_URL}/integrated-analysis"

def test_integrated_analysis_api():
    """测试集成分析API"""
    
    # 测试数据
    test_request = {
        "supabase_project_id": "your_project_id_here",
        "supabase_access_token": "your_access_token_here", 
        "user_name": "test_user",
        "openai_api_key": "your_openai_key_here",  # 可选
        "analysis_type": "market_only"  # 或者 "full_integrated"
    }
    
    print("=" * 60)
    print("测试集成分析API接口")
    print("=" * 60)
    print(f"API端点: {INTEGRATED_ANALYSIS_ENDPOINT}")
    print(f"请求时间: {datetime.now().isoformat()}")
    print("=" * 60)
    
    try:
        # 发送POST请求
        print("发送请求...")
        start_time = time.time()
        
        response = requests.post(
            INTEGRATED_ANALYSIS_ENDPOINT,
            json=test_request,
            headers={"Content-Type": "application/json"},
            timeout=300  # 5分钟超时
        )
        
        request_time = time.time() - start_time
        
        print(f"响应状态码: {response.status_code}")
        print(f"请求耗时: {request_time:.2f}秒")
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ 请求成功!")
            print(f"分析类型: {result.get('analysis_type')}")
            print(f"执行时间: {result.get('execution_time'):.2f}秒")
            print(f"生成文件数: {len(result.get('files_generated', []))}")
            print(f"时间戳: {result.get('timestamp')}")
            
            # 显示生成的文件
            files = result.get('files_generated', [])
            if files:
                print("\n📁 生成的文件:")
                for file_path in files:
                    print(f"  - {file_path}")
            
            # 显示结果摘要
            results = result.get('results', {})
            if 'market_analysis' in results:
                print("\n📊 市场分析结果:")
                market_data = results['market_analysis']
                if 'summary' in market_data:
                    summary = market_data['summary']
                    print(f"  - 标题: {summary.get('headline', 'N/A')}")
                    print(f"  - 核心洞察: {summary.get('core_insight', 'N/A')[:100]}...")
                
            if 'validation_reports' in results:
                reports = results['validation_reports']
                print(f"\n🔍 问题验证报告: {len(reports)}个问题")
                
        else:
            print(f"\n❌ 请求失败!")
            print(f"错误信息: {response.text}")
            
    except requests.exceptions.Timeout:
        print("\n⏰ 请求超时 (5分钟)")
        print("集成分析可能需要更长时间，请检查服务器日志")
        
    except requests.exceptions.ConnectionError:
        print("\n🔌 连接错误")
        print("请确保API服务器正在运行: python bi_api/start_bi_api.py")
        
    except Exception as e:
        print(f"\n💥 测试失败: {str(e)}")

def test_health_check():
    """测试健康检查接口"""
    health_url = f"{API_BASE_URL}/health"
    
    try:
        print("\n" + "=" * 60)
        print("测试健康检查接口")
        print("=" * 60)
        
        response = requests.get(health_url, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 服务健康")
            print(f"状态: {result.get('status')}")
            print(f"服务: {result.get('service')}")
            print(f"时间戳: {result.get('timestamp')}")
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 健康检查失败: {str(e)}")

def test_config():
    """测试配置接口"""
    config_url = f"{API_BASE_URL}/config"
    
    try:
        print("\n" + "=" * 60)
        print("测试配置接口")
        print("=" * 60)
        
        response = requests.get(config_url, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 配置信息获取成功")
            print(f"OpenAI API Key配置: {result.get('openai_api_key_configured')}")
            print(f"Supabase Project ID配置: {result.get('supabase_project_id_configured')}")
            print(f"Supabase Access Token配置: {result.get('supabase_access_token_configured')}")
        else:
            print(f"❌ 配置获取失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 配置获取失败: {str(e)}")

if __name__ == "__main__":
    print("集成分析API测试脚本")
    print("请确保:")
    print("1. API服务器正在运行: python bi_api/start_bi_api.py")
    print("2. 已正确配置环境变量")
    print("3. 修改测试脚本中的Supabase配置信息")
    print()
    
    # 运行测试
    test_health_check()
    test_config()
    
    # 询问是否运行集成分析测试
    user_input = input("\n是否运行集成分析测试? (y/n): ").lower().strip()
    if user_input == 'y':
        test_integrated_analysis_api()
    else:
        print("跳过集成分析测试")
    
    print("\n测试完成!")

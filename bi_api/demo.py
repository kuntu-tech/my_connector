#!/usr/bin/env python3
"""
BI Analysis API 演示脚本
展示如何使用 API 进行数据分析
"""
import requests
import json
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# API 配置
API_BASE_URL = "http://localhost:8000"

def demo_analysis():
    """演示完整的分析流程"""
    print("=" * 60)
    print("BI Analysis API 演示")
    print("=" * 60)
    
    # 检查环境变量
    print("检查环境变量...")
    openai_key = os.getenv("OPENAI_API_KEY")
    supabase_project_id = os.getenv("SUPABASE_PROJECT_ID")
    supabase_token = os.getenv("SUPABASE_ACCESS_TOKEN")
    
    if not all([openai_key, supabase_project_id, supabase_token]):
        print("❌ 环境变量未完全设置，请检查 .env 文件")
        print("需要的环境变量:")
        print("- OPENAI_API_KEY")
        print("- SUPABASE_PROJECT_ID") 
        print("- SUPABASE_ACCESS_TOKEN")
        return
    
    print("✅ 环境变量检查通过")
    
    # 准备请求数据
    analysis_request = {
        "analysis_type": "all",  # 执行完整分析
        "supabase_project_id": supabase_project_id,
        "supabase_access_token": supabase_token,
        "user_name": "demo_user",
        "data_review_result": True,
        "openai_api_key": openai_key
    }
    
    print(f"\n开始分析...")
    print(f"分析类型: {analysis_request['analysis_type']}")
    print(f"用户: {analysis_request['user_name']}")
    
    try:
        # 发送分析请求
        response = requests.post(
            f"{API_BASE_URL}/analyze",
            json=analysis_request,
            headers={"Content-Type": "application/json"},
            timeout=300  # 5分钟超时
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 分析完成！")
            print(f"执行时间: {result['execution_time']:.2f}秒")
            print(f"生成文件: {len(result['files_generated'])}个")
            print(f"数据库保存: {'是' if result['database_saved'] else '否'}")
            
            # 显示结果摘要
            print("\n分析结果摘要:")
            for key, value in result['results'].items():
                if isinstance(value, str) and len(value) > 100:
                    print(f"- {key}: {value[:100]}...")
                else:
                    print(f"- {key}: {value}")
            
            # 列出生成的文件
            if result['files_generated']:
                print(f"\n生成的文件:")
                for file_path in result['files_generated']:
                    print(f"- {file_path}")
            
        else:
            print(f"❌ 分析失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            
    except requests.exceptions.Timeout:
        print("❌ 请求超时，分析可能需要更长时间")
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败，请确保 API 服务正在运行")
    except Exception as e:
        print(f"❌ 分析过程中出现错误: {e}")

def demo_simple_test():
    """演示简单的接口测试"""
    print("=" * 60)
    print("简单接口测试")
    print("=" * 60)
    
    # 测试健康检查
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            print("✅ 健康检查通过")
            print(f"服务状态: {response.json()['status']}")
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 健康检查异常: {e}")
        return
    
    # 测试配置
    try:
        response = requests.get(f"{API_BASE_URL}/config")
        if response.status_code == 200:
            print("✅ 配置检查通过")
            config = response.json()
            print(f"OpenAI API 配置: {'是' if config['openai_api_key_configured'] else '否'}")
            print(f"Supabase 配置: {'是' if config['supabase_project_id_configured'] else '否'}")
        else:
            print(f"❌ 配置检查失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 配置检查异常: {e}")
    
    # 测试结果列表
    try:
        response = requests.get(f"{API_BASE_URL}/results")
        if response.status_code == 200:
            print("✅ 结果列表获取成功")
            results = response.json()
            print(f"结果文件数量: {results['count']}")
        else:
            print(f"❌ 结果列表获取失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 结果列表获取异常: {e}")

def main():
    """主函数"""
    print("选择演示模式:")
    print("1. 简单接口测试")
    print("2. 完整分析演示")
    print("3. 退出")
    
    choice = input("\n请输入选择 (1-3): ").strip()
    
    if choice == "1":
        demo_simple_test()
    elif choice == "2":
        demo_analysis()
    elif choice == "3":
        print("退出演示")
    else:
        print("无效选择")

if __name__ == "__main__":
    main()


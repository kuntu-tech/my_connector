#!/usr/bin/env python3
"""
测试远程 Render API 接口
"""
import requests
import json
import time
from datetime import datetime

def test_remote_api():
    """测试远程 API 接口"""
    
    # Render 服务地址
    base_url = "https://my-connector.onrender.com"
    
    # 测试参数（使用您提供的参数）
    test_data = {
        "analysis_type": "schema",
        "supabase_project_url": "https://mcp.supabase.com/mcp?project_ref=yzcdbefleociqdpxsqjt",
        "supabase_access_token": "sbp_82dc8d631fde6e235ec5b7d4792b8d6fb66ad5cf",
        "user_name": "huimin",
        "data_review_result": True,
        "openai_api_key": "your_openai_api_key_here"  # 请替换为真实的API密钥
    }
    
    print("=" * 60)
    print("远程 Render API 接口测试")
    print("=" * 60)
    print(f"服务地址: {base_url}")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 显示测试参数
    print("测试参数:")
    print(f"  analysis_type: {test_data['analysis_type']}")
    print(f"  supabase_project_url: {test_data['supabase_project_url']}")
    print(f"  supabase_access_token: {test_data['supabase_access_token'][:20]}...")
    print(f"  user_name: {test_data['user_name']}")
    print(f"  data_review_result: {test_data['data_review_result']}")
    print(f"  openai_api_key: {test_data['openai_api_key'][:20]}...")
    print()
    
    # 1. 测试健康检查接口
    print("1. 测试健康检查接口...")
    try:
        health_response = requests.get(f"{base_url}/health", timeout=30)
        print(f"   状态码: {health_response.status_code}")
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"   响应: {health_data}")
            print("   健康检查: 通过")
        else:
            print(f"   错误: {health_response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"   连接错误: {e}")
        return False
    
    print()
    
    # 2. 测试配置检查接口
    print("2. 测试配置检查接口...")
    try:
        config_response = requests.get(f"{base_url}/config", timeout=30)
        print(f"   状态码: {config_response.status_code}")
        if config_response.status_code == 200:
            config_data = config_response.json()
            print(f"   响应: {config_data}")
            print("   配置检查: 通过")
        else:
            print(f"   错误: {config_response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"   连接错误: {e}")
        return False
    
    print()
    
    # 3. 测试 AI 分析接口
    print("3. 测试 AI 分析接口...")
    print("   正在发送分析请求...")
    
    try:
        start_time = time.time()
        
        # 设置请求头
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        analysis_response = requests.post(
            f"{base_url}/analyze", 
            json=test_data,
            headers=headers,
            timeout=120  # 分析可能需要较长时间
        )
        
        end_time = time.time()
        
        print(f"   状态码: {analysis_response.status_code}")
        print(f"   响应时间: {end_time - start_time:.2f} 秒")
        
        if analysis_response.status_code == 200:
            print("   AI 分析接口: 成功!")
            result = analysis_response.json()
            
            print(f"   成功状态: {result.get('success', 'N/A')}")
            print(f"   分析类型: {result.get('analysis_type', 'N/A')}")
            print(f"   消息: {result.get('message', 'N/A')}")
            print(f"   执行时间: {result.get('execution_time', 'N/A')} 秒")
            print(f"   数据库保存: {result.get('database_saved', 'N/A')}")
            print(f"   生成文件数: {len(result.get('files_generated', []))}")
            
            # 显示分析结果摘要
            if 'results' in result and 'schema_analysis' in result['results']:
                analysis_text = result['results']['schema_analysis']
                print(f"   分析结果长度: {len(analysis_text)} 字符")
                print(f"   分析结果预览: {analysis_text[:300]}...")
                
                # 保存完整结果到文件
                with open('analysis_result.json', 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                print("   完整结果已保存到: analysis_result.json")
            
            return True
        else:
            print("   AI 分析接口: 失败!")
            print(f"   错误信息: {analysis_response.text}")
            
            # 尝试解析错误信息
            try:
                error_data = analysis_response.json()
                if 'detail' in error_data:
                    print(f"   详细错误: {error_data['detail']}")
            except:
                pass
            
            return False
            
    except requests.exceptions.Timeout:
        print("   请求超时: 分析时间过长")
        return False
    except requests.exceptions.RequestException as e:
        print(f"   请求错误: {e}")
        return False

def main():
    """主函数"""
    print("开始测试远程 Render API 接口")
    print("=" * 60)
    
    success = test_remote_api()
    
    print("\n" + "=" * 60)
    print("测试结果总结")
    print("=" * 60)
    
    if success:
        print("测试成功: 远程 API 接口正常工作!")
        print("降级方案已生效，服务可以正常使用!")
    else:
        print("测试失败: 远程 API 接口存在问题!")
        print("请检查服务状态和配置")
    
    print("=" * 60)

if __name__ == "__main__":
    main()

import requests
import json
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 测试品牌策略API
url = "http://localhost:8000/brand-strategy"
data = {
    "supabase_project_id": os.getenv("SUPABASE_PROJECT_ID", "your_supabase_project_id"),
    "supabase_access_token": os.getenv("SUPABASE_ACCESS_TOKEN", "your_supabase_access_token"),
    "user_name": os.getenv("USER_NAME", "huimin"),
    "openai_api_key": os.getenv("OPENAI_API_KEY", "your_openai_api_key")
}

try:
    print("正在测试品牌策略API...")
    response = requests.post(url, json=data, timeout=120)
    
    print(f"状态码: {response.status_code}")
    print(f"响应头: {dict(response.headers)}")
    
    if response.status_code == 200:
        result = response.json()
        print("[OK] API调用成功!")
        print(f"执行时间: {result.get('execution_time', 0):.2f}秒")
        print(f"生成文件: {result.get('files_generated', [])}")
        print(f"品牌策略结果:")
        print(json.dumps(result.get('brand_strategy', {}), ensure_ascii=False, indent=2))
    else:
        print("[ERROR] API调用失败!")
        print(f"错误信息: {response.text}")
        
except requests.exceptions.Timeout:
    print("[ERROR] 请求超时")
except requests.exceptions.ConnectionError:
    print("[ERROR] 连接错误，请检查服务是否启动")
except Exception as e:
    print(f"[ERROR] 发生错误: {e}")
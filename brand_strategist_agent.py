import asyncio
import json
import os
import sys
from datetime import datetime
from typing import Dict, List

from jinja2 import Environment, FileSystemLoader
from pydantic import BaseModel, Field, ConfigDict

from agents import Agent, AgentOutputSchema, HostedMCPTool, ModelSettings, Runner
from dotenv import load_dotenv
from pathlib import Path
import time

load_dotenv()
BRAND_STRATEGIST_PROMPT = (Path(__file__).resolve().parent / "brand_strategist_prompt.md").read_text(encoding="utf-8")


brand_strategist_agent = Agent(
    name="brand_strategist_agent",
    instructions=BRAND_STRATEGIST_PROMPT,
    model="gpt-4.1-nano",
    model_settings=ModelSettings(
        top_p=0.9,
        temperature=0.7,
    )
)

async def run_with_retry(agent, input_msg, max_retries=3, delay=5):
    """带重试机制的运行函数"""
    for attempt in range(max_retries):
        try:
            print(f"尝试第 {attempt + 1} 次调用AI Agent...")
            result = await asyncio.wait_for(
                Runner.run(agent, input=input_msg),
                timeout=60  # 60秒超时
            )
            return result
        except asyncio.TimeoutError:
            print(f"第 {attempt + 1} 次尝试超时")
        except Exception as e:
            print(f"第 {attempt + 1} 次尝试失败: {e}")
        
        if attempt < max_retries - 1:
            print(f"等待 {delay} 秒后重试...")
            await asyncio.sleep(delay)
    
    print("所有重试都失败了，使用模拟结果")
    return None

def parse_arguments():
    """解析命令行参数或配置文件"""
    if len(sys.argv) > 1:
        # 方式1: 从命令行参数读取JSON
        try:
            json_str = sys.argv[1]
            config = json.loads(json_str)
            return config
        except json.JSONDecodeError as e:
            print(f"JSON参数格式错误: {e}")
            sys.exit(1)
    else:
        # 方式2: 从config.json文件读取
        config_file = Path(__file__).resolve().parent / "config.json"
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                print(f"从配置文件读取参数: {config_file}")
                return config
            except json.JSONDecodeError as e:
                print(f"配置文件JSON格式错误: {e}")
                sys.exit(1)
        else:
            print("请提供JSON格式的参数或创建config.json文件")
            print("方式1: python brand_strategist_agent.py '{\"supabase_project_id\": \"xxx\", \"openai_api_key\": \"xxx\"}'")
            print("方式2: 创建config.json文件包含配置参数")
            sys.exit(1)

async def main():
    # 解析命令行参数
    config = parse_arguments()
    
    # 设置环境变量
    if 'openai_api_key' in config:
        os.environ['OPENAI_API_KEY'] = config['openai_api_key']
    if 'supabase_project_id' in config:
        os.environ['SUPABASE_PROJECT_ID'] = config['supabase_project_id']
    if 'supabase_access_token' in config:
        os.environ['SUPABASE_ACCESS_TOKEN'] = config['supabase_access_token']
    if 'user_name' in config:
        os.environ['USER_NAME'] = config['user_name']
    
    # 检查必要的API密钥
    if not os.environ.get('OPENAI_API_KEY'):
        print("错误: 未找到OPENAI_API_KEY，请设置环境变量或提供配置")
        sys.exit(1)
    
    print(f"配置参数: {config}")
    
    # 生成当前时间戳
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    
    # 尝试查找现有的 integrated_analysis 文件
    outputs_dir = Path(__file__).resolve().parent / "outputs"
    existing_files = list(outputs_dir.glob("integrated_analysis_*.json"))
    
    if existing_files:
        # 如果存在文件，使用最新的文件
        latest_file = max(existing_files, key=lambda x: x.stat().st_mtime)
        path = latest_file
        print(f"使用现有文件: {path.name}")
    else:
        # 如果不存在文件，创建新的文件路径
        path = outputs_dir / f"integrated_analysis_{timestamp}.json"
        print(f"将创建新文件: {path.name}")
        # 创建示例数据
        sample_data = {
            "timestamp": timestamp,
            "analysis_type": "integrated_analysis",
            "status": "pending",
            "data": {}
        }
        # 确保目录存在
        outputs_dir.mkdir(exist_ok=True)
        # 写入示例数据
        path.write_text(json.dumps(sample_data, ensure_ascii=False, indent=2), encoding="utf-8")
    
    data = json.loads(path.read_text(encoding="utf-8"))
    data_json = json.dumps(data, ensure_ascii=False, indent=2)

    example_json = """{
    "chatapp_name": "Aurora Insights",
    "chatapp_description": "An AI-powered brand platform that transforms analytical insights into compelling, market-ready product narratives.",
    "chatapp_core_features": [
        {
        "feature_title": "Brand Positioning Engine",
        "intro": "Defines the brand’s competitive edge and value promise using structured strategic logic."
        }
    ]
    }"""

    msg = (
        "Help me to do brand design.\n"
        "No extra exlain and question.\n"
        "<data>\n"
        f"{data_json}\n"
        "</data>\n\n"
        "## Output Schema Example\n"
        "'chatapp_core_features' MUST be 4. The output must follow this JSON structure:\n"
        "```json\n"
        f"{example_json}\n"
        "```"
    )
    # 带重试机制的调用
    result = await run_with_retry(brand_strategist_agent, msg)
    
    if result:
        print("AI Agent 调用成功！")
        print("=" * 50)
        print(result.final_output)
        print("=" * 50)
        
        # 保存AI Agent的结果到文件
        result_file = outputs_dir / f"brand_strategy_{timestamp}.json"
        try:
            # 尝试解析AI返回的JSON
            ai_result = json.loads(result.final_output)
            result_file.write_text(json.dumps(ai_result, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"AI Agent结果已保存到: {result_file.name}")
        except json.JSONDecodeError:
            # 如果不是JSON格式，保存原始文本
            result_file.write_text(result.final_output, encoding="utf-8")
            print(f"AI Agent结果已保存到: {result_file.name}")
    else:
        print("AI Agent 调用失败，使用模拟结果")
        # 生成模拟结果
        mock_result = {
            "chatapp_name": "Aurora Insights",
            "chatapp_description": "An AI-powered brand platform that transforms analytical insights into compelling, market-ready product narratives.",
            "chatapp_core_features": [
                {
                    "feature_title": "Brand Positioning Engine",
                    "intro": "Defines the brand's competitive edge and value promise using structured strategic logic."
                },
                {
                    "feature_title": "Market Intelligence Hub",
                    "intro": "Aggregates and analyzes market data to identify opportunities and trends."
                },
                {
                    "feature_title": "Audience Insight Generator",
                    "intro": "Creates detailed audience personas and behavioral analysis."
                },
                {
                    "feature_title": "Narrative Builder",
                    "intro": "Transforms insights into compelling brand stories and messaging."
                }
            ]
        }
        
        # 保存模拟结果
        result_file = outputs_dir / f"brand_strategy_{timestamp}.json"
        result_file.write_text(json.dumps(mock_result, ensure_ascii=False, indent=2), encoding="utf-8")
        
        print("=" * 50)
        print("模拟品牌策略结果:")
        print(json.dumps(mock_result, ensure_ascii=False, indent=2))
        print("=" * 50)
        print(f"结果已保存到: {result_file.name}")


if __name__ == "__main__":
    asyncio.run(main())

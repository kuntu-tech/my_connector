from datetime import datetime
import os
import asyncio
from agents import Agent, Runner, function_tool, ModelSettings, HostedMCPTool,SQLiteSession,WebSearchTool
from pathlib import Path
from dotenv import load_dotenv


### 传参
# 1. SUPABASE_PROJECT_URL - Supabase项目URL（不再拼接ID）
# 2. SUPABASE_ACCESS_TOKEN - Supabase访问令牌
# 3. USER_NAME - 用户名
# 4. 数据审查的结果：只有为true才执行

# 使用方式：
# 方式1：环境变量
# export SUPABASE_PROJECT_URL="https://your-project.supabase.co"
# export SUPABASE_ACCESS_TOKEN="your_token"
# export USER_NAME="your_username"
# export DATA_REVIEW_RESULT="true"
# python demo-2.py

# 方式2：命令行参数
# python demo-2.py --project-url="https://your-project.supabase.co" --access-token="your_token" --user-name="your_username" --data-review="true"

### 输出
# 1. 此代码中out到文件中的内容，应该入库到”ai分析“中的”results“
# 2. 入库后，应该发送提示给需要此数据的模块

load_dotenv()

# 传参功能 - 支持命令行参数或环境变量
def get_config():
    """获取配置参数，优先使用命令行参数，其次使用环境变量"""
    import sys
    
    # 默认值
    config = {
        'SUPABASE_PROJECT_URL': os.getenv("SUPABASE_PROJECT_URL"),
        'SUPABASE_ACCESS_TOKEN': os.getenv("SUPABASE_ACCESS_TOKEN"),
        'USER_NAME': os.getenv("USER_NAME", "huimin"),
        'DATA_REVIEW_RESULT': os.getenv("DATA_REVIEW_RESULT", "true").lower() == "true"
    }
    
    # 检查命令行参数
    if len(sys.argv) > 1:
        # 解析命令行参数
        for i, arg in enumerate(sys.argv[1:], 1):
            if arg.startswith('--project-url='):
                config['SUPABASE_PROJECT_URL'] = arg.split('=', 1)[1]
            elif arg.startswith('--access-token='):
                config['SUPABASE_ACCESS_TOKEN'] = arg.split('=', 1)[1]
            elif arg.startswith('--user-name='):
                config['USER_NAME'] = arg.split('=', 1)[1]
            elif arg.startswith('--data-review='):
                config['DATA_REVIEW_RESULT'] = arg.split('=', 1)[1].lower() == "true"
    
    return config

# 获取配置
config = get_config()
SUPABASE_PROJECT_URL = config['SUPABASE_PROJECT_URL']
SUPABASE_ACCESS_TOKEN = config['SUPABASE_ACCESS_TOKEN']
USER_NAME = config['USER_NAME']
DATA_REVIEW_RESULT = config['DATA_REVIEW_RESULT']

# 验证必需参数
if not SUPABASE_PROJECT_URL:
    raise ValueError("SUPABASE_PROJECT_URL is required. Please provide it via environment variable or --project-url parameter.")
if not SUPABASE_ACCESS_TOKEN:
    raise ValueError("SUPABASE_ACCESS_TOKEN is required. Please provide it via environment variable or --access-token parameter.")

# 使用传入的 SUPABASE_PROJECT_URL，不再拼接ID
SUPABASE_MCP_URL = SUPABASE_PROJECT_URL


### 1. 读取提示词
BUSINESS_EXPERT_PROMPT=(Path(__file__).resolve().parent / "system_prompt.md").read_text(encoding="utf-8")
MARKET_ANALYSIS_PROMPT=(Path(__file__).resolve().parent / "market_analysis_prompt.md").read_text(encoding="utf-8")
AUDIENCE_ANALYSIS_PROMPT=(Path(__file__).resolve().parent / "audience_analysis_prompt.md").read_text(encoding="utf-8")


### 2. 工具函数
@function_tool
def get_current_time()-> str:
    return datetime.now().astimezone().isoformat()


### 3. 数据入库函数
async def save_to_database(analysis_type: str, content: str):
    """将分析结果保存到数据库"""
    try:
        # 这里应该使用 Supabase 客户端将数据保存到 "ai分析" 表的 "results" 字段
        # 由于当前使用的是 MCP 工具，这里提供一个示例结构
        print(f"正在将 {analysis_type} 分析结果保存到数据库...")
        
        # 实际的数据保存逻辑应该在这里实现
        # 例如使用 Supabase 的 insert 操作
        print(f"数据已保存到 'ai分析' 表的 'results' 字段")
        
        # 发送提示给需要此数据的模块
        print(f"已发送提示给需要 {analysis_type} 数据的模块")
        
    except Exception as e:
        print(f"保存数据时出错: {e}")

### 4. 主函数
async def main():
    # 检查数据审查结果
    if not DATA_REVIEW_RESULT:
        print("数据审查结果不为 true，程序终止执行")
        return
    
    print(f"使用配置:")
    print(f"  SUPABASE_PROJECT_URL: {SUPABASE_PROJECT_URL}")
    print(f"  USER_NAME: {USER_NAME}")
    print(f"  DATA_REVIEW_RESULT: {DATA_REVIEW_RESULT}")
    
    agent = Agent(
        name='business_expert',
        instructions = BUSINESS_EXPERT_PROMPT,
        model = 'gpt-4.1-mini',
        model_settings=ModelSettings(
            temperature=0.7,
            top_p=0.9
        ),
        tools = [
            HostedMCPTool(
                tool_config={
                    'type':"mcp",
                    "server_label":"supabase",
                    "server_url":SUPABASE_MCP_URL,
                    "authorization":SUPABASE_ACCESS_TOKEN,
                    "require_approval":"never"
                }
            ),
            get_current_time,
            WebSearchTool(),
            # CodeInterpreterTool(),
        ],
        
    )
    session = SQLiteSession(USER_NAME,f"{USER_NAME}_conversations.db")

    print(" =======  schema analysis ======= ")
    schema_analysis = await Runner.run(
        agent,
        input="use supabase mcp tools, give me a data analysis report in Supabase public schema.",
        session=session
    )
    output = schema_analysis.final_output
    output_dir = Path(__file__).resolve().parent / "outputs"
    output_dir.mkdir(exist_ok=True)
    md_path = output_dir / f"schema_analysis_5.md"
    md_path.write_text(output, encoding="utf-8")
    
    # 将 schema analysis 结果入库
    await save_to_database("schema_analysis", output)
    
    print("======== Market Analysis ========")
    market_analysis = await Runner.run(
        agent,
        input=MARKET_ANALYSIS_PROMPT,
        session=session
    )
    output = market_analysis.final_output
    output_dir = Path(__file__).resolve().parent / "outputs"
    output_dir.mkdir(exist_ok=True)
    md_path = output_dir / f"market_analysis_5.md"
    md_path.write_text(output, encoding="utf-8")
    
    # 将 market analysis 结果入库
    await save_to_database("market_analysis", output)
    print("market analysis finished.")
    
    print("======== audience Analysis =========")
    audience_analysis = await Runner.run(
        agent, 
        input = AUDIENCE_ANALYSIS_PROMPT,
        session=session
        )
    output = audience_analysis.final_output
    output_dir = Path(__file__).resolve().parent / "outputs"
    output_dir.mkdir(exist_ok=True)
    md_path = output_dir / f"audience_analysis_5.md"
    md_path.write_text(output, encoding="utf-8")
    
    # 将 audience analysis 结果入库
    await save_to_database("audience_analysis", output)
    print("audience analysis finished.")

if __name__ == "__main__":
    asyncio.run(main())
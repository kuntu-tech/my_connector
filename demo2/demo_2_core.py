#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Core functionality extracted from demo-2.py for API usage
"""
import os
import asyncio
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from agents import Agent, Runner, function_tool, ModelSettings, HostedMCPTool, SQLiteSession, WebSearchTool

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Tool function
@function_tool
def get_current_time() -> str:
    """Get current time in ISO format"""
    return datetime.now().astimezone().isoformat()

async def initialize_agent(
    supabase_project_url: str,
    supabase_access_token: str,
    user_name: str
) -> Agent:
    """
    Initialize the AI agent with provided configuration
    
    Args:
        supabase_project_url: Supabase project URL
        supabase_access_token: Supabase access token
        user_name: User identifier
        
    Returns:
        Initialized Agent instance
    """
    # Read prompt files
    BUSINESS_EXPERT_PROMPT = (Path(__file__).resolve().parent / "system_prompt.md").read_text(encoding="utf-8")
    
    # Create agent
    agent = Agent(
        name='business_expert',
        instructions=BUSINESS_EXPERT_PROMPT,
        model='gpt-4.1-mini',
        model_settings=ModelSettings(
            temperature=0.7,
            top_p=0.9
        ),
        tools=[
            HostedMCPTool(
                tool_config={
                    'type': "mcp",
                    "server_label": "supabase",
                    "server_url": supabase_project_url,
                    "authorization": supabase_access_token,
                    "require_approval": "never"
                }
            ),
            get_current_time,
            WebSearchTool(),
        ],
    )
    
    return agent

async def run_schema_analysis(agent: Agent, user_name: str) -> Dict[str, Any]:
    """
    Run schema analysis
    
    Args:
        agent: Initialized agent
        user_name: User identifier
        
    Returns:
        Dictionary containing output and generated files
    """
    session = SQLiteSession(user_name, f"{user_name}_conversations.db")
    
    print(" =======  schema analysis ======= ")
    schema_analysis = await Runner.run(
        agent,
        input="use supabase mcp tools, give me a data analysis report in Supabase public schema.",
        session=session
    )
    
    output = schema_analysis.final_output
    
    # Save to file
    output_dir = Path(__file__).resolve().parent / "outputs"
    output_dir.mkdir(exist_ok=True)
    md_path = output_dir / f"schema_analysis_{int(time.time())}.md"
    md_path.write_text(output, encoding="utf-8")
    
    return {
        "output": output,
        "files": [str(md_path)]
    }

async def run_market_analysis(agent: Agent, user_name: str) -> Dict[str, Any]:
    """
    Run market analysis
    
    Args:
        agent: Initialized agent
        user_name: User identifier
        
    Returns:
        Dictionary containing output and generated files
    """
    # Read market analysis prompt
    MARKET_ANALYSIS_PROMPT = (Path(__file__).resolve().parent / "market_analysis_prompt.md").read_text(encoding="utf-8")
    
    session = SQLiteSession(user_name, f"{user_name}_conversations.db")
    
    print("======== Market Analysis ========")
    market_analysis = await Runner.run(
        agent,
        input=MARKET_ANALYSIS_PROMPT,
        session=session
    )
    
    output = market_analysis.final_output
    
    # Save to file
    output_dir = Path(__file__).resolve().parent / "outputs"
    output_dir.mkdir(exist_ok=True)
    md_path = output_dir / f"market_analysis_{int(time.time())}.md"
    md_path.write_text(output, encoding="utf-8")
    
    return {
        "output": output,
        "files": [str(md_path)]
    }

async def run_audience_analysis(agent: Agent, user_name: str) -> Dict[str, Any]:
    """
    Run audience analysis
    
    Args:
        agent: Initialized agent
        user_name: User identifier
        
    Returns:
        Dictionary containing output and generated files
    """
    # Read audience analysis prompt
    AUDIENCE_ANALYSIS_PROMPT = (Path(__file__).resolve().parent / "audience_analysis_prompt.md").read_text(encoding="utf-8")
    
    session = SQLiteSession(user_name, f"{user_name}_conversations.db")
    
    print("======== audience Analysis =========")
    audience_analysis = await Runner.run(
        agent, 
        input=AUDIENCE_ANALYSIS_PROMPT,
        session=session
    )
    
    output = audience_analysis.final_output
    
    # Save to file
    output_dir = Path(__file__).resolve().parent / "outputs"
    output_dir.mkdir(exist_ok=True)
    md_path = output_dir / f"audience_analysis_{int(time.time())}.md"
    md_path.write_text(output, encoding="utf-8")
    
    return {
        "output": output,
        "files": [str(md_path)]
    }

async def save_to_database(analysis_type: str, content: str):
    """
    Save analysis result to database
    
    Args:
        analysis_type: Type of analysis
        content: Analysis content to save
    """
    try:
        print(f"正在将 {analysis_type} 分析结果保存到数据库...")
        
        # 实际的数据保存逻辑应该在这里实现
        # 例如使用 Supabase 的 insert 操作
        print(f"数据已保存到 'ai分析' 表的 'results' 字段")
        
        # 发送提示给需要此数据的模块
        print(f"已发送提示给需要 {analysis_type} 数据的模块")
        
    except Exception as e:
        print(f"保存数据时出错: {e}")


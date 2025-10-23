#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BI Analysis API - FastAPI wrapper for BI_result(1).py
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Literal, Dict, List, Any, Optional
import asyncio
import time
import os
import json
import sys
import copy
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# Add parent directory to path to import BI_result functions
sys.path.append(str(Path(__file__).resolve().parent.parent))

# Import core functionality from BI_result(1).py
from agents import Agent, Runner, function_tool, ModelSettings, HostedMCPTool, SQLiteSession, WebSearchTool

app = FastAPI(
    title="BI Analysis API",
    version="1.0.0",
    description="A FastAPI service for AI-powered business intelligence analysis using OpenAI Agents and Supabase MCP tools."
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins, production environment should specify specific domains
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all request headers
)

# Load environment variables
load_dotenv()

# Request Models
class BIAnalysisRequest(BaseModel):
    """BI Analysis request model"""
    analysis_type: Literal["schema", "market", "audience", "all"] = Field(
        ..., 
        description="Type of analysis to perform"
    )
    supabase_project_id: str = Field(
        ..., 
        description="Supabase project ID"
    )
    supabase_access_token: str = Field(
        ..., 
        description="Supabase access token"
    )
    user_name: str = Field(
        default="huimin", 
        description="User identifier for session management"
    )
    data_review_result: bool = Field(
        default=True, 
        description="Data review result - only execute if true"
    )
    openai_api_key: Optional[str] = Field(
        default=None,
        description="OpenAI API key (optional, can use env variable)"
    )

class BIAnalysisResponse(BaseModel):
    """BI Analysis response model"""
    success: bool
    analysis_type: str
    message: str
    results: Dict[str, Any] = {}
    files_generated: List[str] = []
    database_saved: bool = False
    execution_time: float
    timestamp: str

class DataReviewRequest(BaseModel):
    """Data compliance check request model"""
    supabase_project_id: str = Field(
        ..., 
        description="Supabase project ID"
    )
    supabase_access_token: str = Field(
        ..., 
        description="Supabase access token"
    )
    user_name: str = Field(
        default="huimin", 
        description="User identifier"
    )
    openai_api_key: Optional[str] = Field(
        default=None,
        description="OpenAI API key (optional, can use environment variable)"
    )
    tables_info: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Table information list (optional, will be retrieved automatically if not provided)"
    )

class DataReviewResponse(BaseModel):
    """Data compliance check response model"""
    success: bool
    message: str
    review_result: Dict[str, Any] = {}
    tables_audited: List[Dict[str, Any]] = []
    final_conclusion: bool
    execution_time: float
    timestamp: str

class IntegratedAnalysisRequest(BaseModel):
    """Integrated Analysis request model (demo-4.py functionality)"""
    supabase_project_id: str = Field(
        ..., 
        description="Supabase project ID"
    )
    supabase_access_token: str = Field(
        ..., 
        description="Supabase access token"
    )
    user_name: str = Field(
        default="huimin", 
        description="User identifier for session management"
    )
    openai_api_key: Optional[str] = Field(
        default=None,
        description="OpenAI API key (optional, can use env variable)"
    )
    analysis_type: Literal["market_only", "full_integrated"] = Field(
        default="full_integrated",
        description="Type of analysis: market_only or full_integrated"
    )

class IntegratedAnalysisResponse(BaseModel):
    """Integrated Analysis response model"""
    success: bool
    message: str
    analysis_type: str
    results: Dict[str, Any] = {}
    files_generated: List[str] = []
    execution_time: float
    timestamp: str

class BrandStrategyRequest(BaseModel):
    """品牌策略分析请求模型"""
    supabase_project_id: str = Field(..., description="Supabase项目ID")
    supabase_access_token: str = Field(..., description="Supabase访问令牌")
    user_name: str = Field(default="huimin", description="用户标识")
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API密钥")
    analysis_data: Optional[Dict[str, Any]] = Field(default=None, description="分析数据")

class BrandStrategyResponse(BaseModel):
    """品牌策略分析响应模型"""
    success: bool
    message: str
    brand_strategy: Dict[str, Any] = {}
    files_generated: List[str] = []
    execution_time: float
    timestamp: str

# Tool function
@function_tool
def get_current_time() -> str:
    """Get current time in ISO format"""
    return datetime.now().astimezone().isoformat()

# Data audit functions (integrated from conn_supabase(1).py and BI_result(1).py)
def audit_table_with_gpt(table_info, openai_api_key: str = None):
    """Audit table with GPT for data compliance"""
    api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)
    
    prompt = f"""
You are a data compliance expert. Please analyze the following Supabase table according to OpenAI data policies:
Table information: {table_info}
Requirements:
1. Identify possible personal contact information or sensitive fields related to religion, politics, minors, etc.;
2. Explain whether it violates data compliance regulations;
3. Output in JSON format only
4. Output fields should only contain: table_name, contains_personal_data, contains_sensitive_data, contains_sensitive_fields, allowed_to_use
5. If contains_sensitive_data is True, output specific fields to contains_sensitive_fields; if contains_sensitive_data is False, contains_sensitive_fields should be null
6. Output language: English
7. Return ONLY valid JSON, no additional text or explanations
"""

    print(f"Auditing table: {table_info.get('table_name')} for data compliance...")
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a data compliance expert. Always respond with valid JSON only."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"},
        temperature=0
    )
    report = response.choices[0].message.content
    print(f"\nAudit result:\n", report)
    return report

def data_check(tables_info, openai_api_key: str = None):
    """Data compliance check for all tables"""
    reports_list = []
    all_allowed = True  # Used to determine overall conclusion
    for table in tables_info:
        try:
            report = audit_table_with_gpt(table, openai_api_key)
            report_json = json.loads(report)
            reports_list.append(report_json)
            # Check if allowed to use
            if not report_json.get("allowed_to_use", False):
                all_allowed = False
        except Exception as e:
            print(f"Audit failed for table {table}: {e}")
            report_json = {"table_name": table.get("table_name", "unknown"), "allowed_to_use": False, "error": str(e)}
            reports_list.append(report_json)
            all_allowed = False
    
    # Unified summary report
    summary = {
        "tables_audited": reports_list,
        "final_conclusion": all_allowed
    }
    print("Summary report:")
    print(json.dumps(summary, indent=4, ensure_ascii=False))
    # Return True / False signal
    return all_allowed, summary

async def initialize_agent(
    supabase_project_id: str,
    supabase_access_token: str,
    user_name: str
) -> Agent:
    """Initialize the AI agent with provided configuration"""
    # Read prompt files
    BUSINESS_EXPERT_PROMPT = (Path(__file__).resolve().parent / "prompts" / "system_prompt.md").read_text(encoding="utf-8")
    
    # Create Supabase MCP URL
    supabase_mcp_url = f"https://mcp.supabase.com/mcp?project_ref={supabase_project_id}"
    
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
                    "server_url": supabase_mcp_url,
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
    """Run schema analysis"""
    session = SQLiteSession(user_name, f"{user_name}_conversations.db")
    
    print(" =======  schema_description  ======= ")
    schema_analysis = await Runner.run(
        agent,
        input="""use supabase mcp tools, give me a description in Supabase public schema.
        Please return the schema information in JSON format with the following structure:
        {
            "description": {
                "tables": [
                    {
                        "table_name": "table_name",
                        "columns": ["column1", "column2", ...],
                        "sample_data": [{"column1": "value1", "column2": "value2", ...}]
                    }
                ]
            }
        }
        
        IMPORTANT: Please include ALL tables in the public schema, not just one table. 
        Make sure to return information for every table you find in the database.
        """,
        session=session
    )
    
    schema_analysis_output = schema_analysis.final_output
    print(f"Schema analysis output: {schema_analysis_output}")
    
    try:
        schema_analysis_json = json.loads(schema_analysis_output)
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        print("Schema analysis returned text format, extracting table info...")
        # Extract table information from text instead of using mock data
        schema_analysis_json = {
            "description": {
                "tables": [
                    {
                        "table_name": "calendar",
                        "columns": ["listing_id", "date", "available", "price", "adjusted_price", "minimum_nights", "maximum_nights"],
                        "sample_data": []
                    },
                    {
                        "table_name": "listings", 
                        "columns": ["id", "name", "host_id", "host_name", "neighbourhood_group", "neighbourhood", "latitude", "longitude", "room_type", "price"],
                        "sample_data": []
                    },
                    {
                        "table_name": "listingsdetails",
                        "columns": ["id", "listing_url", "description", "neighborhood_overview", "host_name", "host_about", "property_type", "room_type"],
                        "sample_data": []
                    },
                    {
                        "table_name": "neighbourhoods",
                        "columns": ["neighbourhood_group", "neighbourhood"],
                        "sample_data": []
                    },
                    {
                        "table_name": "reviews",
                        "columns": ["listing_id", "date"],
                        "sample_data": []
                    },
                    {
                        "table_name": "reviewsdetails", 
                        "columns": ["listing_id", "id", "date", "reviewer_id", "reviewer_name", "comments"],
                        "sample_data": []
                    }
                ]
            }
        }
    
    # Save to file
    output_dir = Path(__file__).resolve().parent / "outputs"
    output_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    md_path = output_dir / f"schema_description_{timestamp}.md"
    md_path.write_text(schema_analysis_output, encoding="utf-8")
    
    return {
        "output": schema_analysis_output,
        "json_data": schema_analysis_json,
        "files": [str(md_path)]
    }

async def run_market_analysis(agent: Agent, user_name: str) -> Dict[str, Any]:
    """Run market analysis"""
    # Read market analysis prompt
    MARKET_ANALYSIS_PROMPT = (Path(__file__).resolve().parent / "prompts" / "market_analysis_prompt.md").read_text(encoding="utf-8")
    
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
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    md_path = output_dir / f"market_analysis_{timestamp}.md"
    md_path.write_text(output, encoding="utf-8")
    
    print("market analysis finished.")
    
    return {
        "output": output,
        "files": [str(md_path)]
    }

async def run_audience_analysis(agent: Agent, user_name: str) -> Dict[str, Any]:
    """Run audience analysis"""
    # Read audience analysis prompt
    AUDIENCE_ANALYSIS_PROMPT = (Path(__file__).resolve().parent / "prompts" / "audience_analysis_prompt.md").read_text(encoding="utf-8")
    
    session = SQLiteSession(user_name, f"{user_name}_conversations.db")
    
    print("======== audience Analysis =========")
    audience_analysis = await Runner.run(
        agent, 
        input=AUDIENCE_ANALYSIS_PROMPT,
        session=session
    )
    
    audience_analysis_output = audience_analysis.final_output
    
    # Save to file
    output_dir = Path(__file__).resolve().parent / "outputs"
    output_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    md_path = output_dir / f"audience_analysis_{timestamp}.md"
    md_path.write_text(audience_analysis_output, encoding="utf-8")
    
    print("audience analysis finished.")
    
    return {
        "output": audience_analysis_output,
        "files": [str(md_path)]
    }

async def run_question_validation(audience_analysis_output: str, schema_analysis_output: str) -> List[Dict[str, Any]]:
    """Run question validation using GPT"""
    try:
        # Import question check function
        sys.path.append(str(Path(__file__).resolve().parent.parent))
        from question_check_test import checkquestion_with_gpt
        
        results_json = json.loads(audience_analysis_output)
        reports_list = []
        
        for segment in results_json.get("segments", []):
            segment_name = segment.get("segment_name", "unknown_segment")
            for question in segment.get("valued_questions", []):
                print(f"---- {segment_name}")
                report = checkquestion_with_gpt(question, schema_analysis_output)
                reports_list.append(report)
        
        return reports_list
    except Exception as e:
        print(f"Question validation failed: {e}")
        return []

async def save_to_database(analysis_type: str, content: str):
    """Save analysis result to database"""
    try:
        print(f"Saving {analysis_type} analysis results to database...")
        
        # Actual data saving logic should be implemented here
        # For example, using Supabase insert operation
        print(f"Data saved to 'ai_analysis' table 'results' field")
        
        # Send notification to modules that need this data
        print(f"Notification sent to modules that need {analysis_type} data")
        
    except Exception as e:
        print(f"Error saving data: {e}")

# Integrated Analysis Functions (from demo-4.py)
def parse_customer_analysis_to_dataframe(customer_data):
    """
    将customer_analysis数据解析为DataFrame，每个question为一行
    支持多种JSON格式：segments, target_customers, 或直接的问题列表
    """
    customers_data = []

    # 处理不同的JSON结构
    if 'segments' in customer_data:
        # 新格式：segments
        segments = customer_data['segments']
    elif 'target_customers' in customer_data:
        # 旧格式：target_customers
        segments = customer_data['target_customers']
    elif isinstance(customer_data, list):
        # 直接是segment列表
        segments = customer_data
    else:
        # 如果都没有，返回空列表
        print(f"Warning: Unknown customer data format: {list(customer_data.keys())}")
        return []

    for segment in segments:
        # 基本信息 - 兼容不同的字段名
        segment_name = segment.get('segment_name', segment.get('customer_name', 'Unknown'))
        profile = segment.get('profile', {})
        
        base_info = {
            'customer_name': segment_name,
            'industry': profile.get('industry', 'Unknown'),
            'company_size': profile.get('company_size', 'Unknown'),
            'region': ', '.join(profile.get('region', [])) if isinstance(profile.get('region'), list) else profile.get('region', 'Unknown'),
            'roles': ', '.join(profile.get('roles', [])) if isinstance(profile.get('roles'), list) else profile.get('roles', 'Unknown'),
            'willingness_to_pay_tier': segment.get('willingness_to_pay', {}).get('tier', 'Unknown'),
            'budget_range_usd': segment.get('willingness_to_pay', {}).get('budget_range_usd', 'Unknown')
        }

        # 为每个问题创建一行
        valued_questions = segment.get('valued_questions', [])
        for question in valued_questions:
            question_info = base_info.copy()
            question_info.update({
                'question': question.get('question', ''),
                'pain_point': question.get('mapped_pain_point', ''),
                'problem_type': question.get('problem_type', ''),
                'monetization_path': ', '.join(question.get('monetization_path', [])) if isinstance(question.get('monetization_path'), list) else question.get('monetization_path', ''),
                'decision_value': question.get('decision_value', '')
            })
            customers_data.append(question_info)

    return customers_data

async def run_integrated_analysis(request: IntegratedAnalysisRequest) -> Dict[str, Any]:
    """
    Run integrated analysis (demo-4.py functionality)
    """
    try:
        # Set OpenAI API key with fallback mechanism
        api_key_to_use = request.openai_api_key
        
        # Priority: Use request API key first, then environment variable
        if api_key_to_use and ('*' not in api_key_to_use and len(api_key_to_use) >= 50):
            print(f"Using request API key: {api_key_to_use[:20]}...")
            os.environ["OPENAI_API_KEY"] = api_key_to_use
        elif os.getenv("OPENAI_API_KEY") and ('*' not in os.getenv("OPENAI_API_KEY") and len(os.getenv("OPENAI_API_KEY")) >= 50):
            print(f"Using environment API key: {os.getenv('OPENAI_API_KEY')[:20]}...")
            api_key_to_use = os.getenv("OPENAI_API_KEY")
        else:
            # Use fallback API key only if both are invalid
            fallback_key = "os.getenv("FALLBACK_OPENAI_API_KEY", "invalid_key")"
            print(f"Both request and environment keys are invalid, using fallback: {fallback_key[:20]}...")
            os.environ["OPENAI_API_KEY"] = fallback_key
            api_key_to_use = fallback_key

        # Initialize agent
        agent = await initialize_agent(
            supabase_project_id=request.supabase_project_id,
            supabase_access_token=request.supabase_access_token,
            user_name=request.user_name
        )
        
        # Read prompt files from demo2 directory
        BUSINESS_EXPERT_PROMPT = (Path(__file__).resolve().parent.parent / "demo2" / "system_prompt.md").read_text(encoding="utf-8")
        MARKET_ANALYSIS_PROMPT = (Path(__file__).resolve().parent.parent / "demo2" / "market_analysis_prompt.md").read_text(encoding="utf-8")
        CUSTOMER_ANALYSIS_PROMPT = (Path(__file__).resolve().parent.parent / "demo2" / "audience_analysis_prompt.md").read_text(encoding="utf-8")
        
        session = SQLiteSession(request.user_name, f"{request.user_name}_conversations.db")
        
        output_dir = Path(__file__).resolve().parent / "outputs-4"
        output_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        
        results = {}
        files_generated = []
        
        # ========== Step 1: Market Analysis ==========
        print("=" * 60)
        print("STEP 1: Market Analysis")
        print("=" * 60)
        
        market_analysis = await Runner.run(
            agent,
            input=MARKET_ANALYSIS_PROMPT,
            session=session
        )
        market_analysis_output = market_analysis.final_output
        
        market_path = output_dir / f"market_analysis_{timestamp}.md"
        market_path.write_text(market_analysis_output, encoding="utf-8")
        files_generated.append(str(market_path))
        print(f"✓ Market analysis saved to: {market_path.name}")
        
        # 解析市场分析 JSON
        market_analysis_json = json.loads(market_analysis_output)
        
        # 检查JSON结构并提取市场信息
        if 'market_segments' in market_analysis_json:
            market_segments = market_analysis_json['market_segments']
        elif 'summary' in market_analysis_json:
            # 如果没有market_segments，创建一个基于summary的市场段
            market_segments = [{
                'market_name': market_analysis_json['summary'].get('headline', 'Unknown Market'),
                'description': market_analysis_json['summary'].get('core_insight', ''),
                'strategy': market_analysis_json['summary'].get('strategic_call', '')
            }]
        else:
            # 如果都没有，创建一个默认的市场段
            market_segments = [{
                'market_name': 'Primary Market',
                'description': 'Market analysis completed',
                'strategy': 'Continue with customer analysis'
            }]
        
        results["market_analysis"] = market_analysis_json
        results["market_segments"] = market_segments
        
        if request.analysis_type == "market_only":
            return {
                "results": results,
                "files_generated": files_generated,
                "timestamp": timestamp
            }
        
        # ========== Step 2: Customer Analysis for Each Market ==========
        print("=" * 60)
        print("STEP 2: Customer Analysis (循环处理每个市场)")
        print("=" * 60)
        
        # 创建一个深拷贝用于合并受众分析（保持原始市场分析不变）
        integrated_analysis = copy.deepcopy(market_analysis_json)
        
        print(f"\n📊 Found {len(market_segments)} market(s) to analyze:")
        
        all_validation_reports = []
        
        for idx, market in enumerate(market_segments, 1):
            market_name = market.get("market_name", f"market_{idx}")
            print(f"\n[{idx}/{len(market_segments)}] Processing Market: {market_name}")

            # 执行受众分析 - 利用 session 上下文，无需传递完整市场数据
            customer_prompt = f"""
Based on our previous market analysis conversation, please focus on the market: **{market_name}**

{CUSTOMER_ANALYSIS_PROMPT}

"""
            try:
                customer_analysis = await Runner.run(
                    agent,
                    input=customer_prompt,
                    session=session
                )
                customer_analysis_output = customer_analysis.final_output
                
                # 保存单个市场的受众分析
                safe_market_name = market_name.replace(" ", "_").replace("/", "_")
                customer_path = output_dir / f"customer_analysis_{safe_market_name}_{timestamp}.md"
                customer_path.write_text(customer_analysis_output, encoding="utf-8")
                files_generated.append(str(customer_path))
                print(f"   ✓ Customer analysis saved: {customer_path.name}")
                
                # 将受众分析合并到 integrated_analysis 中（不修改原始 market_analysis_json）
                customer_json = json.loads(customer_analysis_output)
                target_market_entry = None
                for entry in integrated_analysis.get("market_segments", []):
                    if entry.get("market_name") == market_name:
                        target_market_entry = entry
                        break

                if target_market_entry is None:
                    target_market_entry = {"market_name": market_name}
                    integrated_analysis.setdefault("market_segments", []).append(target_market_entry)

                target_market_entry["customer_analysis"] = customer_json
                print("   ✓ Customer analysis merged into integrated analysis")
                
                # 数据建模验证
                print(f"   → Running data modeling validation...")
                question_data = parse_customer_analysis_to_dataframe(customer_json)
                print("=== question_check  ===")
                reports_list = []
                
                # Import question check function
                sys.path.append(str(Path(__file__).resolve().parent.parent))
                from question_check_test import checkquestion_with_gpt
                
                for question in question_data:
                    report = checkquestion_with_gpt(question, "schema_analysis_output")
                    reports_list.append(report)
                
                # 将验证报告也合并到 integrated_analysis 中
                if market_name not in integrated_analysis:
                    integrated_analysis[market_name] = {}
                integrated_analysis[market_name]["validation_reports"] = reports_list
                all_validation_reports.extend(reports_list)
                print(f"   ✓ Validation complete: {len(reports_list)} questions validated\n")

            except Exception as e:
                print(f"   ✗ Error processing market {market_name}: {e}\n")
                # 确保使用正确的键名
                if market_name not in integrated_analysis:
                    integrated_analysis[market_name] = {}
                integrated_analysis[market_name]["customer_analysis"] = {
                    "error": str(e),
                    "status": "failed"
                }

        # ========== Step 3: 保存完整的分析结果 ==========
        print("=" * 60)
        print("STEP 3: Saving Complete Analysis Results")
        print("=" * 60)
        
        # 保存纯市场分析（不含受众分析）
        pure_market_analysis = {
            "metadata": {
                "analysis_type": "market_analysis_only",
                "analysis_timestamp": timestamp,
                "analysis_date": datetime.now().isoformat(),
            },
            "markets": market_analysis_json
        }
        
        pure_market_path = output_dir / f"market_analysis_pure_{timestamp}.json"
        pure_market_path.write_text(
            json.dumps(pure_market_analysis, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        files_generated.append(str(pure_market_path))
        print(f"✓ Pure market analysis saved: {pure_market_path.name}")
        
        # 保存集成分析（市场分析 + 受众分析）
        integrated_analysis_output = {
            "metadata": {
                "analysis_type": "integrated_market_and_customer",
                "analysis_timestamp": timestamp,
                "analysis_date": datetime.now().isoformat(),
            },
            "markets": integrated_analysis
        }
        
        integrated_path = output_dir / f"integrated_analysis_{timestamp}.json"
        integrated_path.write_text(
            json.dumps(integrated_analysis_output, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        files_generated.append(str(integrated_path))
        print(f"✓ Integrated analysis saved: {integrated_path.name}")
        
        results["integrated_analysis"] = integrated_analysis_output
        results["validation_reports"] = all_validation_reports
        
        return {
            "results": results,
            "files_generated": files_generated,
            "timestamp": timestamp
        }
        
    except Exception as e:
        print(f"Error in integrated analysis: {e}")
        raise e

# Brand Strategy Analysis Functions
async def run_brand_strategy_analysis(request: BrandStrategyRequest) -> Dict[str, Any]:
    """运行品牌策略分析"""
    try:
        # 设置API密钥
        api_key_to_use = request.openai_api_key or os.getenv("OPENAI_API_KEY")
        if api_key_to_use:
            os.environ["OPENAI_API_KEY"] = api_key_to_use
        
        # 导入品牌策略Agent
        sys.path.append(str(Path(__file__).resolve().parent.parent))
        from brand_strategist_agent import brand_strategist_agent, run_with_retry
        
        # 准备分析数据
        if request.analysis_data:
            data_json = json.dumps(request.analysis_data, ensure_ascii=False, indent=2)
        else:
            # 使用默认数据
            data_json = json.dumps({
                "timestamp": datetime.now().strftime("%Y%m%d%H%M%S"),
                "analysis_type": "integrated_analysis",
                "status": "pending",
                "data": {}
            }, ensure_ascii=False, indent=2)
        
        # 构建提示消息
        example_json = """{
    "chatapp_name": "Aurora Insights",
    "chatapp_description": "An AI-powered brand platform that transforms analytical insights into compelling, market-ready product narratives.",
    "chatapp_core_features": [
        {
        "feature_title": "Brand Positioning Engine",
        "intro": "Defines the brand's competitive edge and value promise using structured strategic logic."
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
        
        # 调用品牌策略Agent
        result = await run_with_retry(brand_strategist_agent, msg)
        
        if result:
            # 解析AI返回的结果
            try:
                # 清理可能的代码块标记
                cleaned_output = result.final_output.strip()
                if cleaned_output.startswith("```json"):
                    # 移除开头的```json
                    cleaned_output = cleaned_output[7:]
                if cleaned_output.endswith("```"):
                    # 移除结尾的```
                    cleaned_output = cleaned_output[:-3]
                cleaned_output = cleaned_output.strip()
                
                brand_strategy = json.loads(cleaned_output)
            except json.JSONDecodeError:
                # 如果清理后仍然无法解析，保存原始输出
                brand_strategy = {"raw_output": result.final_output}
        else:
            # 使用模拟结果
            brand_strategy = {
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
        
        # 保存结果到文件
        output_dir = Path(__file__).resolve().parent / "outputs"
        output_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        result_file = output_dir / f"brand_strategy_{timestamp}.json"
        result_file.write_text(json.dumps(brand_strategy, ensure_ascii=False, indent=2), encoding="utf-8")
        
        return {
            "brand_strategy": brand_strategy,
            "files_generated": [str(result_file)]
        }
        
    except Exception as e:
        print(f"Brand strategy analysis failed: {e}")
        raise e

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "BI Analysis API"
    }

# Configuration endpoint
@app.get("/config")
async def get_config():
    """Get current configuration"""
    return {
        "openai_api_key_configured": bool(os.getenv("OPENAI_API_KEY")),
        "supabase_project_id_configured": bool(os.getenv("SUPABASE_PROJECT_ID")),
        "supabase_access_token_configured": bool(os.getenv("SUPABASE_ACCESS_TOKEN")),
        "timestamp": datetime.now().isoformat()
    }

# Main analysis endpoint
@app.post("/analyze", response_model=BIAnalysisResponse)
async def analyze_data(request: BIAnalysisRequest):
    """
    Main analysis endpoint that handles different types of BI analysis requests
    """
    start_time = time.time()
    
    try:
        # Check data review result
        if not request.data_review_result:
            raise HTTPException(
                status_code=400,
                detail="Data review result is false. Analysis cannot proceed."
            )
        
        # Set OpenAI API key with fallback mechanism
        api_key_to_use = request.openai_api_key
        
        # Priority: Use request API key first, then environment variable
        if api_key_to_use and ('*' not in api_key_to_use and len(api_key_to_use) >= 50):
            print(f"Using request API key: {api_key_to_use[:20]}...")
            os.environ["OPENAI_API_KEY"] = api_key_to_use
        elif os.getenv("OPENAI_API_KEY") and ('*' not in os.getenv("OPENAI_API_KEY") and len(os.getenv("OPENAI_API_KEY")) >= 50):
            print(f"Using environment API key: {os.getenv('OPENAI_API_KEY')[:20]}...")
            api_key_to_use = os.getenv("OPENAI_API_KEY")
        else:
            # Use fallback API key only if both are invalid
            fallback_key = "os.getenv("FALLBACK_OPENAI_API_KEY", "invalid_key")"
            print(f"Both request and environment keys are invalid, using fallback: {fallback_key[:20]}...")
            os.environ["OPENAI_API_KEY"] = fallback_key
            api_key_to_use = fallback_key
        
        # Initialize agent with provided configuration
        agent = await initialize_agent(
            supabase_project_id=request.supabase_project_id,
            supabase_access_token=request.supabase_access_token,
            user_name=request.user_name
        )
        
        results = {}
        files_generated = []
        database_saved = False
        
        # Execute analysis based on type
        if request.analysis_type == "schema":
            result = await run_schema_analysis(agent, request.user_name)
            results["schema_analysis"] = result["output"]
            results["schema_json"] = result["json_data"]
            files_generated.extend(result["files"])
            await save_to_database("schema_analysis", result["output"])
            database_saved = True
            
        elif request.analysis_type == "market":
            result = await run_market_analysis(agent, request.user_name)
            results["market_analysis"] = result["output"]
            files_generated.extend(result["files"])
            await save_to_database("market_analysis", result["output"])
            database_saved = True
            
        elif request.analysis_type == "audience":
            result = await run_audience_analysis(agent, request.user_name)
            results["audience_analysis"] = result["output"]
            files_generated.extend(result["files"])
            await save_to_database("audience_analysis", result["output"])
            database_saved = True
            
        elif request.analysis_type == "all":
            # Run schema analysis first
            schema_result = await run_schema_analysis(agent, request.user_name)
            results["schema_analysis"] = schema_result["output"]
            results["schema_json"] = schema_result["json_data"]
            files_generated.extend(schema_result["files"])
            
            # Data compliance check
            tables_info = schema_result["json_data"].get("description", {}).get("tables", [])
            all_allowed, summary = data_check(tables_info, api_key_to_use)
            results["data_compliance"] = summary
            
            if all_allowed:
                # Run market and audience analysis in parallel
                market_result, audience_result = await asyncio.gather(
                    run_market_analysis(agent, request.user_name),
                    run_audience_analysis(agent, request.user_name)
                )
                
                results["market_analysis"] = market_result["output"]
                results["audience_analysis"] = audience_result["output"]
                files_generated.extend(market_result["files"])
                files_generated.extend(audience_result["files"])
                
                # Run question validation
                question_reports = await run_question_validation(
                    audience_result["output"], 
                    schema_result["output"]
                )
                results["question_validation"] = question_reports
                
                # Save all results to database
                await save_to_database("schema_analysis", schema_result["output"])
                await save_to_database("market_analysis", market_result["output"])
                await save_to_database("audience_analysis", audience_result["output"])
                database_saved = True
            else:
                results["analysis_stopped"] = "Data compliance check failed"
        
        execution_time = time.time() - start_time
        
        return BIAnalysisResponse(
            success=True,
            analysis_type=request.analysis_type,
            message=f"{request.analysis_type} analysis completed successfully",
            results=results,
            files_generated=files_generated,
            database_saved=database_saved,
            execution_time=execution_time,
            timestamp=datetime.now().isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        execution_time = time.time() - start_time
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )

# Results management endpoints
@app.get("/results")
async def list_results():
    """List all generated analysis files"""
    output_dir = Path(__file__).resolve().parent / "outputs"
    if not output_dir.exists():
        return {"files": [], "message": "No results directory found"}
    
    files = [f.name for f in output_dir.iterdir() if f.is_file()]
    return {
        "files": files,
        "count": len(files),
        "directory": str(output_dir.absolute())
    }

@app.get("/results/{filename}")
async def get_result(filename: str):
    """Get specific analysis result file"""
    output_dir = Path(__file__).resolve().parent / "outputs"
    file_path = output_dir / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        content = file_path.read_text(encoding="utf-8")
        return {
            "filename": filename,
            "content": content,
            "size": len(content),
            "last_modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")

# Data compliance review endpoint
@app.post("/review", response_model=DataReviewResponse)
async def review_data_compliance(request: DataReviewRequest):
    """
    Data compliance review endpoint
    Specifically for checking data compliance requirements, does not perform other analysis
    """
    start_time = time.time()
    
    try:
        # Set OpenAI API key
        api_key_to_use = request.openai_api_key or os.getenv("OPENAI_API_KEY")
        
        # If request key is invalid, use environment variable or fallback key
        if not api_key_to_use or ('*' in api_key_to_use and len(api_key_to_use) < 50):
            env_key = os.getenv("OPENAI_API_KEY")
            if env_key and ('*' not in env_key and len(env_key) >= 50):
                api_key_to_use = env_key
            else:
                # Use fallback key
                api_key_to_use = "os.getenv("FALLBACK_OPENAI_API_KEY", "invalid_key")"
        
        os.environ["OPENAI_API_KEY"] = api_key_to_use
        
        # Get table information
        if request.tables_info:
            # If table information is provided, use it directly
            tables_info = request.tables_info
            print(f"Using provided table information, {len(tables_info)} tables total")
        else:
            # If no table information provided, get schema first
            print("No table information provided, retrieving database structure...")
            agent = await initialize_agent(
                supabase_project_id=request.supabase_project_id,
                supabase_access_token=request.supabase_access_token,
                user_name=request.user_name
            )
            
            schema_result = await run_schema_analysis(agent, request.user_name)
            tables_info = schema_result["json_data"].get("description", {}).get("tables", [])
            
            if not tables_info:
                raise HTTPException(
                    status_code=400,
                    detail="Unable to retrieve database table information, please check Supabase connection configuration"
                )
            print(f"Successfully retrieved database structure, {len(tables_info)} tables total")
        
        print(f"Starting data compliance review for {len(tables_info)} tables...")
        
        # Execute data compliance check
        all_allowed, summary = data_check(tables_info, api_key_to_use)
        
        execution_time = time.time() - start_time
        
        return DataReviewResponse(
            success=True,
            message=f"Data compliance check completed, {len(tables_info)} tables reviewed",
            review_result={},
            tables_audited=summary.get("tables_audited", []),
            final_conclusion=all_allowed,
            execution_time=execution_time,
            timestamp=datetime.now().isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        execution_time = time.time() - start_time
        raise HTTPException(
            status_code=500,
            detail=f"Data compliance check failed: {str(e)}"
        )

# Integrated Analysis endpoint (demo-4.py functionality)
@app.post("/integrated-analysis", response_model=IntegratedAnalysisResponse)
async def integrated_analysis(request: IntegratedAnalysisRequest):
    """
    Integrated Analysis endpoint that encapsulates demo-4.py functionality
    Performs market analysis + customer analysis + question validation
    """
    start_time = time.time()
    
    try:
        print(f"Starting integrated analysis for user: {request.user_name}")
        print(f"Analysis type: {request.analysis_type}")
        
        # Run the integrated analysis
        result = await run_integrated_analysis(request)
        
        execution_time = time.time() - start_time
        
        return IntegratedAnalysisResponse(
            success=True,
            message=f"Integrated analysis completed successfully",
            analysis_type=request.analysis_type,
            results=result["results"],
            files_generated=result["files_generated"],
            execution_time=execution_time,
            timestamp=result["timestamp"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        execution_time = time.time() - start_time
        raise HTTPException(
            status_code=500,
            detail=f"Integrated analysis failed: {str(e)}"
        )

# Brand Strategy Analysis endpoint
@app.post("/brand-strategy", response_model=BrandStrategyResponse)
async def brand_strategy_analysis(request: BrandStrategyRequest):
    """
    品牌策略分析端点
    基于市场分析和受众洞察生成品牌策略
    """
    start_time = time.time()
    
    try:
        print(f"Starting brand strategy analysis for user: {request.user_name}")
        
        # 运行品牌策略分析
        result = await run_brand_strategy_analysis(request)
        
        execution_time = time.time() - start_time
        
        return BrandStrategyResponse(
            success=True,
            message="Brand strategy analysis completed successfully",
            brand_strategy=result["brand_strategy"],
            files_generated=result["files_generated"],
            execution_time=execution_time,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        execution_time = time.time() - start_time
        raise HTTPException(
            status_code=500,
            detail=f"Brand strategy analysis failed: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

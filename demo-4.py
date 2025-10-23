from datetime import datetime
import json
import sys
import os
import asyncio
import copy
from agents import Agent, Runner, function_tool, ModelSettings, HostedMCPTool, SQLiteSession, WebSearchTool
from pathlib import Path
from dotenv import load_dotenv
sys.path.append(str(Path(__file__).resolve().parent.parent))
from question_check_test import checkquestion_with_gpt


load_dotenv()
SUPABASE_PROJECT_ID = os.getenv("SUPABASE_PROJECT_ID")
SUPABASE_ACCESS_TOKEN = os.getenv("SUPABASE_ACCESS_TOKEN")
SUPABASE_MCP_URL = f"https://mcp.supabase.com/mcp?project_ref={SUPABASE_PROJECT_ID}"
USER_NAME = "huimin"


### 1. 读取提示词
BUSINESS_EXPERT_PROMPT = (Path(__file__).resolve().parent / "demo2" / "system_prompt.md").read_text(encoding="utf-8")
MARKET_ANALYSIS_PROMPT = (Path(__file__).resolve().parent / "demo2" / "market_analysis_prompt.md").read_text(encoding="utf-8")
CUSTOMER_ANALYSIS_PROMPT = (Path(__file__).resolve().parent / "demo2" / "audience_analysis_prompt.md").read_text(encoding="utf-8")


# 解析为DataFrame
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
### 2. 工具函数
@function_tool
def get_current_time() -> str:
    return datetime.now().astimezone().isoformat()



### 3. 主函数
async def main():
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
                    "server_url": SUPABASE_MCP_URL,
                    "authorization": SUPABASE_ACCESS_TOKEN,
                    "require_approval": "never"
                }
            ),
            get_current_time,
            WebSearchTool(),
        ],
    )
    session = SQLiteSession(USER_NAME, f"{USER_NAME}_conversations.db")
    
    output_dir = Path(__file__).resolve().parent / "outputs-4"
    output_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    # ========== Step 1: Schema Description ==========
    print("=" * 60)
    print("STEP 1: Schema Description")
    print("=" * 60)
    
    # schema_analysis = await Runner.run(
    #     agent,
    #     input="Use supabase mcp tools, give me a description in Supabase public schema.",
    #     session=session
    # )
    # schema_analysis_output = schema_analysis.final_output
    
    # schema_path = output_dir / f"schema_description_{timestamp}.md"
    # schema_path.write_text(schema_analysis_output, encoding="utf-8")
    # print(f"✓ Schema description saved to: {schema_path.name}\n")

    # ========== Step 2: Market Analysis ==========
    print("=" * 60)
    print("STEP 2: Market Analysis")
    print("=" * 60)
    
    market_analysis = await Runner.run(
        agent,
        input=MARKET_ANALYSIS_PROMPT,
        session=session
    )
    market_analysis_output = market_analysis.final_output
    
    market_path = output_dir / f"market_analysis_{timestamp}.md"
    market_path.write_text(market_analysis_output, encoding="utf-8")
    print(f"✓ Market analysis saved to: {market_path.name}")
    
    # 解析市场分析 JSON
    market_analysis_json = json.loads(market_analysis_output)
    # print(market_analysis_json)
    
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
    
    # 在受众分析之前测试
    test_run = await Runner.run(
        agent,
        input=f"What was the TAM (Total Addressable Market) for {market_segments[0]['market_name']} that we just analyzed?",
        session=session
    )
    print(f"Session test: {test_run.final_output[:100]}...")
    # 创建一个深拷贝用于合并受众分析（保持原始市场分析不变）
    integrated_analysis = copy.deepcopy(market_analysis_json)

    print(f"\n📊 Found {len(market_segments)} market(s) to analyze:")

    # ========== Step 3: Customer Analysis for Each Market ==========
    print("=" * 60)
    print("STEP 3: Customer Analysis (循环处理每个市场)")
    print("=" * 60)
    
    all_validation_reports = []
    
    for idx, market in enumerate(market_segments, 1):
        market_name = market.get("market_name", f"market_{idx}")
        print(f"\n[{idx}/{len(market_segments)}] Processing Market: {market_name}")

        # 3.1 执行受众分析 - 利用 session 上下文，无需传递完整市场数据
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
            print(f"   ✓ Customer analysis saved: {customer_path.name}")
            
            # 3.2 将受众分析合并到 integrated_analysis 中（不修改原始 market_analysis_json）
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
            
            # # 3.3 数据建模验证
            print(f"   → Running data modeling validation...")
            market_reports = []
            question_data = parse_customer_analysis_to_dataframe(customer_json)
            print("=== question_check  ===")
            reports_list = []
            for question in question_data:
                # print(i)
                report = checkquestion_with_gpt(question, "schema_analysis_output")
                reports_list.append(report)
            
            # 将验证报告也合并到 integrated_analysis 中
            if market_name not in integrated_analysis:
                integrated_analysis[market_name] = {}
            integrated_analysis[market_name]["validation_reports"] = reports_list
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

    # ========== Step 4: 保存完整的分析结果 ==========
    print("=" * 60)
    print("STEP 4: Saving Complete Analysis Results")
    print("=" * 60)
    
    # 4.1 保存纯市场分析（不含受众分析）
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
    print(f"✓ Pure market analysis saved: {pure_market_path.name}")
    
    # 4.2 保存集成分析（市场分析 + 受众分析）
    integrated_analysis_output = {
        "metadata": {
            "analysis_type": "integrated_market_and_customer",
            "analysis_timestamp": timestamp,
            "analysis_date": datetime.now().isoformat(),
        },
        "markets": integrated_analysis
    }
    
    # 将验证报告添加到集成分析中
    if market_name in integrated_analysis and "customer_analysis" in integrated_analysis[market_name]:
        # 如果customer_analysis是字典格式，直接添加validation_reports
        if isinstance(integrated_analysis[market_name]["customer_analysis"], dict):
            integrated_analysis[market_name]["customer_analysis"]["validation_reports"] = reports_list
        # 如果customer_analysis是列表格式，添加到第一个元素
        elif isinstance(integrated_analysis[market_name]["customer_analysis"], list) and len(integrated_analysis[market_name]["customer_analysis"]) > 0:
     
            integrated_analysis[market_name]["customer_analysis"][0]["validation_reports"] = reports_list
    integrated_path = output_dir / f"integrated_analysis_{timestamp}.json"
    integrated_path.write_text(
        json.dumps(integrated_analysis_output, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )
    print(f"✓ Integrated analysis saved: {integrated_path.name}")
    
    # 4.3 保存所有验证报告汇总
    
    
    # # 返回关键数据供后续使用
    # return {
    #     "market_analysis": market_analysis_json,
    #     "integrated_analysis": integrated_analysis,
    #     "validation_reports": all_validation_reports,
    #     "timestamp": timestamp
    # }


if __name__ == "__main__":
    asyncio.run(main())

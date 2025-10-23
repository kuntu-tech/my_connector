from datetime import datetime
import json
import sys
import os
import asyncio
import time
from agents import Agent, Runner, function_tool, ModelSettings, HostedMCPTool,SQLiteSession,WebSearchTool
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
sys.path.append(str(Path(__file__).resolve().parent.parent))
from question_check_test import checkquestion_with_gpt


### 传参
# 1. SUPABASE_PROJECT_URL 
# 2. SUPABASE_ACCESS_TOKEN 
# 3. USER_NAME
# 4. 数据审查的结果：只有为true才执行

### 输出
# 1. 此代码中out到文件中的内容，应该入库到”ai分析“中的”results“
# 2. 入库后，应该发送提示给需要此数据的模块

load_dotenv()
SUPABASE_PROJECT_ID = os.getenv("SUPABASE_PROJECT_ID")
SUPABASE_ACCESS_TOKEN = os.getenv("SUPABASE_ACCESS_TOKEN")  # Personal Access Token (PAT)
SUPABASE_MCP_URL = f"https://mcp.supabase.com/mcp?project_ref={SUPABASE_PROJECT_ID}"
USER_NAME = "huimin"
OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")


### 1. 读取提示词
BUSINESS_EXPERT_PROMPT=(Path(__file__).resolve().parent / "demo2" / "system_prompt.md").read_text(encoding="utf-8")
MARKET_ANALYSIS_PROMPT=(Path(__file__).resolve().parent / "demo2" / "market_analysis_prompt.md").read_text(encoding="utf-8")
AUDIENCE_ANALYSIS_PROMPT=(Path(__file__).resolve().parent / "demo2" / "audience_analysis_prompt.md").read_text(encoding="utf-8")


### 2. 工具函数
def audit_table_with_gpt(table_info):
    # print(table_name,schema_data,sample_data)
    client = OpenAI(api_key=OPENAI_API_KEY)
    # print(client)
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

    # print(f"正在进行表：{table_info.get('table_name')}的数据审查 ...")
    # print(table_info)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a data compliance expert. Always respond with valid JSON only."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"},
        temperature=0
    )
    # print(response)
    report = response.choices[0].message.content
    print(f"\n审查结果：\n", report)
    return report
#数据审查主流程
def data_check(tables_info):
    reports_list = []
    all_allowed = True  # 用于判断整体结论
    for table in tables_info:
        try:
            report = audit_table_with_gpt(table)
            report_json = json.loads(report)
            reports_list.append(report_json)
            # 判断是否允许使用
            if not report_json.get("allowed_to_use", False):
                all_allowed = False
        except Exception as e:
            print(f"审查 {table} 失败：{e}")
            report_json = {"table_name": table.get("table_name", "unknown"), "allowed_to_use": False, "error": str(e)}
            reports_list.append(report_json)
            all_allowed = False
    # 统一总结报告
    summary = {
        "tables_audited": reports_list,
        "final_conclusion": all_allowed
    }
    print("总结报告：")
    print(json.dumps(summary, indent=4, ensure_ascii=False))
    
    # 保存审查结果到文件
    output_dir = Path(__file__).resolve().parent / "outputs-1"
    output_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    
    # 创建包含all_allowed和summary的完整审查结果
    complete_audit_result = {
        "all_allowed": all_allowed,
        "summary": summary,
        "audit_timestamp": timestamp
    }
    
    audit_path = output_dir / f"data_audit_{timestamp}.json"
    audit_path.write_text(json.dumps(complete_audit_result, indent=4, ensure_ascii=False), encoding="utf-8")
    print(f"数据审查结果已保存到: {audit_path}")
    print(f"all_allowed: {all_allowed}")
    print(f"summary: {json.dumps(summary, indent=2, ensure_ascii=False)}")
    
    # 返回 True / False 信号
    return all_allowed, summary

@function_tool
def get_current_time()-> str:
    return datetime.now().astimezone().isoformat()



### 3. 主函数
async def main():
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
        """,
        session=session
    )
    schema_analysis_output = schema_analysis.final_output
    print(f"Schema analysis output: {schema_analysis_output}")
    try:
        schema_analysis_json = json.loads(schema_analysis_output)
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        print("Creating mock schema data for testing...")
        schema_analysis_json = {
            "description": {
                "tables": [
                    {
                        "table_name": "test_table",
                        "columns": ["id", "name", "created_at"],
                        "sample_data": [{"id": 1, "name": "test", "created_at": "2024-01-01"}]
                    }
                ]
            }
        }
    output_dir = Path(__file__).resolve().parent / "outputs-1"
    output_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    md_path = output_dir / f"schema_description _{timestamp}.md"
    md_path.write_text(schema_analysis_output, encoding="utf-8")
    print(" =======  data_check  ======= ")  
    tables_info = schema_analysis_json.get("description")["tables"]
    all_allowed,summary = data_check(tables_info)
    # ----------------------
    # -------------------------
    if all_allowed:
        print("======== Market Analysis ========")
        market_analysis = await Runner.run(
            agent,
            input=MARKET_ANALYSIS_PROMPT,
            session=session
        )
        output = market_analysis.final_output
        output_dir = Path(__file__).resolve().parent / "outputs-1"
        output_dir.mkdir(exist_ok=True)
        md_path = output_dir / f"market_analysis_{timestamp}.md"
        md_path.write_text(output, encoding="utf-8")
        print("market analysis finished.")
        print("======== audience Analysis =========")
        audience_analysis = await Runner.run(
            agent, 
            input = AUDIENCE_ANALYSIS_PROMPT,
            session=session
            )
        audience_analysis_output = audience_analysis.final_output
        output_dir = Path(__file__).resolve().parent / "outputs-1"
        output_dir.mkdir(exist_ok=True)
        md_path = output_dir / f"audience_analysis_{timestamp}.md"
        md_path.write_text(audience_analysis_output, encoding="utf-8")
        print("audience analysis finished.")

        ## 问题审查
        print("=======  data modeling validation ========")
        results_json = json.loads(audience_analysis_output)
        reports_list = []
        for segment in results_json.get("segments", []):
            segment_name = segment.get("segment_name", "unknown_segment")
            for question in segment.get("valued_questions", []):
                print(f"---- {segment_name}")
                report = checkquestion_with_gpt(question, schema_analysis_output)
                reports_list.append(report)
        print(reports_list)
        
        # 保存数据建模验证结果到文件
        output_dir = Path(__file__).resolve().parent / "outputs-1"
        output_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        validation_path = output_dir / f"data_modeling_validation_{timestamp}.json"
        validation_path.write_text(json.dumps(reports_list, indent=4, ensure_ascii=False), encoding="utf-8")
        print(f"数据建模验证结果已保存到: {validation_path}")
    else:
        output_info = check_result.get("check_report")
        print(output_info)
        
        # 保存审查失败的结果到文件
        output_dir = Path(__file__).resolve().parent / "outputs-1"
        output_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        
        # 创建包含all_allowed和summary的完整审查失败结果
        complete_audit_failed_result = {
            "all_allowed": all_allowed,
            "summary": summary,
            "audit_timestamp": timestamp
        }
        
        audit_failed_path = output_dir / f"data_audit_failed_{timestamp}.json"
        audit_failed_path.write_text(json.dumps(complete_audit_failed_result, indent=4, ensure_ascii=False), encoding="utf-8")
        print(f"数据审查失败结果已保存到: {audit_failed_path}")
        print(f"all_allowed: {all_allowed}")
        print(f"summary: {json.dumps(summary, indent=2, ensure_ascii=False)}")
	
if __name__ == "__main__":
    asyncio.run(main())
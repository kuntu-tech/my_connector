import json
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def checkquestion_with_gpt(question_info, schema_analysis_output):
    """
    使用GPT检查问题是否可以通过给定的schema进行分析
    基于conn_supabase(1).py和question_check_test.py的功能整合
    """
    client = OpenAI(api_key=OPENAI_API_KEY)
    
    # 提取问题信息
    if isinstance(question_info, dict):
        question = question_info.get("question", "")
        data_requirement = question_info.get("data_requirement", "")
    else:
        question = str(question_info)
        data_requirement = ""
    
    prompt = f"""
    你是一名数据分析师，请根据每一个问题{question}，结合数据表的基本信息{data_requirement}，给出回答，这些表是否能回答问题：
    以下表信息：{schema_analysis_output}
    要求：
    1.输出原始的question,data_requirement
    2.输出判断结果：是否可以直接使用SQL在这些表中查询这个问题，如果可以result_type:直接查询输出1，需要建模输出2，不能查询输出3
    3.如果可以从表信息中查询这个问题，给出SQL语句，并且验证，这条SQL语句可以查询成功
    4.以英文结果输出，输出结果为JSON格式，主要包括字段：question,data_requirement,sql_query,result_type
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        
        result = response.choices[0].message.content
        # 尝试解析JSON，如果失败则返回原始文本
        try:
            return json.loads(result)
        except json.JSONDecodeError:
            return {
                "question": question,
                "data_requirement": data_requirement,
                "sql_query": "",
                "result_type": 3,
                "reasoning": result
            }
    except Exception as e:
        return {
            "question": question,
            "data_requirement": data_requirement,
            "sql_query": "",
            "result_type": 3,
            "reasoning": f"Error occurred: {str(e)}"
        }

import json
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def checkquestion_with_gpt(question_info, tables_info):
    # print(table_name,schema_data,sample_data)
    client = OpenAI(api_key=OPENAI_API_KEY)
    # print(client)
    prompt = f"""
You are a data analysis and modeling expert. Below is the database table information: {tables_info}.
Please determine, based on {tables_info}, whether it is possible to answer the following question from the data: {question_info.get("question")}.

For each question, output a JSON object with the following requirements:

Output a judgment result:
Determine whether the question can be directly answered using SQL queries on these tables.

If yes → result_type = 1 (direct SQL query possible)

If modeling is required → result_type = 2

If it cannot be answered from the data → result_type = 3

If the question can be answered directly from the tables,
provide a valid SQL query and verify that this SQL can be executed successfully.

Output format:

The result must be in English.

The output must be in JSON format, based on the original {question_info} object, with the following additional fields:

sql_query: the executable SQL statement if applicable; otherwise NULL if modeling is required or the question cannot be answered.

query_type:

1 → SQL query (directly answerable)

2 → requires modeling/analysis

3 → cannot be answered from the data.
"""

    response = client.chat.completions.create(
        model="gpt-5-nano",
        messages=[{"role": "user", "content": prompt}],
        # temperature=0
    )
    # print(response)
    report = response.choices[0].message.content
    report = json.loads(report)
    # print(f"\n📋 审查结果：\n", report)
    return report

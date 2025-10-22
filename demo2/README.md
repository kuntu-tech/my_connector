# Demo2 Package

这个包包含了 AI 分析的核心功能，使用 OpenAI Agents 和 Supabase MCP 工具进行数据驱动分析。

## 📁 文件结构

```
demo2/
├── __init__.py                    # 包初始化文件
├── demo-2.py                     # 原始脚本文件
├── demo_2_core.py                # 核心功能模块
├── system_prompt.md              # 系统提示词
├── market_analysis_prompt.md     # 市场分析提示词
├── audience_analysis_prompt.md   # 受众分析提示词
├── requirements.txt              # 包依赖
└── README.md                     # 包说明文档
```

## 🚀 功能特性

### 核心分析功能

1. **数据库结构分析 (Schema Analysis)**
   - 分析 Supabase 数据库的公共模式
   - 生成数据结构报告

2. **市场分析 (Market Analysis)**
   - 基于数据驱动的市场洞察
   - 六步分析工作流

3. **受众分析 (Audience Analysis)**
   - 用户行为分析
   - 受众细分和画像

### 核心函数

- `initialize_agent()` - 初始化 AI Agent
- `run_schema_analysis()` - 执行数据库结构分析
- `run_market_analysis()` - 执行市场分析
- `run_audience_analysis()` - 执行受众分析
- `save_to_database()` - 保存结果到数据库

## 📋 使用方法

### 直接使用脚本

```bash
cd demo2
python demo-2.py
```

### 作为包导入使用

```python
from demo2 import (
    initialize_agent,
    run_schema_analysis,
    run_market_analysis,
    run_audience_analysis
)

# 初始化 Agent
agent = await initialize_agent(
    supabase_project_url="your_url",
    supabase_access_token="your_token",
    user_name="your_user"
)

# 执行分析
result = await run_schema_analysis(agent, "user_name")
```

## 🔧 环境配置

### 必需环境变量

```env
OPENAI_API_KEY=your_openai_api_key
SUPABASE_PROJECT_URL=https://mcp.supabase.com/mcp?project_ref=your_project_id
SUPABASE_ACCESS_TOKEN=your_supabase_access_token
```

### 可选环境变量

```env
USER_NAME=your_username
DATA_REVIEW_RESULT=true
```

## 📦 依赖安装

```bash
pip install -r demo2/requirements.txt
```

## 🔄 API 集成

这个包被设计为可以与 FastAPI 应用无缝集成：

```python
# 在 FastAPI 应用中使用
from demo2 import initialize_agent, run_schema_analysis

@app.post("/analyze")
async def analyze_endpoint(request: AnalysisRequest):
    agent = await initialize_agent(
        request.supabase_project_url,
        request.supabase_access_token,
        request.user_name
    )
    
    result = await run_schema_analysis(agent, request.user_name)
    return result
```

## 📊 输出格式

所有分析函数返回统一格式的结果：

```python
{
    "output": "分析结果内容...",
    "files": ["outputs/analysis_1234567890.md"]
}
```

## 🛠️ 开发说明

- 所有分析函数都是异步的，支持并发执行
- 结果会自动保存到文件系统
- 支持数据库结果存储
- 包含完整的错误处理机制

## 📝 注意事项

1. 确保 Supabase 连接配置正确
2. 验证 OpenAI API 密钥有效性
3. 检查文件系统写入权限
4. 确保所有依赖包已正确安装

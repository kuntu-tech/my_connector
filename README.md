# My Custom Connector

一个基于 FastAPI 的 AI 分析服务，集成了 ChatGPT Connectors 和 Supabase MCP 工具。

## 📁 项目结构

```
my_connector/
├── demo2/                          # Demo2 分析包
│   ├── __init__.py                # 包初始化文件
│   ├── demo-2.py                  # 原始分析脚本
│   ├── demo_2_core.py             # 核心功能模块
│   ├── system_prompt.md           # 系统提示词
│   ├── market_analysis_prompt.md  # 市场分析提示词
│   ├── audience_analysis_prompt.md # 受众分析提示词
│   ├── requirements.txt           # 包依赖
│   └── README.md                  # 包说明文档
├── analysis_api.py                # FastAPI 分析服务
├── app.py                         # 原始 FastAPI 应用
├── start_api.py                   # API 服务启动脚本
├── test_api.py                    # API 测试脚本
├── API_README.md                  # API 使用文档
├── requirements.txt               # 项目依赖
├── .env                          # 环境变量配置
└── README.md                     # 项目说明文档
```

## 🚀 功能特性

### 1. AI 分析服务
- **数据库结构分析** - 分析 Supabase 数据库模式
- **市场分析** - 基于数据驱动的市场洞察
- **受众分析** - 用户行为分析和受众细分

### 2. RESTful API 接口
- 统一的 `/analyze` 端点处理所有分析类型
- 支持批量分析
- 自动生成 API 文档
- 完整的错误处理和日志记录

### 3. 灵活的配置管理
- 支持环境变量和 API 参数配置
- 数据审查控制
- 会话管理

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

创建或更新 `.env` 文件：

```env
OPENAI_API_KEY=your_openai_api_key
SUPABASE_PROJECT_URL=https://mcp.supabase.com/mcp?project_ref=your_project_id
SUPABASE_ACCESS_TOKEN=your_supabase_access_token
```

### 3. 启动 AI 分析服务

```bash
python start_api.py
```

或使用 uvicorn：

```bash
uvicorn analysis_api:app --reload --host 0.0.0.0 --port 8000
```

### 4. 访问服务

- **API 文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health
- **分析接口**: http://localhost:8000/analyze

### 5. 运行原始脚本

```bash
cd demo2
python demo-2.py
```

## Deploy to Render

1. Push this repository to GitHub.
2. Go to https://render.com
3. Click "New → Web Service"
4. Choose your GitHub repository.
5. Use the following commands:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app:app --host 0.0.0.0 --port 10000`
6. After deployment, verify:
   - `/ping` returns `{"message":"pong"}`
   - `/health` returns `{"status":"ok"}`
   - `/openapi.json` is accessible for ChatGPT Connector.

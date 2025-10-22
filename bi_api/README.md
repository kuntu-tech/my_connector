# BI Analysis API

这是一个基于 FastAPI 的商业智能分析服务，将原有的 `BI_result(1).py` 脚本封装为 RESTful API。该API集成了数据合规审查、市场分析、受众分析和问题验证等功能。

## 🚀 功能特性

- **Schema分析**: 分析Supabase数据库结构
- **数据合规审查**: 使用GPT进行数据合规性检查
- **市场分析**: 基于McKinsey方法论的市场分析
- **受众分析**: 详细的受众细分和价值问题分析
- **问题验证**: 验证受众问题是否可以通过数据回答
- **动态环境变量**: 支持通过API请求动态传递配置参数

## 📁 项目结构

```
bi_api/
├── app.py                 # FastAPI 应用主文件
├── start_bi_api.py        # 启动脚本
├── test_bi_api.py         # 测试脚本
├── render.yaml            # Render 部署配置
├── requirements.txt        # Python 依赖
├── README.md              # 项目文档
└── prompts/               # 提示词文件
    ├── system_prompt.md
    ├── market_analysis_prompt.md
    └── audience_analysis_prompt.md
```

## 🔧 安装和运行

### 1. 安装依赖

```bash
cd bi_api
pip install -r requirements.txt
```

### 2. 配置环境变量

创建 `.env` 文件或设置环境变量：

```env
# Supabase配置
SUPABASE_PROJECT_ID=your_supabase_project_id
SUPABASE_ACCESS_TOKEN=your_supabase_access_token

# OpenAI配置
OPENAI_API_KEY=your_openai_api_key

# 用户配置
USER_NAME=huimin
DATA_REVIEW_RESULT=true
```

### 3. 启动服务

```bash
python start_bi_api.py
```

或者直接使用 uvicorn：

```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

### 4. 访问 API 文档

打开浏览器访问：http://localhost:8000/docs

## 📋 API 端点

### 基础端点

- `GET /health` - 健康检查
- `GET /config` - 获取配置信息
- `GET /results` - 列出所有分析结果文件
- `GET /results/{filename}` - 获取特定结果文件

### 分析端点

- `POST /analyze` - 执行BI分析（主要端点）

## 🔧 API 使用示例

### 1. Schema分析

```bash
curl -X POST "http://localhost:8000/analyze" \
     -H "Content-Type: application/json" \
     -d '{
       "analysis_type": "schema",
       "supabase_project_id": "your_project_id",
       "supabase_access_token": "your_access_token",
       "user_name": "test_user",
       "data_review_result": true,
       "openai_api_key": "your_openai_key"
     }'
```

### 2. 市场分析

```bash
curl -X POST "http://localhost:8000/analyze" \
     -H "Content-Type: application/json" \
     -d '{
       "analysis_type": "market",
       "supabase_project_id": "your_project_id",
       "supabase_access_token": "your_access_token",
       "user_name": "test_user"
     }'
```

### 3. 完整分析流程

```bash
curl -X POST "http://localhost:8000/analyze" \
     -H "Content-Type: application/json" \
     -d '{
       "analysis_type": "all",
       "supabase_project_id": "your_project_id",
       "supabase_access_token": "your_access_token",
       "user_name": "test_user",
       "data_review_result": true,
       "openai_api_key": "your_openai_key"
     }'
```

## 📊 请求参数

### BIAnalysisRequest 模型

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| analysis_type | string | 是 | - | 分析类型: "schema", "market", "audience", "all" |
| supabase_project_id | string | 是 | - | Supabase 项目 ID |
| supabase_access_token | string | 是 | - | Supabase 访问令牌 |
| user_name | string | 否 | "huimin" | 用户标识 |
| data_review_result | boolean | 否 | true | 数据审查结果 |
| openai_api_key | string | 否 | null | OpenAI API 密钥 |

## 📤 响应格式

### BIAnalysisResponse 模型

```json
{
  "success": true,
  "analysis_type": "all",
  "message": "all analysis completed successfully",
  "results": {
    "schema_analysis": "分析结果内容...",
    "data_compliance": {
      "tables_audited": [...],
      "final_conclusion": true
    },
    "market_analysis": "市场分析结果...",
    "audience_analysis": "受众分析结果...",
    "question_validation": [...]
  },
  "files_generated": [
    "outputs/schema_description_1234567890.md",
    "outputs/market_analysis_1234567890.md",
    "outputs/audience_analysis_1234567890.md"
  ],
  "database_saved": true,
  "execution_time": 120.5,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## 🧪 测试

运行测试脚本：

```bash
python test_bi_api.py
```

测试脚本会验证：
- 健康检查端点
- 配置端点
- Schema分析功能
- 结果管理端点

## 🚀 部署到 Render

### 1. 准备部署

确保 `render.yaml` 文件配置正确：

```yaml
services:
  - type: web
    name: bi-analysis-api
    env: python
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: python start_bi_api.py
    healthCheckPath: /health
    envVars:
      - key: OPENAI_API_KEY
        sync: false
      - key: SUPABASE_PROJECT_ID
        sync: false
      - key: SUPABASE_ACCESS_TOKEN
        sync: false
      - key: USER_NAME
        value: huimin
      - key: DATA_REVIEW_RESULT
        value: true
      - key: ENVIRONMENT
        value: production
```

### 2. 部署步骤

1. 将代码推送到GitHub仓库
2. 在Render中创建新的Web服务
3. 连接GitHub仓库
4. 设置环境变量：
   - `OPENAI_API_KEY`: 您的OpenAI API密钥
   - `SUPABASE_PROJECT_ID`: Supabase项目ID
   - `SUPABASE_ACCESS_TOKEN`: Supabase访问令牌
5. 部署服务

### 3. 验证部署

部署完成后，访问：
- API文档: `https://your-app-name.onrender.com/docs`
- 健康检查: `https://your-app-name.onrender.com/health`

## 🔧 核心功能

- **initialize_agent()** - 初始化 AI Agent
- **run_schema_analysis()** - 执行数据库结构分析
- **data_check()** - 数据合规性审查
- **run_market_analysis()** - 执行市场分析
- **run_audience_analysis()** - 执行受众分析
- **run_question_validation()** - 问题验证
- **save_to_database()** - 保存结果到数据库

## 🚨 注意事项

1. **API密钥安全**: 不要在代码中硬编码API密钥，使用环境变量
2. **超时设置**: 完整分析可能需要较长时间，建议设置合适的超时时间
3. **资源限制**: Render免费计划有资源限制，复杂分析可能需要升级
4. **错误处理**: API包含完整的错误处理机制，会返回详细的错误信息
5. **数据合规**: 数据合规审查是强制性的，只有通过审查的数据才会进行后续分析

## 📝 更新日志

- **v1.0.0**: 初始版本，集成BI_result(1).py功能
- 支持动态环境变量传递
- 完整的API文档和测试套件
- 支持Render部署

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目。

## 📄 许可证

MIT License
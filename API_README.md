# AI Analysis API

这是一个基于 FastAPI 的 AI 分析服务，将原有的 `demo-2.py` 脚本封装为 RESTful API。

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

### 3. 启动服务

```bash
python start_api.py
```

或者直接使用 uvicorn：

```bash
uvicorn analysis_api:app --host 0.0.0.0 --port 8000 --reload
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

- `POST /analyze` - 执行分析（主要端点）
- `POST /analyze/batch` - 批量分析

## 🔧 API 使用示例

### 1. 健康检查

```bash
curl -X GET "http://localhost:8000/health"
```

### 2. 执行 Schema 分析

```bash
curl -X POST "http://localhost:8000/analyze" \
     -H "Content-Type: application/json" \
     -d '{
       "analysis_type": "schema",
       "supabase_project_url": "https://mcp.supabase.com/mcp?project_ref=your_project_id",
       "supabase_access_token": "your_access_token",
       "user_name": "test_user",
       "data_review_result": true
     }'
```

### 3. 执行市场分析

```bash
curl -X POST "http://localhost:8000/analyze" \
     -H "Content-Type: application/json" \
     -d '{
       "analysis_type": "market",
       "supabase_project_url": "https://mcp.supabase.com/mcp?project_ref=your_project_id",
       "supabase_access_token": "your_access_token"
     }'
```

### 4. 执行所有分析

```bash
curl -X POST "http://localhost:8000/analyze" \
     -H "Content-Type: application/json" \
     -d '{
       "analysis_type": "all",
       "supabase_project_url": "https://mcp.supabase.com/mcp?project_ref=your_project_id",
       "supabase_access_token": "your_access_token"
     }'
```

## 📊 请求参数

### AnalysisRequest 模型

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| analysis_type | string | 是 | - | 分析类型: "schema", "market", "audience", "all" |
| supabase_project_url | string | 是 | - | Supabase 项目 URL |
| supabase_access_token | string | 是 | - | Supabase 访问令牌 |
| user_name | string | 否 | "huimin" | 用户标识 |
| data_review_result | boolean | 否 | true | 数据审查结果 |
| openai_api_key | string | 否 | null | OpenAI API 密钥 |

## 📤 响应格式

### AnalysisResponse 模型

```json
{
  "success": true,
  "analysis_type": "market",
  "message": "market analysis completed successfully",
  "results": {
    "market_analysis": "分析结果内容..."
  },
  "files_generated": [
    "outputs/market_analysis_1234567890.md"
  ],
  "database_saved": true,
  "execution_time": 45.2,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## 🧪 测试

运行测试脚本：

```bash
python test_api.py
```

## 🔧 开发

### 项目结构

```
├── analysis_api.py      # FastAPI 应用主文件
├── demo_2_core.py      # 核心功能模块
├── start_api.py        # 启动脚本
├── test_api.py         # 测试脚本
├── API_README.md       # API 文档
└── requirements.txt    # 依赖文件
```

### 核心功能

- **initialize_agent()** - 初始化 AI Agent
- **run_schema_analysis()** - 执行数据库结构分析
- **run_market_analysis()** - 执行市场分析
- **run_audience_analysis()** - 执行受众分析
- **save_to_database()** - 保存结果到数据库

## 🚨 注意事项

1. **API 密钥安全**：请确保不要将 API 密钥提交到版本控制系统
2. **网络连接**：确保能够访问 OpenAI 和 Supabase 服务
3. **权限设置**：确保 Supabase access token 有足够的权限
4. **资源限制**：分析任务可能需要较长时间，注意设置合适的超时时间

## 🐛 故障排除

### 常见问题

1. **401 错误**：检查 Supabase access token 是否正确
2. **连接超时**：检查网络连接和防火墙设置
3. **模块导入错误**：确保已安装所有依赖包

### 日志查看

API 服务会输出详细的日志信息，包括：
- 请求处理状态
- 错误信息
- 执行时间统计

## 📞 支持

如有问题，请检查：
1. API 文档：http://localhost:8000/docs
2. 健康检查：http://localhost:8000/health
3. 配置信息：http://localhost:8000/config

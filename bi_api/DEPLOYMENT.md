# BI Analysis API 部署指南

## 项目概述

本项目成功将 `BI_result(1).py` 文件封装成了一个完整的 FastAPI 服务，提供 AI 驱动的商业智能分析功能。

## 项目结构

```
bi_api/
├── app.py                 # 主应用文件 (FastAPI)
├── start_api.py          # 启动脚本
├── requirements.txt      # Python 依赖
├── render.yaml          # Render 部署配置
├── env_template.txt     # 环境变量模板
├── README.md            # 项目说明文档
├── test_api.py          # API 测试脚本
├── demo.py              # 演示脚本
└── prompts/             # 提示词文件
    ├── system_prompt.md
    ├── market_analysis_prompt.md
    └── audience_analysis_prompt.md
```

## 核心功能

### 1. API 接口
- **健康检查**: `GET /health`
- **配置检查**: `GET /config`
- **数据分析**: `POST /analyze`
- **结果管理**: `GET /results`, `GET /results/{filename}`

### 2. 分析类型
- **Schema 分析**: 数据库结构分析
- **市场分析**: 基于 McKinsey 框架的市场分析
- **受众分析**: 目标受众细分和价值问题分析
- **完整分析**: 包含数据合规性检查的完整流程

### 3. 数据合规性
- GPT 驱动的数据合规性审查
- 自动检测敏感信息字段
- 只有通过合规性检查才会执行后续分析

## 环境变量配置

### 必需的环境变量
```env
OPENAI_API_KEY=your_openai_api_key_here
SUPABASE_PROJECT_ID=your_supabase_project_id_here
SUPABASE_ACCESS_TOKEN=your_supabase_access_token_here
```

### 可选的环境变量
```env
USER_NAME=huimin
DATA_REVIEW_RESULT=true
ENVIRONMENT=production
```

## 本地开发

### 1. 设置环境
```bash
cd bi_api
cp env_template.txt .env
# 编辑 .env 文件，填入你的配置
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 启动服务
```bash
python start_api.py
```

### 4. 测试 API
```bash
python test_api.py
```

## 部署到 Render

### 1. 准备部署
1. 将 `bi_api` 文件夹推送到 GitHub 仓库
2. 确保所有文件都在仓库中

### 2. 在 Render 中创建服务
1. 登录 Render 控制台
2. 点击 "New +" -> "Web Service"
3. 连接你的 GitHub 仓库
4. 选择 `bi_api` 文件夹

### 3. 配置服务
- **名称**: `bi-analysis-api`
- **环境**: `Python 3`
- **计划**: `Free`
- **构建命令**: `pip install -r requirements.txt`
- **启动命令**: `uvicorn app:app --host 0.0.0.0 --port $PORT`
- **健康检查路径**: `/health`

### 4. 设置环境变量
在 Render 控制台中设置以下环境变量：
- `OPENAI_API_KEY`: 你的 OpenAI API 密钥
- `SUPABASE_PROJECT_ID`: 你的 Supabase 项目 ID
- `SUPABASE_ACCESS_TOKEN`: 你的 Supabase 访问令牌
- `USER_NAME`: `huimin`
- `DATA_REVIEW_RESULT`: `true`
- `ENVIRONMENT`: `production`

### 5. 部署
点击 "Create Web Service" 开始部署

## API 使用示例

### 基本分析请求
```python
import requests

# 分析请求
analysis_request = {
    "analysis_type": "all",
    "supabase_project_id": "your_project_id",
    "supabase_access_token": "your_access_token",
    "user_name": "huimin",
    "data_review_result": True,
    "openai_api_key": "your_openai_key"
}

response = requests.post(
    "https://your-render-app.onrender.com/analyze",
    json=analysis_request
)

result = response.json()
print(f"分析完成: {result['message']}")
print(f"执行时间: {result['execution_time']:.2f}秒")
```

### 获取分析结果
```python
# 列出所有结果
response = requests.get("https://your-render-app.onrender.com/results")
results = response.json()
print(f"结果文件数量: {results['count']}")

# 获取特定结果文件
filename = results['files'][0]  # 获取第一个文件
response = requests.get(f"https://your-render-app.onrender.com/results/{filename}")
file_content = response.json()
print(f"文件内容: {file_content['content'][:200]}...")
```

## 注意事项

1. **API 密钥安全**: 确保不要在代码中硬编码 API 密钥
2. **数据合规性**: 所有数据都会经过合规性检查
3. **超时设置**: 分析可能需要较长时间，建议设置适当的超时
4. **错误处理**: API 会返回详细的错误信息，便于调试
5. **文件存储**: 分析结果会保存到本地文件系统

## 故障排除

### 常见问题
1. **环境变量未设置**: 检查 `.env` 文件或 Render 环境变量配置
2. **Supabase 连接失败**: 验证项目 ID 和访问令牌
3. **OpenAI API 错误**: 检查 API 密钥和额度
4. **分析超时**: 增加请求超时时间或检查网络连接

### 调试方法
1. 使用 `GET /health` 检查服务状态
2. 使用 `GET /config` 检查配置
3. 查看 Render 日志了解详细错误信息
4. 使用本地测试脚本验证功能

## 扩展功能

### 可能的改进
1. **数据库集成**: 将分析结果保存到 Supabase 数据库
2. **缓存机制**: 添加结果缓存以提高性能
3. **批量处理**: 支持批量分析请求
4. **实时通知**: 分析完成后发送通知
5. **结果可视化**: 添加图表和可视化功能

## 技术支持

如有问题，请检查：
1. 项目 README.md 文件
2. API 文档 (访问 `/docs` 端点)
3. 测试脚本和演示脚本
4. Render 部署日志


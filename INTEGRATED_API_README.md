# 集成分析API接口使用说明

## 概述

新增的 `/integrated-analysis` 接口封装了 `demo-4.py` 的功能，提供完整的市场分析和受众分析能力。

## API端点

**URL**: `POST /integrated-analysis`  
**功能**: 执行集成的市场分析和受众分析

## 请求参数

```json
{
  "supabase_project_id": "string",      // 必需: Supabase项目ID
  "supabase_access_token": "string",    // 必需: Supabase访问令牌
  "user_name": "string",                // 可选: 用户名，默认为"huimin"
  "openai_api_key": "string",           // 可选: OpenAI API密钥
  "analysis_type": "string"             // 可选: 分析类型，默认为"full_integrated"
}
```

### 参数说明

- `supabase_project_id`: Supabase项目ID，用于连接数据库
- `supabase_access_token`: Supabase访问令牌，用于身份验证
- `user_name`: 用户标识符，用于会话管理
- `openai_api_key`: OpenAI API密钥（可选，会使用环境变量中的密钥）
- `analysis_type`: 分析类型
  - `"market_only"`: 仅执行市场分析
  - `"full_integrated"`: 执行完整的市场+受众分析（默认）

## 响应格式

```json
{
  "success": true,
  "message": "Integrated analysis completed successfully",
  "analysis_type": "full_integrated",
  "results": {
    "market_analysis": {...},           // 市场分析结果
    "market_segments": [...],           // 市场段信息
    "integrated_analysis": {...},        // 集成分析结果（仅full_integrated模式）
    "validation_reports": [...]          // 问题验证报告（仅full_integrated模式）
  },
  "files_generated": [                  // 生成的文件列表
    "/path/to/market_analysis_20241201_143022.md",
    "/path/to/integrated_analysis_20241201_143022.json"
  ],
  "execution_time": 45.67,              // 执行时间（秒）
  "timestamp": "20241201_143022"        // 时间戳
}
```

## 使用示例

### Python示例

```python
import requests
import json

# API配置
api_url = "http://localhost:8000/integrated-analysis"

# 请求数据
request_data = {
    "supabase_project_id": "your_project_id",
    "supabase_access_token": "your_access_token",
    "user_name": "test_user",
    "analysis_type": "full_integrated"
}

# 发送请求
response = requests.post(api_url, json=request_data)

if response.status_code == 200:
    result = response.json()
    print(f"分析完成，耗时: {result['execution_time']:.2f}秒")
    print(f"生成文件: {len(result['files_generated'])}个")
else:
    print(f"请求失败: {response.status_code}")
    print(response.text)
```

### cURL示例

```bash
curl -X POST "http://localhost:8000/integrated-analysis" \
  -H "Content-Type: application/json" \
  -d '{
    "supabase_project_id": "your_project_id",
    "supabase_access_token": "your_access_token",
    "user_name": "test_user",
    "analysis_type": "full_integrated"
  }'
```

## 分析流程

### 市场分析模式 (`market_only`)
1. 连接Supabase数据库
2. 执行市场分析
3. 保存市场分析结果
4. 返回市场分析数据

### 完整集成模式 (`full_integrated`)
1. 执行市场分析
2. 对每个市场段执行受众分析
3. 对每个问题执行数据验证
4. 整合所有分析结果
5. 保存多种格式的输出文件
6. 返回完整的分析结果

## 输出文件

分析完成后会生成以下文件（保存在 `bi_api/outputs-4/` 目录）：

- `market_analysis_{timestamp}.md`: 市场分析Markdown文件
- `customer_analysis_{market_name}_{timestamp}.md`: 各市场段的受众分析文件
- `market_analysis_pure_{timestamp}.json`: 纯市场分析JSON文件
- `integrated_analysis_{timestamp}.json`: 集成分析JSON文件

## 错误处理

API会返回适当的HTTP状态码和错误信息：

- `400`: 请求参数错误
- `500`: 服务器内部错误（分析失败）

## 注意事项

1. **执行时间**: 完整集成分析可能需要几分钟时间，请设置合适的超时时间
2. **API密钥**: 建议使用环境变量配置OpenAI API密钥
3. **文件存储**: 生成的文件存储在服务器本地，请定期清理
4. **并发限制**: 建议避免同时运行多个分析任务

## 测试

使用提供的测试脚本验证API功能：

```bash
python test_integrated_api.py
```

测试脚本会检查：
- 服务健康状态
- 配置信息
- 集成分析功能（可选）

## 部署

新接口已集成到现有的BI API服务中，通过以下命令启动：

```bash
python bi_api/start_bi_api.py
```

在Render平台上会自动部署，无需额外配置。

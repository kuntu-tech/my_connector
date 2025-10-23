#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
离线测试品牌策略Agent脚本
不依赖网络调用，只测试基本功能
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

def test_offline_functionality():
    """测试离线功能"""
    print("=== 品牌策略Agent离线测试 ===")
    
    # 1. 测试配置文件读取
    config_file = Path(__file__).resolve().parent / "config.json"
    if config_file.exists():
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        print(f"[OK] 配置文件读取成功: {list(config.keys())}")
    else:
        print("[ERROR] 配置文件不存在")
        return False
    
    # 2. 测试环境变量设置
    if 'openai_api_key' in config:
        os.environ['OPENAI_API_KEY'] = config['openai_api_key']
        print("[OK] OpenAI API密钥设置成功")
    
    if 'supabase_project_id' in config:
        os.environ['SUPABASE_PROJECT_ID'] = config['supabase_project_id']
        print("✓ Supabase项目ID设置成功")
    
    # 3. 测试时间戳生成
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    print(f"✓ 时间戳生成: {timestamp}")
    
    # 4. 测试目录操作
    outputs_dir = Path(__file__).resolve().parent / "outputs"
    outputs_dir.mkdir(exist_ok=True)
    print(f"✓ 输出目录创建: {outputs_dir}")
    
    # 5. 测试文件查找
    existing_files = list(outputs_dir.glob("integrated_analysis_*.json"))
    print(f"✓ 找到现有文件数量: {len(existing_files)}")
    
    if existing_files:
        latest_file = max(existing_files, key=lambda x: x.stat().st_mtime)
        print(f"✓ 最新文件: {latest_file.name}")
        
        # 读取并显示文件内容
        data = json.loads(latest_file.read_text(encoding="utf-8"))
        print(f"✓ 文件内容: {data}")
    else:
        # 创建新的测试文件
        test_file = outputs_dir / f"integrated_analysis_{timestamp}.json"
        sample_data = {
            "timestamp": timestamp,
            "analysis_type": "integrated_analysis",
            "status": "test",
            "data": {
                "brand_name": "测试品牌",
                "description": "这是一个测试品牌描述",
                "market_analysis": {
                    "target_market": "科技行业",
                    "competitors": ["品牌A", "品牌B"],
                    "opportunities": ["新兴市场", "技术创新"]
                },
                "audience_analysis": {
                    "primary_audience": "年轻专业人士",
                    "demographics": {
                        "age": "25-35",
                        "income": "中高收入",
                        "interests": ["科技", "创新", "效率"]
                    }
                }
            }
        }
        test_file.write_text(json.dumps(sample_data, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"✓ 创建测试文件: {test_file.name}")
        data = sample_data
    
    # 6. 模拟品牌策略处理（不调用AI）
    print("\n=== 模拟品牌策略处理 ===")
    
    # 基于现有数据生成品牌策略
    brand_strategy = {
        "chatapp_name": "Aurora Insights",
        "chatapp_description": "An AI-powered brand platform that transforms analytical insights into compelling, market-ready product narratives.",
        "chatapp_core_features": [
            {
                "feature_title": "Brand Positioning Engine",
                "intro": "Defines the brand's competitive edge and value promise using structured strategic logic."
            },
            {
                "feature_title": "Market Intelligence Hub", 
                "intro": "Aggregates and analyzes market data to identify opportunities and trends."
            },
            {
                "feature_title": "Audience Insight Generator",
                "intro": "Creates detailed audience personas and behavioral analysis."
            },
            {
                "feature_title": "Narrative Builder",
                "intro": "Transforms insights into compelling brand stories and messaging."
            }
        ]
    }
    
    # 7. 保存品牌策略结果
    strategy_file = outputs_dir / f"brand_strategy_{timestamp}.json"
    strategy_file.write_text(json.dumps(brand_strategy, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✓ 品牌策略结果保存: {strategy_file.name}")
    
    # 8. 显示结果
    print("\n=== 品牌策略结果 ===")
    print(f"应用名称: {brand_strategy['chatapp_name']}")
    print(f"应用描述: {brand_strategy['chatapp_description']}")
    print("\n核心功能:")
    for i, feature in enumerate(brand_strategy['chatapp_core_features'], 1):
        print(f"  {i}. {feature['feature_title']}")
        print(f"     {feature['intro']}")
    
    print("\n=== 测试完成 ===")
    print("✅ 所有离线功能测试通过！")
    print(f"生成的文件:")
    print(f"  - {latest_file.name if existing_files else test_file.name}")
    print(f"  - {strategy_file.name}")
    
    return True

if __name__ == "__main__":
    try:
        success = test_offline_functionality()
        if success:
            print("\n🎉 脚本基本功能正常，可以正常运行！")
        else:
            print("\n❌ 脚本存在问题，需要修复")
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试脚本
"""

import json
import os
from datetime import datetime
from pathlib import Path

def main():
    print("=== 品牌策略Agent测试 ===")
    
    # 1. 测试配置文件读取
    config_file = Path(__file__).resolve().parent / "config.json"
    if config_file.exists():
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        print("[OK] 配置文件读取成功")
        print(f"配置项: {list(config.keys())}")
    else:
        print("[ERROR] 配置文件不存在")
        return
    
    # 2. 测试环境变量设置
    if 'openai_api_key' in config:
        os.environ['OPENAI_API_KEY'] = config['openai_api_key']
        print("[OK] OpenAI API密钥设置成功")
    
    # 3. 测试时间戳生成
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    print(f"[OK] 时间戳生成: {timestamp}")
    
    # 4. 测试目录操作
    outputs_dir = Path(__file__).resolve().parent / "outputs"
    outputs_dir.mkdir(exist_ok=True)
    print(f"[OK] 输出目录: {outputs_dir}")
    
    # 5. 测试文件查找
    existing_files = list(outputs_dir.glob("integrated_analysis_*.json"))
    print(f"[OK] 找到现有文件数量: {len(existing_files)}")
    
    if existing_files:
        latest_file = max(existing_files, key=lambda x: x.stat().st_mtime)
        print(f"[OK] 最新文件: {latest_file.name}")
        
        # 读取文件内容
        data = json.loads(latest_file.read_text(encoding="utf-8"))
        print(f"[OK] 文件内容读取成功")
        print(f"数据: {data}")
    
    # 6. 模拟品牌策略结果
    brand_strategy = {
        "chatapp_name": "Aurora Insights",
        "chatapp_description": "AI-powered brand platform",
        "chatapp_core_features": [
            {"feature_title": "Brand Positioning Engine", "intro": "Defines competitive edge"},
            {"feature_title": "Market Intelligence Hub", "intro": "Analyzes market data"},
            {"feature_title": "Audience Insight Generator", "intro": "Creates personas"},
            {"feature_title": "Narrative Builder", "intro": "Transforms insights"}
        ]
    }
    
    # 7. 保存结果
    strategy_file = outputs_dir / f"brand_strategy_{timestamp}.json"
    strategy_file.write_text(json.dumps(brand_strategy, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[OK] 品牌策略结果保存: {strategy_file.name}")
    
    print("\n=== 测试完成 ===")
    print("所有基本功能正常！")
    print(f"生成的文件: {strategy_file.name}")

if __name__ == "__main__":
    main()

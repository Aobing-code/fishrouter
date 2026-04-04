#!/usr/bin/env python3
"""配置验证工具 - 检查 config.json 的完整性和后端可达性"""

import sys
import json
import requests
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import Config

def validate_config(filepath: str = "config.json"):
    """验证配置文件"""
    try:
        config = Config(filepath)
        print(f"✅ 配置文件有效: {filepath}")
    except Exception as e:
        print(f"❌ 配置错误: {e}")
        return 1

    # 检查后端连通性（可选，超时短）
    print("\n检查后端连通性...")
    for backend in config.backends:
        if not backend.enabled:
            continue
        url = backend.url.rstrip("/")
        try:
            # 尝试发送一个轻量级请求（如 /v1/models 或 /health）
            test_url = f"{url}/healthz"  # 有的后端有 /healthz
            resp = requests.get(test_url, timeout=3, headers={"Authorization": f"Bearer {backend.api_keys[0]}" if backend.api_keys else {}})
            if resp.status_code < 500:
                print(f"  ✅ {backend.name} ({url}) - 响应 {resp.status_code}")
            else:
                print(f"  ⚠️ {backend.name} ({url}) - 状态码 {resp.status_code}")
        except requests.RequestException as e:
            print(f"  ❌ {backend.name} ({url}) - 连接失败: {e}")

    print("\n✅ 验证完成")
    return 0

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "config.json"
    sys.exit(validate_config(path))

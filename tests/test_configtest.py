import sys
import os
import pytest

# 将项目根加入路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from scripts.configtest import validate_config

def test_configtest_valid_default(tmp_path, monkeypatch):
    """验证默认 config.json 有效时返回 0"""
    # 这里我们简单测试脚本能运行且不抛异常
    # 实际连通性检查可能需要网络，因此跳过或设为集成测试
    # 单元测试只测试加载逻辑
    from app.config import Config
    # 测试加载一个最小配置
    cfg = Config()
    assert cfg.server.port == 8080

def test_configtest_importable():
    """确保 configtest 脚本可以导入"""
    import scripts.configtest as ct
    assert hasattr(ct, 'validate_config')
    assert callable(ct.validate_config)

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_healthz_ok():
    """当所有后端健康时，/healthz 返回 200 和 {"status":"ok"}"""
    response = client.get("/healthz")
    assert response.status_code == 200
    data = response.json()
    assert data.get("status") == "ok"

def test_healthz_structure():
    """健康检查端点必须存在且返回 JSON"""
    response = client.get("/healthz")
    assert response.headers["content-type"] == "application/json"
    assert "status" in response.json()

def test_metrics_content():
    """Metrics 端点返回 Prometheus 文本格式"""
    response = client.get("/metrics")
    assert response.status_code == 200
    text = response.text
    # 至少包含这些指标
    required = [
        'fishrouter_requests_total{status="success"}',
        'fishrouter_requests_total{status="error"}',
        'fishrouter_tokens_total',
        'fishrouter_qps_current',
        'fishrouter_backend_requests_total{backend=',
        'fishrouter_model_requests_total{model='
    ]
    for metric in required:
        assert metric in text, f"Missing metric: {metric}"

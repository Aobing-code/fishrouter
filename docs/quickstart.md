# Quick Start - FishRouter

## 安装

### 从源码安装（开发）

```bash
git clone https://github.com/Aobing-code/fishrouter.git
cd fishrouter
pip install -r requirements.txt
cp config.example.json config.json
# 编辑 config.json 填入后端和 API Key
python -m app.main
```

### 使用 Docker（推荐）

```bash
# 构建镜像
docker build -t fishrouter:latest .

# 运行
docker run -d \
  --name fishrouter \
  -p 8080:8080 \
  -v $(pwd)/config.json:/app/config.json \
  fishrouter:latest
```

### Docker Compose

```bash
docker-compose up -d
```

---

## 配置说明

配置文件 `config.json` 主要字段：

```json
{
  "server": {
    "host": "0.0.0.0",
    "port": 8080,
    "workers": 4
  },
  "auth": {
    "enabled": true,
    "api_keys": ["your-api-key-here"]
  },
  "backends": [
    {
      "name": "openai",
      "type": "openai",
      "api_base": "https://api.openai.com/v1",
      "api_key": "sk-...",
      "priority": 1,
      "rate_limit": {
        "rpm": 1000,
        "tpm": 40000,
        "concurrent": 10
      }
    }
  ],
  "routes": [
    {
      "path": "/v1/chat/completions",
      "backend": "openai",
      "models": ["gpt-4", "gpt-3.5-turbo"]
    }
  ]
}
```

---

## 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/v1` | GET | API 根信息 |
| `/v1/chat/completions` | POST | 聊天补全（需 API Key） |
| `/v1/embeddings` | POST | 嵌入向量（需 API Key） |
| `/v1/models` | GET | 列出可用模型（需 API Key） |
| `/healthz` | GET | 健康检查（返回 `{"status":"ok"}`） |
| `/metrics` | GET | Prometheus 格式指标 |
| `/api/monitor/status` | GET | 监控状态页 |

---

## 测试

```bash
# 健康检查
curl http://localhost:8080/healthz

# 获取模型列表
curl -H "Authorization: Bearer your-api-key" \
     http://localhost:8080/v1/models

# 聊天请求
curl -X POST http://localhost:8080/v1/chat/completions \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4",
    "messages": [{"role":"user","content":"Hello!"}]
  }'
```

---

## 生产建议

- 使用 Nginx 反向代理并添加限流
- 开启配置热重载（`config_reload_middleware` 已内置）
- 通过 `/metrics` 集成 Prometheus + Grafana
- 使用 systemd 或 Kubernetes 部署

---


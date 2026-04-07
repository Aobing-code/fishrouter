# FishRouter

<div align="center">

**像鱼一样穿梭于API之间**

**Swimming through APIs like a fish**

**轻量级端侧AI总线 · 统一AI模型路由平台**

**Lightweight Edge AI Bus · Unified AI Model Routing Platform**

[![Python](https://img.shields.io/badge/Python-3.11+-green)](https://python.org)
[![Stars](https://img.shields.io/github/stars/Aobing-code/fishrouter?style=flat-square)](https://github.com/Aobing-code/fishrouter/stargazers)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

</div>

---

## 亮点特性 | Highlights

| Feature 特性 | Description 说明 |
|--------------|------------------|
| **全平台API统一** | 一个接口兼容 OpenAI、Claude、Gemini、Ollama |
| **Unified API** | One interface for OpenAI, Claude, Gemini, Ollama |
| **智能故障转移** | 速率限制预判、自动降级、多级回退 |
| **Smart Failover** | Rate limit prediction, auto degradation, multi-level fallback |
| **多Key轮询** | 每个提供商支持多个 API Key，自动负载均衡 |
| **Multi-Key Rotation** | Multiple API keys per provider with load balancing |
| **模型独立限速** | 每个模型可设置 RPM/TPM/并发数 |
| **Per-Model Rate Limit** | RPM/TPM/concurrent limits for each model |
| **多模态支持** | 图片、文本混合输入，Vision 全后端通用 |
| **Multimodal** | Image and text input, Vision across all backends |
| **工具调用** | Function Calling 跨平台统一 |
| **Tool Calling** | Unified Function Calling in OpenAI format |
| **零依赖部署** | 纯内存运行，无数据库，Docker 一键启动 |
| **Zero Dependencies** | In-memory, no database, Docker one-click deploy |
| **实时监控** | React 现代化 Web 面板，支持全平台 |
| **Real-time Monitor** | Modern React Web dashboard, cross-platform |

---

## 快速开始 | Quick Start

### Linux 一键安装 | Linux One-Click Install

```bash
curl -sSL https://raw.githubusercontent.com/Aobing-code/fishrouter/main/install.sh | sudo bash
```

安装后管理 | Post-Install Management:

```bash
# 查看状态
sudo systemctl status fishrouter

# 查看日志
sudo journalctl -u fishrouter -f

# 重启服务
sudo systemctl restart fishrouter

# 编辑配置
sudo nano /opt/fishrouter/config.json

# 卸载
sudo systemctl stop fishrouter
sudo systemctl disable fishrouter
sudo rm -rf /opt/fishrouter /etc/systemd/system/fishrouter.service
sudo systemctl daemon-reload
```

### Docker 部署 | Docker Deploy

```bash
docker run -d -p 8080:8080 \
  -v ./config.json:/app/config.json \
  fishrouter
```

### 源码运行 | From Source

```bash
pip install -r requirements.txt
python -m app.main
```

### Windows 部署 | Windows Deploy

**方式一：安装包安装 | Option 1: Installer**
1. 下载 `FishRouter-Setup.msi` 从 [Releases](https://github.com/Aobing-code/fishrouter/releases)
2. 双击安装，自动创建桌面快捷方式和开始菜单
3. 打开 FishRouter，通过 Web 面板管理所有配置

**方式二：便携版 | Option 2: Portable**
1. 下载 `FishRouter-Windows-Portable.zip`
2. 解压到任意目录
3. 双击 `FishRouter.exe` 直接运行

> Windows 客户端启动后会自动打开内置浏览器窗口，访问 `http://localhost:8080`

---

## 核心功能 | Core Features

### 1. 统一API入口 | Unified API

所有后端使用相同的 OpenAI 格式：

```bash
# 调用 OpenAI
curl -X POST http://localhost:8080/v1/chat/completions \
  -d '{"model": "gpt-4", "messages": [...]}'

# 调用 Claude
curl -X POST http://localhost:8080/v1/chat/completions \
  -d '{"model": "claude-sonnet", "messages": [...]}'

# 调用 Gemini
curl -X POST http://localhost:8080/v1/chat/completions \
  -d '{"model": "gemini-pro", "messages": [...]}'

# 调用本地 Ollama
curl -X POST http://localhost:8080/v1/chat/completions \
  -d '{"model": "llama3", "messages": [...]}'
```

### 2. 智能路由 | Smart Routing

```bash
# 直接指定模型（失败后自动回退）
curl -d '{"model": "gpt-4", ...}'

# 使用指定路由策略
curl -d '{"model": "back-default", ...}'
curl -d '{"model": "back-cheap", ...}'
curl -d '{"model": "back-fast", ...}'
```

### 3. 工具调用 | Tool Calling

```json
{
  "model": "gpt-4",
  "messages": [{"role": "user", "content": "北京天气"}],
  "tools": [{
    "type": "function",
    "function": {
      "name": "get_weather",
      "description": "获取天气",
      "parameters": {
        "type": "object",
        "properties": {
          "city": {"type": "string"}
        }
      }
    }
  }],
  "tool_choice": "auto"
}
```

### 4. 多模态 Vision | Multimodal

```json
{
  "model": "gpt-4",
  "messages": [{
    "role": "user",
    "content": [
      {"type": "text", "text": "这是什么？"},
      {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,..."}}
    ]
  }]
}
```

---

## 路由策略 | Routing Strategy

| 策略 | 说明 | Description |
|------|------|-------------|
| `latency` | 选择延迟最低的后端（默认） | Select lowest latency (default) |
| `round_robin` | 轮询分发 | Round-robin distribution |
| `random` | 随机选择 | Random selection |
| `weighted` | 按权重分发 | Weighted distribution |
| `priority` | 按优先级选择 | Priority-based selection |
| `custom` | 自定义回退顺序 | Custom fallback order |

## 故障转移 | Failover

| 条件 | 说明 | Description |
|------|------|-------------|
| `rate_limit` | 触发速率限制时自动转移 | Auto transfer on rate limit |
| `error` | 错误次数超过阈值时转移 | Transfer on error threshold |
| `latency` | 延迟超过阈值时转移 | Transfer on latency threshold |
| `timeout` | 请求超时时转移 | Transfer on timeout |

## 支持的后端 | Supported Backends

| Backend 后端 | Type 类型 | Tool Calling | Multimodal |
|--------------|-----------|-------------|------------|
| OpenAI / Azure / Compatible | `openai` | ✅ | ✅ |
| Anthropic Claude | `anthropic` | ✅ | ✅ |
| Google Gemini | `google` | ✅ | ✅ |
| Ollama | `ollama` | ✅ | ✅ |

---

## 配置说明 | Configuration

### 完整配置示例 | Full Config Example

```json
{
  "server": {
    "host": "0.0.0.0",
    "port": 8080
  },
  "backends": [
    {
      "name": "ollama-local",
      "type": "ollama",
      "url": "http://localhost:11434",
      "api_keys": [],
      "weight": 10,
      "priority": 1,
      "timeout": 120,
      "verify_ssl": false,
      "models": [
        {
          "id": "llama3",
          "name": "llama3",
          "context_length": 8192,
          "rate_limit": {"rpm": 30, "tpm": 50000, "concurrent": 3}
        }
      ],
      "rate_limit": {"rpm": 0, "tpm": 0, "concurrent": 10}
    },
    {
      "name": "openai",
      "type": "openai",
      "url": "https://api.openai.com/v1",
      "api_keys": ["sk-key1", "sk-key2", "sk-key3"],
      "weight": 5,
      "priority": 2,
      "models": [
        {"id": "gpt-4", "name": "gpt-4-turbo", "context_length": 128000},
        {"id": "gpt-4-mini", "name": "gpt-4o-mini", "context_length": 16384}
      ],
      "rate_limit": {"rpm": 1000, "tpm": 1000000, "concurrent": 20}
    },
    {
      "name": "anthropic",
      "type": "anthropic",
      "url": "https://api.anthropic.com",
      "api_keys": ["sk-ant-key1", "sk-ant-key2"],
      "models": [
        {"id": "claude-sonnet", "name": "claude-3-5-sonnet-20241022", "context_length": 200000}
      ]
    },
    {
      "name": "google",
      "type": "google",
      "url": "https://generativelanguage.googleapis.com",
      "api_keys": ["gemini-key1"],
      "models": [
        {"id": "gemini-pro", "name": "gemini-1.5-pro", "context_length": 1000000}
      ]
    }
  ],
  "routes": [
    {
      "name": "default",
      "models": ["*"],
      "strategy": "latency",
      "failover": true,
      "fallback_order": ["ollama-local", "openai", "anthropic"],
      "fallback_rules": [
        {"name": "rate-limit", "condition": "rate_limit", "backends": ["openai", "anthropic"]},
        {"name": "error", "condition": "error", "threshold": 3, "backends": ["anthropic"]},
        {"name": "latency", "condition": "latency", "threshold": 10.0, "backends": ["anthropic"]}
      ]
    }
  ],
  "auth": {
    "enabled": false,
    "api_keys": ["sk-fishrouter"]
  }
}
```

---

## 项目结构 | Project Structure

```
fishrouter/
├── app/
│   ├── main.py           # 主入口 | Main entry
│   ├── config.py         # 配置管理 | Config management
│   ├── api/
│   │   ├── chat.py       # Chat Completions
│   │   ├── embeddings.py # Embeddings
│   │   ├── models.py     # Models
│   │   ├── monitor.py    # 监控API | Monitor API
│   │   └── config.py     # 配置API | Config API
│   ├── backends/
│   │   ├── base.py       # 后端基类 | Backend base
│   │   ├── openai.py     # OpenAI 兼容
│   │   ├── anthropic.py  # Anthropic Claude
│   │   ├── google.py     # Google Gemini
│   │   └── ollama.py     # Ollama
│   ├── core/
│   │   ├── balancer.py   # 负载均衡 | Load balancer
│   │   ├── ratelimit.py  # 速率限制 | Rate limiter
│   │   ├── auth.py       # API Key 认证
│   │   └── stats.py      # 统计追踪 | Statistics
│   └── web/
│       └── dashboard.py  # 静态文件服务 | Static file serving
├── frontend/             # React 前端 | React frontend
│   ├── src/
│   │   ├── App.tsx       # 路由入口 | Router entry
│   │   └── pages/        # 页面组件 | Page components
│   ├── vite.config.ts    # Vite 配置
│   └── package.json
├── static/               # 构建产物 | Build output
│   └── dist/
│       ├── index.html
│       └── assets/
├── config.example.json   # 示例配置 | Example config
├── Dockerfile
├── docker-compose.yml
├── launcher.py           # Windows 客户端 | Windows client
├── launcher.spec         # PyInstaller 配置
├── server.spec           # PyInstaller 配置
└── requirements.txt
```

---

## 下载 | Downloads

| 平台 Platform | 文件 File | 说明 Description |
|---------------|-----------|------------------|
| 🪟 Windows | `FishRouter-Setup.msi` | 安装包 Installer |
| 🪟 Windows | `FishRouter-Windows-Portable.zip` | 便携版 Portable |
| 🐧 Linux | `install.sh` 一键脚本 | 自动下载 + systemd 服务 |
| 🐧 Linux | `fishrouter-server-linux-amd64.tar.gz` | 服务端二进制 |
| 🍎 macOS ARM64 | `fishrouter-server-macos-arm64.tar.gz` | Apple Silicon |

> **管理方式 | Management:**
> - **全平台**: Web UI → `http://localhost:8080`
> - **Windows**: 客户端自动打开内置浏览器窗口

---

## Star History

<a href="https://www.star-history.com/?repos=Aobing-code%2Ffishrouter&type=date&legend=top-left">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/image?repos=Aobing-code/fishrouter&type=date&theme=dark&legend=top-left" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/image?repos=Aobing-code/fishrouter&type=date&legend=top-left" />
   <img alt="Star History Chart" src="https://api.star-history.com/image?repos=Aobing-code/fishrouter&type=date&legend=top-left" />
 </picture>
</a>

---

## License

MIT

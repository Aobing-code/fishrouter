"""Common API Platform Presets"""

API_PLATFORMS = [
    {
        "name": "OpenAI",
        "type": "openai",
        "url": "https://api.openai.com/v1",
        "icon": "🟢",
        "description": "GPT-4, GPT-3.5, DALL-E, Whisper",
        "models_url": "/models",
        "auth_type": "bearer",
        "docs_url": "https://platform.openai.com/docs/api-reference"
    },
    {
        "name": "Azure OpenAI",
        "type": "openai",
        "url": "https://{resource}.openai.azure.com/openai",
        "icon": "🔵",
        "description": "Azure-hosted OpenAI models",
        "models_url": "/deployments?api-version=2022-12-01",
        "auth_type": "api-key",
        "docs_url": "https://learn.microsoft.com/azure/ai-services/openai/"
    },
    {
        "name": "Anthropic Claude",
        "type": "anthropic",
        "url": "https://api.anthropic.com",
        "icon": "🟣",
        "description": "Claude 3.5 Sonnet, Haiku, Opus",
        "models_url": "/v1/models",
        "auth_type": "x-api-key",
        "docs_url": "https://docs.anthropic.com/claude/reference"
    },
    {
        "name": "Google Gemini",
        "type": "google",
        "url": "https://generativelanguage.googleapis.com",
        "icon": "🔴",
        "description": "Gemini 1.5 Pro, Flash, Embeddings",
        "models_url": "/v1beta/models",
        "auth_type": "query-param",
        "docs_url": "https://ai.google.dev/docs"
    },
    {
        "name": "Ollama (本地)",
        "type": "ollama",
        "url": "http://localhost:11434",
        "icon": "🦙",
        "description": "本地运行 Llama, Qwen, Mistral 等",
        "models_url": "/api/tags",
        "auth_type": "none",
        "docs_url": "https://ollama.ai"
    },
    {
        "name": "DeepSeek",
        "type": "openai",
        "url": "https://api.deepseek.com",
        "icon": "🐋",
        "description": "DeepSeek-V3, DeepSeek-R1",
        "models_url": "/models",
        "auth_type": "bearer",
        "docs_url": "https://platform.deepseek.com"
    },
    {
        "name": "SiliconFlow (硅基流动)",
        "type": "openai",
        "url": "https://api.siliconflow.cn/v1",
        "icon": "🔶",
        "description": "国内可用，支持多种开源模型",
        "models_url": "/models",
        "auth_type": "bearer",
        "docs_url": "https://cloud.siliconflow.cn"
    },
    {
        "name": "OpenRouter",
        "type": "openai",
        "url": "https://openrouter.ai/api/v1",
        "icon": "🌐",
        "description": "聚合多种模型，支持免费模型",
        "models_url": "/models",
        "auth_type": "bearer",
        "docs_url": "https://openrouter.ai/docs"
    },
    {
        "name": "智谱 AI (Zhipu)",
        "type": "openai",
        "url": "https://open.bigmodel.cn/api/paas/v4",
        "icon": "🧠",
        "description": "GLM-4, GLM-3-Turbo, CogView",
        "models_url": "/models",
        "auth_type": "bearer",
        "docs_url": "https://open.bigmodel.cn/dev/api"
    },
    {
        "name": "通义千问 (DashScope)",
        "type": "openai",
        "url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "icon": "💎",
        "description": "Qwen-Max, Qwen-Plus, Qwen-Turbo",
        "models_url": "/models",
        "auth_type": "bearer",
        "docs_url": "https://help.aliyun.com/zh/dashscope"
    },
    {
        "name": "Moonshot (月之暗面)",
        "type": "openai",
        "url": "https://api.moonshot.cn/v1",
        "icon": "🌙",
        "description": "Moonshot-V1-8K/32K/128K",
        "models_url": "/models",
        "auth_type": "bearer",
        "docs_url": "https://platform.moonshot.cn/docs"
    },
    {
        "name": "MiniMax",
        "type": "openai",
        "url": "https://api.minimax.chat/v1",
        "icon": "🤖",
        "description": "abab6, abab5.5 系列",
        "models_url": "/models",
        "auth_type": "bearer",
        "docs_url": "https://platform.minimaxi.com"
    },
    {
        "name": "百川智能 (Baichuan)",
        "type": "openai",
        "url": "https://api.baichuan-ai.com/v1",
        "icon": "🌊",
        "description": "Baichuan2-Turbo, Baichuan3-Turbo",
        "models_url": "/models",
        "auth_type": "bearer",
        "docs_url": "https://platform.baichuan-ai.com"
    },
    {
        "name": "零一万物 (Yi)",
        "type": "openai",
        "url": "https://api.lingyiwanwu.com/v1",
        "icon": "🌟",
        "description": "Yi-Large, Yi-Medium, Yi-Sparks",
        "models_url": "/models",
        "auth_type": "bearer",
        "docs_url": "https://platform.lingyiwanwu.com"
    },
    {
        "name": "vLLM (自部署)",
        "type": "openai",
        "url": "http://localhost:8000/v1",
        "icon": "⚡",
        "description": "自部署 vLLM 服务",
        "models_url": "/models",
        "auth_type": "bearer",
        "docs_url": "https://docs.vllm.ai"
    },
    {
        "name": "LM Studio (本地)",
        "type": "openai",
        "url": "http://localhost:1234/v1",
        "icon": "🏠",
        "description": "本地 LM Studio 服务",
        "models_url": "/models",
        "auth_type": "none",
        "docs_url": "https://lmstudio.ai"
    },
    {
        "name": "Groq",
        "type": "openai",
        "url": "https://api.groq.com/openai/v1",
        "icon": "⚡",
        "description": "超快速推理，Llama, Mixtral, Gemma",
        "models_url": "/models",
        "auth_type": "bearer",
        "docs_url": "https://console.groq.com/docs"
    },
    {
        "name": "Together AI",
        "type": "openai",
        "url": "https://api.together.xyz/v1",
        "icon": "🔗",
        "description": "多种开源模型托管服务",
        "models_url": "/models",
        "auth_type": "bearer",
        "docs_url": "https://docs.together.ai"
    },
    {
        "name": "NVIDIA NIM",
        "type": "openai",
        "url": "https://integrate.api.nvidia.com/v1",
        "icon": "🟩",
        "description": "NVIDIA 加速的推理服务",
        "models_url": "/models",
        "auth_type": "bearer",
        "docs_url": "https://build.nvidia.com"
    },
    {
        "name": "Mistral AI",
        "type": "openai",
        "url": "https://api.mistral.ai/v1",
        "icon": "💨",
        "description": "Mistral Large, Small, Codestral",
        "models_url": "/models",
        "auth_type": "bearer",
        "docs_url": "https://docs.mistral.ai"
    },
]


def get_platform_by_name(name):
    """Get platform config by name"""
    for p in API_PLATFORMS:
        if p["name"] == name:
            return p
    return None


def get_platform_names():
    """Get list of platform names"""
    return [p["name"] for p in API_PLATFORMS]

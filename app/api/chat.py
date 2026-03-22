"""Chat Completions API端点"""
import time
import json
from typing import Dict, List, Any, Optional, Tuple
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from app.core import stats, rate_limiter

import logging
logger = logging.getLogger("openfish.api.chat")

router = APIRouter()

# 上下文升级追踪器
# 格式: {session_key: {"count": int, "original_model": str}}
context_upgrade_tracker: Dict[str, Dict] = {}

# 追踪器清理间隔（秒）
TRACKER_CLEANUP_INTERVAL = 300
_last_cleanup = time.time()


def get_app():
    from app import main as app_main
    return app_main


def get_session_key(request: Request) -> str:
    """获取会话标识（使用API Key或IP）"""
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        return f"key:{auth[7:]}"
    return f"ip:{request.client.host if request.client else 'unknown'}"


def cleanup_tracker():
    """清理过期的追踪记录"""
    global _last_cleanup, context_upgrade_tracker
    now = time.time()
    if now - _last_cleanup > TRACKER_CLEANUP_INTERVAL:
        # 清理超过5分钟的记录
        expired = [k for k, v in context_upgrade_tracker.items() 
                   if now - v.get("timestamp", 0) > 300]
        for k in expired:
            del context_upgrade_tracker[k]
        _last_cleanup = now


def parse_model_field(model: str, config) -> Tuple[str, Optional[object]]:
    """
    解析model字段
    返回: (实际model_id, 路由配置)
    """
    if model.startswith("back-"):
        route_name = model[5:]
        for route in config.routes:
            if route.name == route_name:
                return "*", route
        return "*", config.routes[0] if config.routes else None
    else:
        return model, config.routes[0] if config.routes else None


def find_backends_for_model(model_id: str, config, backends: dict) -> List:
    """查找支持指定模型的后端"""
    if model_id == "*":
        return [b for b in backends.values() if b.status.healthy]
    
    available = []
    for backend in backends.values():
        if not backend.status.healthy:
            continue
        backend_config = config.get_backend_by_name(backend.name)
        if backend_config:
            for m in backend_config.models:
                if m.id == "*" or m.id == model_id:
                    if m.enabled:
                        available.append(backend)
                        break
    return available


def find_larger_context_model(app, current_model_id: str, current_context: int) -> Optional[Tuple[str, str, int]]:
    """查找更大context的模型，返回 (model_id, backend_name, context_length)"""
    best_model = None
    best_context = current_context

    for backend in app.backends.values():
        if not backend.status.healthy:
            continue
        backend_config = app.config.get_backend_by_name(backend.name)
        if backend_config:
            for m in backend_config.models:
                if m.enabled and m.context_length > best_context:
                    best_model = (m.id, backend.name, m.context_length)
                    best_context = m.context_length

    return best_model


def extract_request_params(body: Dict) -> Dict[str, Any]:
    """提取请求参数"""
    params = {}
    for key in ["temperature", "max_tokens", "top_p", "frequency_penalty", 
                "presence_penalty", "stop", "n", "seed", "response_format",
                "tools", "tool_choice", "functions", "function_call",
                "logprobs", "top_logprobs"]:
        if key in body and body[key] is not None:
            params[key] = body[key]
    return params


@router.post("/v1/chat/completions")
async def chat_completions(request: Request):
    """OpenAI兼容的chat/completions端点"""
    app = get_app()
    session_key = get_session_key(request)

    # 清理过期追踪记录
    cleanup_tracker()

    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    raw_model = body.get("model", "")
    messages = body.get("messages", [])
    stream = body.get("stream", False)

    if not raw_model:
        raise HTTPException(status_code=400, detail="Model is required")
    if not messages:
        raise HTTPException(status_code=400, detail="Messages are required")

    # 解析model字段
    model_id, route = parse_model_field(raw_model, app.config)

    # 查找可用后端
    if model_id == "*" and route:
        available_backends = []
        for backend_name in route.fallback_order if route.fallback_order else [b.name for b in app.config.backends if b.enabled]:
            if backend_name in app.backends and app.backends[backend_name].status.healthy:
                available_backends.append(app.backends[backend_name])
        if not available_backends:
            available_backends = [b for b in app.backends.values() if b.status.healthy]
    else:
        available_backends = find_backends_for_model(model_id, app.config, app.backends)

    if not available_backends:
        raise HTTPException(
            status_code=503,
            detail=f"No healthy backend available for model: {raw_model}"
        )

    # 获取路由配置
    strategy = route.strategy if route else "latency"
    fallback_order = route.fallback_order if route else []
    fallback_rules = route.fallback_rules if route else []

    # 估算tokens
    estimated_tokens = sum(len(str(m.get("content", ""))) for m in messages) // 4

    # 检查是否需要自动升级到更大context的模型
    tracker_info = context_upgrade_tracker.get(session_key)
    if tracker_info and tracker_info.get("count", 0) == 1:
        # 第二次请求：自动路由到更大context的模型
        larger_model = tracker_info.get("upgrade_to")
        if larger_model:
            model_id = larger_model[0]
            # 更新追踪状态
            tracker_info["count"] = 2
            tracker_info["timestamp"] = time.time()
            # 重新查找后端
            available_backends = find_backends_for_model(model_id, app.config, app.backends)
    elif tracker_info and tracker_info.get("count", 0) >= 2:
        # 第三次请求：恢复原模型，清除追踪
        model_id = tracker_info.get("original_model", model_id)
        del context_upgrade_tracker[session_key]
        available_backends = find_backends_for_model(model_id, app.config, app.backends)

    # 检查上下文长度是否超过80%
    backend_config = app.config.get_backend_by_name(available_backends[0].name) if available_backends else None
    current_context = 0
    
    if backend_config and model_id != "*":
        for m in backend_config.models:
            if m.id == model_id:
                current_context = m.context_length
                if current_context > 0:
                    usage_ratio = estimated_tokens / current_context
                    if usage_ratio > 0.8:
                        # 查找更大context的模型
                        larger = find_larger_context_model(app, model_id, current_context)
                        
                        # 记录追踪信息
                        context_upgrade_tracker[session_key] = {
                            "count": 1,
                            "original_model": model_id,
                            "upgrade_to": larger,
                            "timestamp": time.time()
                        }
                        
                        if larger:
                            raise HTTPException(
                                status_code=400,
                                detail=f"context used {int(usage_ratio * 100)}%, will auto-route to {larger[0]} ({larger[2]} tokens) next time"
                            )
                        else:
                            raise HTTPException(
                                status_code=400,
                                detail=f"context used {int(usage_ratio * 100)}%"
                            )
                break

    # 选择后端
    selected_backend = None
    tried_backends = []

    for backend in available_backends:
        if backend in tried_backends:
            continue
        if not await rate_limiter.can_request(backend.name, estimated_tokens):
            tried_backends.append(backend)
            continue
        if rate_limiter.is_near_limit(backend.name, threshold=0.8):
            tried_backends.append(backend)
            continue
        selected_backend = backend
        break

    # 回退规则
    if not selected_backend and fallback_rules:
        for rule in fallback_rules:
            if rule.condition in ["rate_limit", "error"]:
                for backend_name in rule.backends:
                    if backend_name in app.backends:
                        backend = app.backends[backend_name]
                        if backend.status.healthy and await rate_limiter.can_request(backend.name, estimated_tokens):
                            selected_backend = backend
                            break
            if selected_backend:
                break

    # 回退顺序
    if not selected_backend and fallback_order:
        for name in fallback_order:
            if name in app.backends:
                backend = app.backends[name]
                if backend.status.healthy and await rate_limiter.can_request(backend.name, estimated_tokens):
                    selected_backend = backend
                    break

    # 最后选择
    if not selected_backend:
        for backend in available_backends:
            if backend not in tried_backends:
                selected_backend = backend
                break

    if not selected_backend:
        raise HTTPException(status_code=503, detail="All backends are rate limited or unavailable")

    # 获取实际模型名称
    backend_config = app.config.get_backend_by_name(selected_backend.name)
    actual_model = model_id
    if backend_config and model_id != "*":
        for m in backend_config.models:
            if m.id == model_id:
                actual_model = m.name
                break
    elif backend_config and model_id == "*":
        for m in backend_config.models:
            if m.enabled:
                actual_model = m.name
                break

    # 提取请求参数
    request_params = extract_request_params(body)

    # 获取速率限制许可
    await rate_limiter.acquire(selected_backend.name, estimated_tokens)

    start_time = time.time()

    try:
        if stream:
            return StreamingResponse(
                stream_chat_completion(selected_backend, actual_model, messages, request_params, start_time),
                media_type="text/event-stream"
            )
        else:
            result = await selected_backend.chat_completion(
                model=actual_model,
                messages=messages,
                stream=False,
                **request_params
            )

            latency = time.time() - start_time
            tokens = result.get("usage", {}).get("total_tokens", 0)
            await stats.record(raw_model, selected_backend.name, tokens, latency, True)

            return result

    except Exception as e:
        latency = time.time() - start_time
        await stats.record(raw_model, selected_backend.name, 0, latency, False)
        logger.error(f"Chat completion error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        rate_limiter.release(selected_backend.name)


async def stream_chat_completion(backend, model: str, messages: List[Dict], params: Dict, start_time: float):
    """流式响应"""
    try:
        async for chunk in backend.chat_completion_stream(
            model=model,
            messages=messages,
            **params
        ):
            yield f"data: {json.dumps(chunk)}\n\n"

        yield "data: [DONE]\n\n"

        latency = time.time() - start_time
        await stats.record(model, backend.name, 0, latency, True)

    except Exception as e:
        latency = time.time() - start_time
        await stats.record(model, backend.name, 0, latency, False)
        logger.error(f"Stream error: {e}")
        error_chunk = {"error": {"message": str(e), "type": "server_error"}}
        yield f"data: {json.dumps(error_chunk)}\n\n"
    finally:
        rate_limiter.release(backend.name)

"""Web监控面板"""
import hashlib
import secrets
import time
from pathlib import Path
from typing import Dict
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from pydantic import BaseModel

import logging
logger = logging.getLogger("fishrouter.web")

router = APIRouter()

# Session存储 {token: expire_time}
sessions: Dict[str, float] = {}

# Session过期时间（秒）
SESSION_EXPIRE = 86400  # 24小时


def get_static_dir() -> Path:
    """获取静态文件目录"""
    possible_paths = [
        Path("/app/static"),
        Path(__file__).parent.parent.parent / "static",
        Path.cwd() / "static",
    ]
    for p in possible_paths:
        if p.exists() and (p / "index.html").exists():
            return p
    return possible_paths[0]


def get_app():
    from app import main as app_main
    return app_main


def verify_session(token: str) -> bool:
    """验证session是否有效"""
    if not token:
        return False
    expire = sessions.get(token)
    if not expire:
        return False
    if time.time() > expire:
        sessions.pop(token, None)
        return False
    return True


def get_session_token(request: Request) -> str:
    """从请求中获取session token"""
    # 从cookie获取
    token = request.cookies.get("fishrouter_session")
    if token:
        return token
    # 从header获取
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Session "):
        return auth[8:]
    return ""


class LoginRequest(BaseModel):
    password: str


@router.get("/login", response_class=HTMLResponse)
async def login_page():
    """登录页面"""
    static_dir = get_static_dir()
    login_file = static_dir / "login.html"
    if login_file.exists():
        return FileResponse(login_file)
    return HTMLResponse("<h1>Login page not found</h1>")


@router.post("/api/login")
async def login(body: LoginRequest):
    """登录API"""
    app = get_app()
    
    # 验证密码（使用第一个API key作为管理员密码）
    valid_keys = app.config.auth.api_keys if app.config.auth.enabled else ["sk-fishrouter"]
    
    if body.password in valid_keys:
        # 生成session token
        token = secrets.token_hex(32)
        sessions[token] = time.time() + SESSION_EXPIRE
        
        response = JSONResponse({"status": "ok", "message": "登录成功"})
        response.set_cookie(
            key="fishrouter_session",
            value=token,
            max_age=SESSION_EXPIRE,
            httponly=True,
            samesite="lax"
        )
        return response
    
    raise HTTPException(status_code=401, detail="密码错误")


@router.post("/api/logout")
async def logout(request: Request):
    """登出API"""
    token = get_session_token(request)
    if token:
        sessions.pop(token, None)
    
    response = JSONResponse({"status": "ok", "message": "已登出"})
    response.delete_cookie("fishrouter_session")
    return response


@router.get("/api/session/check")
async def check_session(request: Request):
    """检查session状态"""
    token = get_session_token(request)
    if verify_session(token):
        return {"authenticated": True}
    return {"authenticated": False}


@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """监控面板首页"""
    app = get_app()
    
    # 如果启用了认证，检查session
    if app.config.auth.enabled:
        token = get_session_token(request)
        if not verify_session(token):
            # 重定向到登录页
            static_dir = get_static_dir()
            login_file = static_dir / "login.html"
            if login_file.exists():
                return FileResponse(login_file)
    
    static_dir = get_static_dir()
    # 优先使用 React 构建的 dist/index.html
    dist_index = static_dir / "dist" / "index.html"
    if dist_index.exists():
        return FileResponse(dist_index)
    index_file = static_dir / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return HTMLResponse("<h1>OpenFish</h1><p>Dashboard not found</p>")


@router.get("/assets/{filename:path}")
async def serve_assets(filename: str):
    """服务 React 构建的 JS/CSS 资源"""
    static_dir = get_static_dir()
    file_path = static_dir / "dist" / "assets" / filename
    if file_path.exists() and file_path.is_file():
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="Asset not found")


@router.get("/favicon.ico")
async def serve_favicon_ico():
    """服务 favicon.ico"""
    static_dir = get_static_dir()
    favicon = static_dir / "favicon.ico"
    if favicon.exists():
        return FileResponse(favicon, media_type="image/x-icon")
    raise HTTPException(status_code=404, detail="Favicon not found")


@router.get("/favicon.svg")
async def serve_favicon_svg():
    """服务 favicon.svg"""
    static_dir = get_static_dir()
    for ext in [".svg", ".ico"]:
        favicon = static_dir / f"favicon{ext}"
        if favicon.exists():
            return FileResponse(favicon)
    raise HTTPException(status_code=404, detail="Favicon not found")


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_alt(request: Request):
    """监控面板（备用路径）"""
    return await dashboard(request)


@router.get("/{full_path:path}", response_class=HTMLResponse)
async def catch_all(request: Request, full_path: str):
    """Catch-all 路由，支持 React 客户端路由"""
    path = request.url.path
    
    # 不拦截 API 路径
    if path.startswith("/api/") or path.startswith("/v1/"):
        raise HTTPException(status_code=404, detail="Not found")
    
    # 不拦截 assets 路径
    if path.startswith("/assets/"):
        raise HTTPException(status_code=404, detail="Not found")
    
    # 返回 React 入口
    static_dir = get_static_dir()
    dist_index = static_dir / "dist" / "index.html"
    if dist_index.exists():
        return FileResponse(dist_index)
    raise HTTPException(status_code=404, detail="Not found")


@router.get("/api/config")
async def get_config_api():
    """获取完整配置（脱敏）"""
    app = get_app()
    
    def backend_to_dict(b):
        return {
            "name": b.name,
            "type": b.type,
            "url": b.url,
            "model": b.model,
            "enabled": b.enabled,
        }
    
    return {
        "server": {
            "host": app.config.server.host,
            "port": app.config.server.port,
            "log_level": app.config.server.log_level,
        },
        "auth": {
            "enabled": app.config.auth.enabled,
            "api_keys": ["***"],  # 脱敏
        },
        "backends": [backend_to_dict(b) for b in app.config.backends],
        "routes": [
            {
                "name": r.name,
                "models": r.models,
                "strategy": r.strategy,
                "failover": r.failover,
            } for r in app.config.routes
        ],
    }


@router.put("/api/config")
async def update_config_api(request: Request):
    """更新配置（部分更新支持）"""
    app = get_app()
    data = await request.json()
    
    # 更新服务器配置
    if "server" in data:
        s = data["server"]
        if "host" in s:
            app.config.server.host = s["host"]
        if "port" in s:
            app.config.server.port = int(s["port"])
        if "log_level" in s:
            app.config.server.log_level = s["log_level"]
    
    # 更新认证配置
    if "auth" in data:
        a = data["auth"]
        if "enabled" in a:
            app.config.auth.enabled = a["enabled"]
    
    # 更新后端列表（完全替换）
    if "backends" in data:
        from app.config import BackendConfig
        new_backends = []
        for b_data in data["backends"]:
            new_backends.append(BackendConfig(**b_data))
        app.config.backends = new_backends
    
    # 更新路由配置
    if "routes" in data:
        from app.config import RouteConfig
        new_routes = []
        for r_data in data["routes"]:
            new_routes.append(RouteConfig(**r_data))
        app.config.routes = new_routes
    
    app.config.save()
    # 重新初始化后端
    await app.init_backends()
    return {"status": "ok", "message": "配置已保存并重新加载"}


@router.get("/api/logs")
async def get_logs_api(lines: int = 100):
    """获取最近日志"""
    try:
        log_file = Path("logs/fishrouter.log")
        if log_file.exists():
            with open(log_file, "r", encoding="utf-8") as f:
                all_lines = f.readlines()
                last_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
                return {"logs": [line.rstrip('\n') for line in last_lines]}
        else:
            return {"logs": ["日志文件尚未创建"]}
    except Exception as e:
        return {"logs": [f"读取日志失败: {e}"]}

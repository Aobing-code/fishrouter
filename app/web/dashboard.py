"""Web监控面板 - 仅服务 React 构建产物"""
import secrets
import sys
import time
from pathlib import Path
from typing import Dict
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from pydantic import BaseModel

import logging
logger = logging.getLogger("fishrouter.web")

router = APIRouter()

sessions: Dict[str, float] = {}
SESSION_EXPIRE = 86400


def get_static_dir() -> Path:
    possible_paths = []
    possible_paths.append(Path.cwd() / "static")
    if getattr(sys, 'frozen', False):
        base_dir = Path(sys.executable).parent
        possible_paths.append(base_dir / "static")
    possible_paths.extend([
        Path(__file__).parent.parent.parent / "static",
        Path("/app/static"),
    ])
    for p in possible_paths:
        if p.exists():
            return p
    return possible_paths[0]


def get_dist_index() -> Path:
    static_dir = get_static_dir()
    return static_dir / "dist" / "index.html"


def get_app():
    from app import main as app_main
    return app_main


def verify_session(token: str) -> bool:
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
    token = request.cookies.get("fishrouter_session")
    if token:
        return token
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Session "):
        return auth[8:]
    return ""


class LoginRequest(BaseModel):
    password: str


@router.get("/api/session/check")
async def check_session(request: Request):
    token = get_session_token(request)
    if verify_session(token):
        return {"authenticated": True}
    return {"authenticated": False}


@router.post("/api/login")
async def login(body: LoginRequest):
    app = get_app()
    valid_keys = app.config.auth.api_keys if app.config.auth.enabled else ["sk-fishrouter"]
    if body.password in valid_keys:
        token = secrets.token_hex(32)
        sessions[token] = time.time() + SESSION_EXPIRE
        response = JSONResponse({"status": "ok", "message": "登录成功"})
        response.set_cookie(key="fishrouter_session", value=token, max_age=SESSION_EXPIRE, httponly=True, samesite="lax")
        return response
    raise HTTPException(status_code=401, detail="密码错误")


@router.post("/api/logout")
async def logout(request: Request):
    token = get_session_token(request)
    if token:
        sessions.pop(token, None)
    response = JSONResponse({"status": "ok", "message": "已登出"})
    response.delete_cookie("fishrouter_session")
    return response


@router.get("/assets/{filename:path}")
async def serve_assets(filename: str):
    file_path = get_static_dir() / "dist" / "assets" / filename
    if file_path.exists() and file_path.is_file():
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="Asset not found")


@router.get("/favicon.ico")
async def serve_favicon():
    static_dir = get_static_dir()
    favicon = static_dir / "favicon.ico"
    if favicon.exists():
        return FileResponse(favicon, media_type="image/x-icon")
    raise HTTPException(status_code=404, detail="Favicon not found")


def _serve_react_app() -> FileResponse:
    dist_index = get_dist_index()
    if dist_index.exists():
        return FileResponse(dist_index)
    raise HTTPException(status_code=404, detail="React frontend not found. Run: cd frontend && npm run build")


@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return _serve_react_app()


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return _serve_react_app()


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_alt(request: Request):
    return _serve_react_app()


@router.get("/{full_path:path}", response_class=HTMLResponse)
async def catch_all(request: Request, full_path: str):
    path = request.url.path
    if path.startswith("/api/") or path.startswith("/v1/"):
        raise HTTPException(status_code=404, detail="Not found")
    if path.startswith("/assets/"):
        raise HTTPException(status_code=404, detail="Not found")
    return _serve_react_app()


@router.get("/api/logs")
async def get_logs_api(lines: int = 100):
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


@router.post("/api/shutdown")
async def shutdown_server():
    import os
    if sys.platform == 'win32':
        os.system('taskkill /F /T /PID %d' % os.getpid())
    else:
        os._exit(0)
    return {"status": "stopping", "message": "Server is stopping"}

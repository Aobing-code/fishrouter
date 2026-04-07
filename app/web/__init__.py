"""Web模块"""
from .dashboard import router as dashboard_router, spa_router

__all__ = ["dashboard_router", "spa_router"]

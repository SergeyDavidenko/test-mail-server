"""
API routers package
"""

from .auth import router as auth_router
from .emails import router as emails_router
from .health import router as health_router

__all__ = ["auth_router", "emails_router", "health_router"]

from fastapi import APIRouter
from .user import router as user_router
from .activity_log import router as activity_log_router
from .auth import router as auth_router

api_router = APIRouter(prefix="/api/v1")

__all__ = ["api_router"]
api_router.include_router(user_router)
api_router.include_router(activity_log_router)
api_router.include_router(auth_router)
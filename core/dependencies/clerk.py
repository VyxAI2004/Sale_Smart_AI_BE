from sqlalchemy.orm import Session
from fastapi import Depends

from core.dependencies.db import get_db
from services.sale_smart_ai_app.clerk import ClerkService


def get_clerk_service(db: Session = Depends(get_db)) -> ClerkService:
    """Dependency to get ClerkService instance"""
    return ClerkService(db)
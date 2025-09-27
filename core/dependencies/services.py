from fastapi import Depends
from sqlalchemy.orm import Session

from core.dependencies.db import get_db

def get_user_service(db: Session = Depends(get_db)):
    from services.sale_smart_ai_app.user import UserService
    return UserService(db)

def get_activity_log_service(db: Session = Depends(get_db)):
    from services.sale_smart_ai_app.activity_log import ActivityLogService
    return ActivityLogService(db)

def get_auth_service(db: Session = Depends(get_db)):
    from services.sale_smart_ai_app.auth import AuthService
    return AuthService(db)
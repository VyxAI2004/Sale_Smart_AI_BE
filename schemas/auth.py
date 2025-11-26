from typing import Optional, List, Dict
from datetime import datetime
from pydantic import BaseModel, EmailStr
from uuid import UUID

class TokenPayload(BaseModel):
    """JWT token payload"""
    sub: UUID  # user id
    exp: datetime
    iat: Optional[datetime] = None
    roles: List[str] = []
    global_permissions: List[str] = []
    project_permissions: Dict[str, List[str]] = {}  # Dict[project_id, permissions]

class Token(BaseModel):
    """Token response schema"""
    access_token: str
    refresh_token: str
    expires_in: int
    token_type: str = "Bearer"

class TokenData(BaseModel):
    """Token data extracted from JWT"""
    user_id: UUID
    email: str
    roles: List[str] = []
    global_permissions: List[str] = []
    project_permissions: Dict[str, List[str]] = {}  # Dict[project_id, permissions]
    exp: datetime

class LoginRequest(BaseModel):
    """Login request schema"""
    email: EmailStr
    password: str
    remember_me: Optional[bool] = False

class RefreshTokenRequest(BaseModel):
    """Refresh token request schema"""
    refresh_token: str


from typing import Optional, List, Dict
from datetime import datetime
from pydantic import BaseModel, EmailStr
from uuid import UUID

class TokenPayload(BaseModel):
    """JWT token payload"""
    sub: UUID  # user id
    exp: datetime
    iat: Optional[datetime] = None
    iss: Optional[str] = None
    aud: Optional[str] = None
    jti: Optional[str] = None
    roles: List[str] = []

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
    exp: datetime
    iss: Optional[str] = None
    aud: Optional[str] = None
    jti: Optional[str] = None

class LoginRequest(BaseModel):
    """Login request schema"""
    email: EmailStr
    password: str
    remember_me: Optional[bool] = False

class RefreshTokenRequest(BaseModel):
    """Refresh token request schema"""
    refresh_token: str


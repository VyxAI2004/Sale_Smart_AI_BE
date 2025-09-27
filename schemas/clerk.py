from pydantic import BaseModel
from typing import Optional


class ClerkTokenExchangeRequest(BaseModel):
    """Schema for Clerk token exchange request"""
    clerk_token: str


class ClerkUserInfo(BaseModel):
    """Schema for Clerk user information"""
    id: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    image_url: Optional[str] = None
    username: Optional[str] = None


class ClerkTokenExchangeResponse(BaseModel):
    """Schema for Clerk token exchange response"""
    accessToken: str
    refreshToken: str
    user: dict
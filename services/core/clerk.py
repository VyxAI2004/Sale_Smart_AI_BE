import requests
import jwt
from typing import Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session

from env import env
from models.user import User
from repositories.user import UserRepository
from schemas.clerk import ClerkUserInfo
from schemas.user import UserCreate
from services.core.auth import AuthService
from shared.enums import RoleEnum


class ClerkService:
    """Service for handling Clerk integration"""
    
    def __init__(self, db: Session):
        self.db = db
        self.user_repository = UserRepository(User, db)
        self.auth_service = AuthService(db)
        
    def verify_clerk_token(self, clerk_token: str) -> ClerkUserInfo:
        """Verify Clerk token and extract user info"""
        try:
            # Decode JWT token without verification (for development)
            # In production, you should verify with Clerk's public keys from:
            # https://[your-domain].clerk.accounts.dev/.well-known/jwks.json
            decoded_token = jwt.decode(clerk_token, options={"verify_signature": False})
            
            print(f"Decoded Clerk token: {decoded_token}")  # Debug log
            print(f"Clerk publishable key: {env.CLERK_PUBLISHABLE_KEY}")  # Debug log
            
            # Extract user ID from token
            user_id = decoded_token.get("sub")
            if not user_id:
                raise HTTPException(
                    status_code=401, 
                    detail="Invalid token: missing user ID"
                )
            
            # For now, create user info from JWT token only
            # You can expand this later to call Clerk API for more details
            email = decoded_token.get("email") or f"user_{user_id}@example.com"
            
            return ClerkUserInfo(
                id=user_id,
                email=email,
                first_name=decoded_token.get("given_name") or "User",
                last_name=decoded_token.get("family_name") or "",
                image_url=decoded_token.get("picture"),
                username=decoded_token.get("preferred_username") or email.split("@")[0]
            )
                
        except Exception as e:
            print(f"Clerk token verification error: {str(e)}")  # Debug log
            raise HTTPException(
                status_code=401, 
                detail=f"Failed to verify Clerk token: {str(e)}"
            )
    
    def find_or_create_user(self, clerk_user: ClerkUserInfo) -> User:
        """Find existing user or create new one from Clerk data"""
        
        # Try to find existing user by email
        existing_user = self.user_repository.get_by_email(email=clerk_user.email)
        
        if existing_user:
            # Update user info if needed
            if clerk_user.image_url and clerk_user.image_url != existing_user.avatar_url:
                existing_user.avatar_url = clerk_user.image_url
                self.db.commit()
            return existing_user
        
        # Create new user
        full_name = f"{clerk_user.first_name or ''} {clerk_user.last_name or ''}".strip()
        if not full_name:
            full_name = clerk_user.email.split('@')[0]  # fallback to email prefix
            
        username = clerk_user.username or clerk_user.email.split('@')[0]
        
        # Ensure username is unique
        counter = 1
        original_username = username
        while self.user_repository.get_by_username(username=username):
            username = f"{original_username}_{counter}"
            counter += 1
        
        new_user_data = UserCreate(
            username=username,
            email=clerk_user.email,
            password_hash="",  # No password for Clerk users
            full_name=full_name,
            is_active=True
        )
        
        # Create user with default USER role
        new_user = self.user_repository.create(obj_in=new_user_data)
        
        # Assign default USER role
        # TODO: You might want to create a method to assign roles
        # For now, we'll assume users are created with USER role by default
        
        return new_user
    
    def exchange_clerk_token(self, clerk_token: str) -> dict:
        """Exchange Clerk token for backend tokens"""
        
        # Verify Clerk token and get user info
        clerk_user = self.verify_clerk_token(clerk_token)
        
        # Find or create user in database
        user = self.find_or_create_user(clerk_user)
        
        # Get user roles for token generation
        roles = []
        if user.roles:
            roles = [user_role.role.name for user_role in user.roles if user_role.role]
        
        # If no roles assigned, give default USER role
        if not roles:
            roles = [RoleEnum.USER.value]
        
        # Generate backend tokens
        tokens = self.auth_service._create_tokens(user, roles)
        
        return {
            "accessToken": tokens.access_token,
            "refreshToken": tokens.refresh_token,
            "user": {
                "id": str(user.id),
                "email": user.email,
                "name": user.full_name,
                "username": user.username,
                "avatar_url": user.avatar_url,
                "is_active": user.is_active,
                "roles": roles
            }
        }
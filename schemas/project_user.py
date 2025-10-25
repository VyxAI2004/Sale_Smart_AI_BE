from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel

from shared.enums import ProjectRoleEnum

class ProjectUserBase(BaseModel):
    """Base schema for ProjectUser model"""
    project_id: UUID
    user_id: UUID
    role_id: Optional[UUID] = None
    permissions: Optional[dict] = None
    is_active: Optional[bool] = True

class ProjectUserCreate(ProjectUserBase):
    """Schema for creating project user membership"""
    invited_by: Optional[UUID] = None

class ProjectUserUpdate(BaseModel):
    """Schema for updating project user membership"""
    role_id: Optional[UUID] = None
    permissions: Optional[dict] = None
    is_active: Optional[bool] = None

class ProjectUserResponse(ProjectUserBase):
    """Schema for project user response"""
    id: UUID
    joined_at: Optional[datetime] = None
    invited_by: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ProjectMemberAssignRequest(BaseModel):
    """Schema for assigning multiple users to project"""
    user_ids: List[UUID]
    role_id: Optional[UUID] = None
    permissions: Optional[dict] = None

class ProjectMemberRemoveRequest(BaseModel):
    """Schema for removing users from project"""
    user_ids: List[UUID]
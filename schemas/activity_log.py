from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel


class ActivityLogCreate(BaseModel):
    action: str
    user_id: UUID
    target_id: Optional[UUID] = None
    target_type: Optional[str] = None
    log_metadata: Optional[dict] = None

class ActivityLogUpdate(BaseModel):
    action: Optional[str] = None
    target_id: Optional[UUID] = None
    target_type: Optional[str] = None
    log_metadata: Optional[dict] = None


class ActivityLogResponse(BaseModel):
    id: UUID
    user_id: UUID
    action: str
    target_id: Optional[UUID] = None
    target_type: Optional[str] = None
    log_metadata: Optional[dict] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ListActivityLogsResponse(BaseModel):
    items: List[ActivityLogResponse]
    total: int

    class Config:
        from_attributes = True

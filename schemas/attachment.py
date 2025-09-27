from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel


class AttachmentCreate(BaseModel):
    task_id: UUID
    filename: str
    url: str
    uploaded_by: UUID
    file_type: Optional[str] = None
    size: Optional[int] = None


class AttachmentUpdate(BaseModel):
    filename: Optional[str] = None
    url: Optional[str] = None
    file_type: Optional[str] = None
    size: Optional[int] = None


class AttachmentResponse(BaseModel):
    id: UUID
    task_id: UUID
    filename: str
    url: str
    file_type: Optional[str] = None
    size: Optional[int] = None
    uploaded_by: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ListAttachmentsResponse(BaseModel):
    items: List[AttachmentResponse]
    total: int

    class Config:
        from_attributes = True

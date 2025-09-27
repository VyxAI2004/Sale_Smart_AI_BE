from datetime import datetime
from uuid import UUID
from pydantic import BaseModel

class CommentResponse(BaseModel):
    id: UUID
    content: str
    user_id: UUID
    task_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class CommentCreate(BaseModel):
    user_id: UUID
    task_id: UUID
    content: str

class CommentUpdate(BaseModel):
    content: str

class ListCommentsResponse(BaseModel):
    items: list[CommentResponse]
    total: int

    class Config:
        from_attributes = True
from datetime import datetime
from uuid import UUID
from typing import List, Optional
from pydantic import BaseModel

class ProductChatMessageBase(BaseModel):
    role: str
    content: str
    
class ProductChatMessageCreate(ProductChatMessageBase):
    session_id: UUID

class ProductChatMessageUpdate(ProductChatMessageBase):
    pass

class ProductChatMessageResponse(ProductChatMessageBase):
    id: UUID
    session_id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ProductChatSessionBase(BaseModel):
    title: Optional[str] = None
    
class ProductChatSessionCreate(ProductChatSessionBase):
    user_id: UUID
    product_id: Optional[UUID] = None
    project_id: Optional[UUID] = None
    session_type: str = "product_consult"

class ProductChatSessionUpdate(ProductChatSessionBase):
    pass

class ProductChatSessionResponse(ProductChatSessionBase):
    id: UUID
    user_id: UUID
    product_id: Optional[UUID] = None
    project_id: Optional[UUID] = None
    session_type: str
    created_at: datetime
    updated_at: datetime
    messages: List[ProductChatMessageResponse] = []
    
    class Config:
        from_attributes = True

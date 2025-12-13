from typing import List, Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field

# Base Schema
class ProductMarketAnalysisBase(BaseModel):
    pros: List[str] = []
    cons: List[str] = []
    target_audience: Optional[str] = None
    price_evaluation: Optional[str] = None
    marketing_suggestions: List[str] = []

class ProductMarketAnalysisCreate(ProductMarketAnalysisBase):
    product_id: UUID

class ProductMarketAnalysisUpdate(ProductMarketAnalysisBase):
    pass

# Response Schema for API
class ProductMarketAnalysisResponse(ProductMarketAnalysisBase):
    id: UUID
    product_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Schema cho LLM Output (Structured Output Parsing)
class LLMMarketAnalysisResult(BaseModel):
    pros: List[str] = Field(description="Danh sách 3-5 ưu điểm nổi bật từ reviews và mô tả")
    cons: List[str] = Field(description="Danh sách 3-5 nhược điểm từ reviews")
    target_audience: str = Field(description="Mô tả chi tiết khách hàng mục tiêu (Persona)")
    price_evaluation: str = Field(description="Nhận xét ngắn về mức giá so với giá trị mang lại")
    marketing_suggestions: List[str] = Field(description="3-5 gợi ý marketing bán hàng (USP, Kênh quảng cáo, Content angle)")

# Schemas for Chatbot Consultant
class ChatMessage(BaseModel):
    role: str = Field(description="user hoặc assistant")
    content: str

class ConsultantChatRequest(BaseModel):
    query: str
    history: List[ChatMessage] = [] # Optional, for legacy support
    session_id: Optional[UUID] = None # New field for multi-session support
    project_id: Optional[UUID] = None # New field for project context chat

class ConsultantChatResponse(BaseModel):
    answer: str
    sources: List[str] = []
    session_id: Optional[UUID] = None # Return session ID so FE can continue chat

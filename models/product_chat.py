from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .user import User
    from .product import Product
    from .project import Project

class ProductChatSession(Base):
    """
    Lưu phiên trò chuyện (Session) giữa User và AI.
    Hỗ trợ: Product-specific, Project-specific, hoặc Global.
    """
    __tablename__ = "product_chat_sessions"
    
    user_id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Context (Nullable để support Global Chat)
    product_id: Mapped[Optional[str]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=True)
    project_id: Mapped[Optional[str]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=True)
    
    # Meta
    title: Mapped[str] = mapped_column(String(255), nullable=True, comment="Tiêu đề cuộc hội thoại")
    session_type: Mapped[str] = mapped_column(String(50), server_default='product_consult', nullable=False, comment="'product', 'project', 'global'")
    
    # Relationships
    messages: Mapped[List["ProductChatMessage"]] = relationship(
        "ProductChatMessage", 
        back_populates="session", 
        cascade="all, delete-orphan",
        order_by="ProductChatMessage.created_at"
    )
    user: Mapped["User"] = relationship("User")
    product: Mapped[Optional["Product"]] = relationship("Product")
    project: Mapped[Optional["Project"]] = relationship("Project")

class ProductChatMessage(Base):
    """
    Lưu nội dung tin nhắn trong phiên chat.
    """
    __tablename__ = "product_chat_messages"
    
    session_id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), ForeignKey("product_chat_sessions.id", ondelete="CASCADE"), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False, comment="'user' hoặc 'ai'")
    content: Mapped[str] = mapped_column(Text, nullable=False)
    
    session: Mapped["ProductChatSession"] = relationship("ProductChatSession", back_populates="messages")

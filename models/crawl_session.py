from typing import TYPE_CHECKING, Optional
from sqlalchemy import String, DateTime, Integer, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .project import Project
    from .product_source import ProductSource
    from .ai_model import AIModel
    from .task import Task
    from .product import Product

class CrawlSession(Base):
    """Model cho bảng crawl_sessions - lưu lịch sử crawl"""
    __tablename__ = "crawl_sessions"
    
    # Columns
    project_id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    product_source_id: Mapped[Optional[str]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("product_sources.id", ondelete="CASCADE"), nullable=True)
    assigned_model_id: Mapped[Optional[str]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("ai_models.id", ondelete="SET NULL"), nullable=True)
    status: Mapped[Optional[str]] = mapped_column(String(20), server_default='pending', nullable=True)  # pending, running, completed, failed
    crawl_type: Mapped[str] = mapped_column(String(20), nullable=False)  # initial, scheduled, manual
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    started_at: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True), nullable=True)
    products_collected: Mapped[Optional[int]] = mapped_column(Integer, server_default='0', nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    crawl_stats: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)  # Thời gian, số request, etc.
    
    # Relationships
    project: Mapped["Project"] = relationship(
        "Project", 
        back_populates="crawl_sessions",
        lazy="select"
    )
    product_source: Mapped["ProductSource"] = relationship(
        "ProductSource", 
        back_populates="crawl_sessions",
        lazy="select"
    )
    assigned_model: Mapped["AIModel"] = relationship(
        "AIModel", 
        back_populates="crawl_sessions",
        lazy="select"
    )
    tasks: Mapped[list["Task"]] = relationship(
        "Task", 
        back_populates="crawl_session",
        lazy="select"
    )
    products: Mapped[list["Product"]] = relationship(
        "Product", 
        back_populates="crawl_session",
        lazy="select"
    )

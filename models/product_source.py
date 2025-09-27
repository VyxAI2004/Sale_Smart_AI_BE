from typing import TYPE_CHECKING
from sqlalchemy import String, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .project import Project
    from .ai_model import AIModel
    from .crawl_session import CrawlSession
    from .product import Product

class ProductSource(Base):
    """Model cho bảng product_sources - lưu các link sản phẩm để crawl định kỳ"""
    __tablename__ = "product_sources"
    
    # Columns
    project_id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    platform: Mapped[str] = mapped_column(String(50), nullable=False)  # shopee, lazada, tiki, etc.
    product_name: Mapped[str | None] = mapped_column(String(300), nullable=True)
    is_active: Mapped[bool | None] = mapped_column(Boolean, server_default='true', nullable=True)
    crawl_schedule: Mapped[str | None] = mapped_column(String(50), nullable=True)  # inherit from project or custom
    last_crawled_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    next_crawl_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    crawl_config: Mapped[dict | None] = mapped_column(JSONB, nullable=True)  # Selectors, wait times, etc.
    assigned_model_id: Mapped[str | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("ai_models.id", ondelete="SET NULL"), nullable=True)  # Model specific cho source này
    
    # Relationships
    project: Mapped["Project"] = relationship(
        "Project", 
        back_populates="product_sources",
        lazy="select"
    )
    assigned_model: Mapped["AIModel"] = relationship(
        "AIModel", 
        back_populates="assigned_sources",
        lazy="select"
    )
    crawl_sessions: Mapped[list["CrawlSession"]] = relationship(
        "CrawlSession", 
        back_populates="product_source", 
        cascade="all, delete-orphan",
        lazy="select"
    )
    products: Mapped[list["Product"]] = relationship(
        "Product", 
        back_populates="product_source",
        lazy="select"
    )

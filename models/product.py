from typing import TYPE_CHECKING
from sqlalchemy import String, Text, Boolean, DateTime, Integer, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .project import Project
    from .product_source import ProductSource
    from .crawl_session import CrawlSession
    from .task import Task
    from .ai_model import AIModel

class Product(Base):
    """Model cho bảng products"""
    __tablename__ = "products"
    
    # Columns
    project_id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    product_source_id: Mapped[str | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("product_sources.id", ondelete="SET NULL"), nullable=True)  # Link đến source URL
    crawl_session_id: Mapped[str | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("crawl_sessions.id", ondelete="SET NULL"), nullable=True)  # Phiên crawl tạo ra product này
    company: Mapped[str | None] = mapped_column(String(200), nullable=True)
    name: Mapped[str] = mapped_column(String(300), nullable=False)
    brand: Mapped[str | None] = mapped_column(String(100), nullable=True)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    subcategory: Mapped[str | None] = mapped_column(String(100), nullable=True)
    platform: Mapped[str] = mapped_column(String(50), nullable=False)
    current_price: Mapped[Numeric] = mapped_column(Numeric(precision=15, scale=2), nullable=False)
    original_price: Mapped[Numeric | None] = mapped_column(Numeric(precision=15, scale=2), nullable=True)
    discount_rate: Mapped[Numeric | None] = mapped_column(Numeric(precision=5, scale=2), nullable=True)
    currency: Mapped[str | None] = mapped_column(String(10), server_default='VND', nullable=True)
    specifications: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    features: Mapped[str | None] = mapped_column(Text, nullable=True)
    images: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    average_rating: Mapped[Numeric | None] = mapped_column(Numeric(precision=3, scale=2), nullable=True)
    review_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    sold_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    url: Mapped[str] = mapped_column(String(500), nullable=False)  # BẮT BUỘC: link sản phẩm
    collected_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), server_default='now()', nullable=True)
    is_verified: Mapped[bool | None] = mapped_column(Boolean, server_default='false', nullable=True)
    data_source: Mapped[str | None] = mapped_column(String(100), nullable=True)
    
    # Relationships
    project: Mapped["Project"] = relationship(
        "Project", 
        back_populates="products",
        lazy="select"
    )
    product_source: Mapped["ProductSource"] = relationship(
        "ProductSource", 
        back_populates="products",
        lazy="select"
    )
    crawl_session: Mapped["CrawlSession"] = relationship(
        "CrawlSession", 
        back_populates="products",
        lazy="select"
    )
    price_history: Mapped[list["PriceHistory"]] = relationship(
        "PriceHistory", 
        back_populates="product", 
        cascade="all, delete-orphan",
        lazy="select"
    )
    product_comparisons: Mapped[list["ProductComparison"]] = relationship(
        "ProductComparison", 
        back_populates="competitor_product",
        lazy="select"
    )


class PriceHistory(Base):
    """Model cho bảng price_history"""
    __tablename__ = "price_history"
    
    # Columns
    product_id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    price: Mapped[Numeric] = mapped_column(Numeric(precision=15, scale=2), nullable=False)
    currency: Mapped[str | None] = mapped_column(String(10), server_default='VND', nullable=True)
    discount_rate: Mapped[Numeric | None] = mapped_column(Numeric(precision=5, scale=2), nullable=True)
    stock_status: Mapped[str | None] = mapped_column(String(20), nullable=True)
    recorded_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), server_default='now()', nullable=True)
    
    # Relationships
    product: Mapped["Product"] = relationship(
        "Product", 
        back_populates="price_history",
        lazy="select"
    )

class PriceAnalysis(Base):
    """Model cho bảng price_analysis"""
    __tablename__ = "price_analysis"
    
    # Columns
    project_id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    task_id: Mapped[str | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("tasks.id"), nullable=True)
    model_id: Mapped[str | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("ai_models.id", ondelete="SET NULL"), nullable=True)  # Model LLM used for analysis
    avg_market_price: Mapped[Numeric | None] = mapped_column(Numeric(precision=15, scale=2), nullable=True)
    min_price: Mapped[Numeric | None] = mapped_column(Numeric(precision=15, scale=2), nullable=True)
    max_price: Mapped[Numeric | None] = mapped_column(Numeric(precision=15, scale=2), nullable=True)
    price_std_dev: Mapped[Numeric | None] = mapped_column(Numeric(precision=15, scale=2), nullable=True)
    recommended_price: Mapped[Numeric | None] = mapped_column(Numeric(precision=15, scale=2), nullable=True)
    confidence_score: Mapped[Numeric | None] = mapped_column(Numeric(precision=5, scale=4), nullable=True)
    price_by_brand: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    price_by_features: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    analysis_metadata: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    llm_analysis_result: Mapped[dict | None] = mapped_column(JSONB, nullable=True)  # Raw LLM analysis output
    insights: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Relationships
    project: Mapped["Project"] = relationship(
        "Project", 
        back_populates="price_analyses",
        lazy="select"
    )
    task: Mapped["Task"] = relationship(
        "Task",
        lazy="select"
    )
    model: Mapped["AIModel"] = relationship(
        "AIModel", 
        back_populates="price_analyses",
        lazy="select"
    )

class ProductComparison(Base):
    """Model cho bảng product_comparisons"""
    __tablename__ = "product_comparisons"
    
    # Columns
    project_id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    target_product_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    competitor_product_id: Mapped[str | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("products.id"), nullable=True)
    similarity_score: Mapped[Numeric | None] = mapped_column(Numeric(precision=5, scale=4), nullable=True)
    price_difference: Mapped[Numeric | None] = mapped_column(Numeric(precision=15, scale=2), nullable=True)
    competitive_advantage: Mapped[str | None] = mapped_column(Text, nullable=True)
    disadvantage: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Relationships
    project: Mapped["Project"] = relationship(
        "Project", 
        back_populates="product_comparisons",
        lazy="select"
    )
    competitor_product: Mapped["Product"] = relationship(
        "Product", 
        back_populates="product_comparisons",
        lazy="select"
    )

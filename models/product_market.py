from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .product import Product

class ProductMarketAnalysis(Base):
    """
    Model lưu kết quả phân tích thị trường từ AI (Pros/Cons, Target Audience...).
    1-1 Relationship với Product.
    """
    __tablename__ = "product_market_analyses"

    # Foreign Key
    product_id: Mapped[str] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey("products.id", ondelete="CASCADE"), 
        unique=True, 
        nullable=False,
        index=True
    )
    
    # AI Analysis Results
    pros: Mapped[List[str]] = mapped_column(JSONB, server_default='[]', nullable=False)
    cons: Mapped[List[str]] = mapped_column(JSONB, server_default='[]', nullable=False)
    target_audience: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    price_evaluation: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    marketing_suggestions: Mapped[List[str]] = mapped_column(JSONB, server_default='[]', nullable=False)
    
    # Relationships
    product: Mapped["Product"] = relationship("Product", back_populates="market_analysis")

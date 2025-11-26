from typing import TYPE_CHECKING, Optional
from sqlalchemy import String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB, INET
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .user import User
    from .ai_model import AIModel

class ActivityLog(Base):
    """Model cho bảng activity_logs"""
    __tablename__ = "activity_logs"
    
    # Columns
    user_id: Mapped[Optional[str]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    model_id: Mapped[Optional[str]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("ai_models.id", ondelete="SET NULL"), nullable=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    target_type: Mapped[str] = mapped_column(String(50), nullable=False)
    target_id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    ip_address: Mapped[Optional[str]] = mapped_column(INET, nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    log_metadata: Mapped[Optional[dict]] = mapped_column(JSONB, server_default='{}', nullable=True)
    old_values: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    new_values: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship(
        "User", 
        back_populates="activity_logs",
        lazy="select"
    )
    model: Mapped["AIModel"] = relationship(
        "AIModel", 
        back_populates="activity_logs",
        lazy="select"
    )

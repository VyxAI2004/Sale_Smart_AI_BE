from typing import TYPE_CHECKING, Optional
from sqlalchemy import String, Text, Boolean, DateTime, Date, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .user import User
    from .ai_model import AIModel
    from .role import Role
    from .product_source import ProductSource
    from .crawl_session import CrawlSession
    from .task import Task
    from .activity_log import ActivityLog
    from .product import Product, PriceAnalysis, ProductComparison
    from .attachment import Attachment
    from .comment import Comment


class Project(Base):
    """Model cho bảng projects"""
    __tablename__ = "projects"
    
    # Columns
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    target_product_name: Mapped[str] = mapped_column(String(200), nullable=False)
    target_product_category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    target_budget_range: Mapped[Optional[Numeric]] = mapped_column(Numeric(precision=15, scale=2), nullable=True)
    currency: Mapped[Optional[str]] = mapped_column(String(10), server_default='VND', nullable=True)
    status: Mapped[Optional[str]] = mapped_column(String(20), server_default='draft', nullable=True)
    pipeline_type: Mapped[Optional[str]] = mapped_column(String(50), server_default='standard', nullable=True)
    crawl_schedule: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # daily, weekly, monthly, custom
    next_crawl_at: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_by: Mapped[Optional[str]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    assigned_to: Mapped[Optional[str]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    assigned_model_id: Mapped[Optional[str]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("ai_models.id", ondelete="SET NULL"), nullable=True)
    deadline: Mapped[Optional[Date]] = mapped_column(Date, nullable=True)
    completed_at: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    creator: Mapped[Optional["User"]] = relationship(
        "User", 
        back_populates="created_projects", 
        foreign_keys=[created_by],
        lazy="select"
    )
    assignee: Mapped[Optional["User"]] = relationship(
        "User", 
        back_populates="assigned_projects", 
        foreign_keys=[assigned_to],
        lazy="select"
    )
    assigned_model: Mapped[Optional["AIModel"]] = relationship(
        "AIModel", 
        back_populates="assigned_projects",
        lazy="select"
    )
    members: Mapped[list["ProjectUser"]] = relationship(
        "ProjectUser", 
        back_populates="project", 
        cascade="all, delete-orphan",
        lazy="select"
    )
    product_sources: Mapped[list["ProductSource"]] = relationship(
        "ProductSource", 
        back_populates="project", 
        cascade="all, delete-orphan",
        lazy="select"
    )
    crawl_sessions: Mapped[list["CrawlSession"]] = relationship(
        "CrawlSession", 
        back_populates="project", 
        cascade="all, delete-orphan",
        lazy="select"
    )
    tasks: Mapped[list["Task"]] = relationship(
        "Task", 
        back_populates="project", 
        cascade="all, delete-orphan",
        lazy="select"
    )
    products: Mapped[list["Product"]] = relationship(
        "Product", 
        back_populates="project", 
        cascade="all, delete-orphan",
        lazy="select"
    )
    price_analyses: Mapped[list["PriceAnalysis"]] = relationship(
        "PriceAnalysis", 
        back_populates="project", 
        cascade="all, delete-orphan",
        lazy="select"
    )
    product_comparisons: Mapped[list["ProductComparison"]] = relationship(
        "ProductComparison", 
        back_populates="project", 
        cascade="all, delete-orphan",
        lazy="select"
    )
    attachments: Mapped[list["Attachment"]] = relationship(
        "Attachment", 
        back_populates="project", 
        cascade="all, delete-orphan",
        lazy="select"
    )
    comments: Mapped[list["Comment"]] = relationship(
        "Comment", 
        back_populates="project", 
        cascade="all, delete-orphan",
        lazy="select"
    )


class ProjectUser(Base):
    """Model cho bảng project_users - phân quyền trong project"""
    __tablename__ = "project_users"
    
    # Columns
    project_id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role_id: Mapped[Optional[str]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("roles.id", ondelete="SET NULL"), nullable=True)
    permissions: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    joined_at: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True), server_default='now()', nullable=True)
    invited_by: Mapped[Optional[str]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    is_active: Mapped[Optional[bool]] = mapped_column(Boolean, server_default='true', nullable=True)
    
    # Relationships
    project: Mapped["Project"] = relationship(
        "Project", 
        back_populates="members",
        lazy="select"
    )
    user: Mapped["User"] = relationship(
        "User",
        back_populates="project_memberships",
        foreign_keys=[user_id],  
        lazy="select"
    )
    role: Mapped[Optional["Role"]] = relationship(
        "Role", 
        back_populates="project_users",
        lazy="select"
    )
    inviter: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="invited_project_memberships",
        foreign_keys=[invited_by],
        lazy="select"
    )

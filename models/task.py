from typing import TYPE_CHECKING
from sqlalchemy import String, Text, Boolean, DateTime, Date, Integer, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .project import Project
    from .crawl_session import CrawlSession
    from .user import User
    from .ai_model import AIModel
    from .attachment import Attachment
    from .comment import Comment

class Task(Base):
    """Model cho bảng tasks"""
    __tablename__ = "tasks"
    
    # Columns
    project_id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    crawl_session_id: Mapped[str | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("crawl_sessions.id", ondelete="SET NULL"), nullable=True)  # Link task với crawl session
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    pipeline_stage: Mapped[str] = mapped_column(String(50), nullable=False)
    stage_order: Mapped[int] = mapped_column(Integer, nullable=False)
    task_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    status: Mapped[str | None] = mapped_column(String(20), server_default='pending', nullable=True)
    priority: Mapped[str | None] = mapped_column(String(20), server_default='medium', nullable=True)
    assigned_to: Mapped[str | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    assigned_model_id: Mapped[str | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("ai_models.id", ondelete="SET NULL"), nullable=True)  # Model cho analysis tasks
    due_date: Mapped[Date | None] = mapped_column(Date, nullable=True)
    completed_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    estimated_hours: Mapped[Numeric | None] = mapped_column(Numeric(precision=5, scale=2), nullable=True)
    actual_hours: Mapped[Numeric | None] = mapped_column(Numeric(precision=5, scale=2), nullable=True)
    stage_metadata: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    
    # Relationships
    project: Mapped["Project"] = relationship(
        "Project", 
        back_populates="tasks",
        lazy="select"
    )
    crawl_session: Mapped["CrawlSession"] = relationship(
        "CrawlSession", 
        back_populates="tasks",
        lazy="select"
    )
    assignee: Mapped["User"] = relationship(
        "User", 
        back_populates="assigned_tasks",
        lazy="select"
    )
    assigned_model: Mapped["AIModel"] = relationship(
        "AIModel", 
        back_populates="assigned_tasks",
        lazy="select"
    )
    subtasks: Mapped[list["Subtask"]] = relationship(
        "Subtask", 
        back_populates="task", 
        cascade="all, delete-orphan",
        lazy="select"
    )
    attachments: Mapped[list["Attachment"]] = relationship(
        "Attachment", 
        back_populates="task",
        lazy="select"
    )
    comments: Mapped[list["Comment"]] = relationship(
        "Comment", 
        back_populates="task",
        lazy="select"
    )


class Subtask(Base):
    """Model cho bảng subtasks"""
    __tablename__ = "subtasks"
    
    # Columns
    task_id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_completed: Mapped[bool | None] = mapped_column(Boolean, server_default='false', nullable=True)
    completed_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    due_date: Mapped[Date | None] = mapped_column(Date, nullable=True)
    
    # Relationships
    task: Mapped["Task"] = relationship(
        "Task", 
        back_populates="subtasks",
        lazy="select"
    )

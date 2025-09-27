from typing import TYPE_CHECKING
from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .project import Project
    from .task import Task
    from .user import User

class Comment(Base):
    """Model cho bảng comments"""
    __tablename__ = "comments"
    
    # Columns
    project_id: Mapped[str | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=True)
    task_id: Mapped[str | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("tasks.id"), nullable=True)
    user_id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    parent_comment_id: Mapped[str | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("comments.id"), nullable=True)
    
    # Relationships
    project: Mapped["Project"] = relationship(
        "Project", 
        back_populates="comments",
        lazy="select"
    )
    task: Mapped["Task"] = relationship(
        "Task", 
        back_populates="comments",
        lazy="select"
    )
    user: Mapped["User"] = relationship(
        "User", 
        back_populates="comments",
        lazy="select"
    )
    parent_comment: Mapped["Comment"] = relationship(
        "Comment", 
        remote_side="Comment.id",
        lazy="select"
    )
    replies: Mapped[list["Comment"]] = relationship(
        "Comment", 
        back_populates="parent_comment",
        cascade="all, delete-orphan",
        lazy="select"
    )

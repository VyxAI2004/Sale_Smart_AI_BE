from typing import TYPE_CHECKING
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .project import Project
    from .task import Task
    from .user import User

class Attachment(Base):
    """Model cho bảng attachments"""
    __tablename__ = "attachments"
    
    # Columns
    project_id: Mapped[str | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=True)
    task_id: Mapped[str | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("tasks.id"), nullable=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    file_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    uploaded_by: Mapped[str | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    # Relationships
    project: Mapped["Project"] = relationship(
        "Project", 
        back_populates="attachments",
        lazy="select"
    )
    task: Mapped["Task"] = relationship(
        "Task", 
        back_populates="attachments",
        lazy="select"
    )
    uploader: Mapped["User"] = relationship(
        "User", 
        back_populates="uploaded_attachments",
        lazy="select"
    )

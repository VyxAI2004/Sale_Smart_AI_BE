from typing import TYPE_CHECKING
from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .user import User
    from .project import ProjectUser

class Role(Base):
    """Model cho bảng roles"""
    __tablename__ = "roles"
    
    # Columns
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Relationships
    users: Mapped[list["UserRole"]] = relationship(
        "UserRole", 
        back_populates="role", 
        cascade="all, delete-orphan",
        lazy="select"
    )
    permissions: Mapped[list["RolePermission"]] = relationship(
        "RolePermission", 
        back_populates="role", 
        cascade="all, delete-orphan",
        lazy="select"
    )
    project_users: Mapped[list["ProjectUser"]] = relationship(
        "ProjectUser", 
        back_populates="role",
        lazy="select"
    )

class Permission(Base):
    """Model cho bảng permissions"""
    __tablename__ = "permissions"
    
    # Columns
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Relationships
    roles: Mapped[list["RolePermission"]] = relationship(
        "RolePermission", 
        back_populates="permission", 
        cascade="all, delete-orphan",
        lazy="select"
    )

class UserRole(Base):
    """Junction table cho User-Role many-to-many relationship"""
    __tablename__ = "user_roles"
    
    # Columns
    user_id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role_id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
    
    # Relationships
    user: Mapped["User"] = relationship(
        "User", 
        back_populates="roles",
        lazy="select"
    )
    role: Mapped["Role"] = relationship(
        "Role", 
        back_populates="users",
        lazy="select"
    )


class RolePermission(Base):
    """Junction table cho Role-Permission many-to-many relationship"""
    __tablename__ = "role_permissions"
    
    # Columns
    role_id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
    permission_id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), ForeignKey("permissions.id", ondelete="CASCADE"), nullable=False)
    
    # Relationships
    role: Mapped["Role"] = relationship(
        "Role", 
        back_populates="permissions",
        lazy="select"
    )
    permission: Mapped["Permission"] = relationship(
        "Permission", 
        back_populates="roles",
        lazy="select"
    )

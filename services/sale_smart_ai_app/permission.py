from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, or_

from models.user import User
from models.role import Role, RolePermission, Permission, UserRole
from models.project import ProjectUser, Project
from shared.enums import RoleEnum

class PermissionService:
    def __init__(self, db: Session):
        self.db = db

    def get_user_permissions(self, user_id: UUID, project_id: Optional[UUID] = None) -> List[str]:
        """
        Get all permissions for a user, optionally scoped to a project.
        Returns a list of permission slugs/names.
        """
        permissions = set()

        # 1. Get Global Permissions via User Roles
        # Join: User -> UserRole -> Role -> RolePermission -> Permission
        stmt = (
            select(Permission.name)
            .join(RolePermission, RolePermission.permission_id == Permission.id)
            .join(Role, Role.id == RolePermission.role_id)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(UserRole.user_id == user_id)
            .where(Role.is_active == True)
            .where(Permission.is_active == True)
        )
        global_perms = self.db.execute(stmt).scalars().all()
        permissions.update(global_perms)

        # 2. If project_id is provided, get Project Permissions
        if project_id:
            # Join: ProjectUser -> Role -> RolePermission -> Permission
            stmt = (
                select(Permission.name)
                .join(RolePermission, RolePermission.permission_id == Permission.id)
                .join(Role, Role.id == RolePermission.role_id)
                .join(ProjectUser, ProjectUser.role_id == Role.id)
                .where(ProjectUser.user_id == user_id)
                .where(ProjectUser.project_id == project_id)
                .where(Role.is_active == True)
                .where(Permission.is_active == True)
            )
            project_perms = self.db.execute(stmt).scalars().all()
            permissions.update(project_perms)

        return list(permissions)

    def has_permission(self, user_id: UUID, permission_name: str, project_id: Optional[UUID] = None) -> bool:
        """
        Check if user has a specific permission.
        """
        # 1. Check Global Roles first
        stmt = (
            select(Permission.id)
            .join(RolePermission, RolePermission.permission_id == Permission.id)
            .join(Role, Role.id == RolePermission.role_id)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(UserRole.user_id == user_id)
            .where(Permission.name == permission_name)
            .where(Role.is_active == True)
            .where(Permission.is_active == True)
        )
        if self.db.execute(stmt).first():
            return True

        # 2. Check Project Roles if project_id is provided
        if project_id:
            stmt = (
                select(Permission.id)
                .join(RolePermission, RolePermission.permission_id == Permission.id)
                .join(Role, Role.id == RolePermission.role_id)
                .join(ProjectUser, ProjectUser.role_id == Role.id)
                .where(ProjectUser.user_id == user_id)
                .where(ProjectUser.project_id == project_id)
                .where(Permission.name == permission_name)
                .where(Role.is_active == True)
                .where(Permission.is_active == True)
            )
            if self.db.execute(stmt).first():
                return True
            
            # 3. Check if user is Project Owner (Implicit Permission) or Assignee
            project = self.db.get(Project, project_id)
            if project:
                if project.created_by == user_id:
                    return True
                if project.assigned_to == user_id:
                    return True

        return False

    def enforce_permission(self, user_id: UUID, permission_name: str, project_id: Optional[UUID] = None):
        """
        Raise exception if user does not have permission.
        """
        if not self.has_permission(user_id, permission_name, project_id):
            from fastapi import HTTPException, status
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"You do not have permission: {permission_name}"
            )

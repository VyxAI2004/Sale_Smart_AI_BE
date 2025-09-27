from functools import wraps
from fastapi import HTTPException, Depends, status
from core.dependencies.auth import verify_token
from schemas.auth import TokenData
from shared.enums import RoleEnum, GlobalPermissionEnum, ProjectPermissionEnum

def check_global_permissions(*required_permissions: GlobalPermissionEnum):
    """
    Middleware để kiểm tra global permissions của user.
    Usage:
        @router.get("/users")
        @check_global_permissions(GlobalPermissionEnum.VIEW_USERS)
        async def get_users():
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, token: TokenData = Depends(verify_token), **kwargs):
            if not token:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated"
                )
            
            # Super Admin có tất cả permissions
            if RoleEnum.SUPER_ADMIN.value in token.roles:
                return await func(*args, token=token, **kwargs)
            
            # Admin có tất cả global permissions trừ một số quyền đặc biệt
            if RoleEnum.ADMIN.value in token.roles:
                # Nếu cần giới hạn một số quyền cho Admin
                # restricted_permissions = [GlobalPermissionEnum.MANAGE_SYSTEM_SETTINGS]
                # if not any(perm in restricted_permissions for perm in required_permissions):
                return await func(*args, token=token, **kwargs)
                
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required permissions: {', '.join(p.value for p in required_permissions)}"
            )
        return wrapper
    return decorator

def check_project_permissions(project_id_param: str = "project_id", *required_permissions: ProjectPermissionEnum):
    """
    Middleware để kiểm tra project-specific permissions của user.
    Usage:
        @router.get("/projects/{project_id}/tasks")
        @check_project_permissions("project_id", ProjectPermissionEnum.VIEW_TASKS)
        async def get_project_tasks():
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, token: TokenData = Depends(verify_token), **kwargs):
            if not token:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated"
                )
            
            project_id = kwargs.get(project_id_param)
            if not project_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Missing {project_id_param} parameter"
                )
            
            # Super Admin và Admin có tất cả project permissions
            if any(role in [RoleEnum.SUPER_ADMIN.value, RoleEnum.ADMIN.value] 
                   for role in token.roles):
                return await func(*args, token=token, **kwargs)
            
            # TODO: Kiểm tra project membership và role
            # Có thể query từ database hoặc lưu trong token
            
            # Ví dụ logic kiểm tra role trong project:
            # if project_role == ProjectRoleEnum.PROJECT_OWNER.value:
            #     return await func(*args, token=token, **kwargs)
            # elif project_role == ProjectRoleEnum.PROJECT_ADMIN.value:
            #     restricted = [ProjectPermissionEnum.DELETE_PROJECT]
            #     if not any(perm in restricted for perm in required_permissions):
            #         return await func(*args, token=token, **kwargs)
            
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required permissions: {', '.join(p.value for p in required_permissions)}"
            )
        return wrapper
    return decorator
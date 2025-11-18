"""
Permissions utilities
"""
from typing import Any
from fastapi import HTTPException, status, Depends, Request
from fastapi.routing import APIRoute
# from fastapi.middleware.httpsredirect import
from starlette.middleware.base import BaseHTTPMiddleware

from jose import jwt
from db.models.user import User
from core.exceptions import exceptions
from core.config import settings
from utils.oauth2 import get_current_user
from utils.enums import UserTypeEnum


def has_permission(permission: str, module: str) -> Any:
    def permission_checker(user: User = Depends(get_current_user)) -> Any:
        user_perms: set[tuple[str, str]] = {
            (userperm.name, userperm.module) for userperm in user.roles.permissions}
        # Check if the user has the required permission
        if (permission, module) in user_perms:
            return user

        # Allow "manage" permission to override "read" permission
        if permission == "read" and ("manage", module) in user_perms:
            return user
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=exceptions.INADEQUATE_PERMISSIONS,
        )
    return permission_checker


def is_admin(user: User = Depends(get_current_user)) -> User:
    """Check if the current user is an admin"""
    if user.user_type != UserTypeEnum.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return user


def is_admin_or_self(user_id: int, current_user: User = Depends(get_current_user)) -> User:
    """Check if the current user is admin or accessing their own data"""
    if current_user.user_type != UserTypeEnum.admin and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    return current_user

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

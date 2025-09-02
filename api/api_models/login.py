"""
Login and authentication related Pydantic models.
"""
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from datetime import date
from typing import Optional


class UserResponse(BaseModel):
    id: int
    first_name: str
    last_name: Optional[str]
    email: EmailStr
    gender: str
    nationality: str
    location: Optional[str]
    is_active: bool
    profile_pic: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class AdminResponse(BaseModel):
    admin_id: str
    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    id: int
    access_token: str
    token_type: str
    is_active: bool
    refresh_token: str
    role_id: int
    user_profile: Optional[UserResponse]

    model_config = ConfigDict(from_attributes=True)

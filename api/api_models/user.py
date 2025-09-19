"""
Serializer for the user model
"""
import json
from datetime import datetime
from typing import Optional, Any
from fastapi import HTTPException, status
from pydantic import BaseModel, Field, ConfigDict, field_validator, EmailStr
from core.exceptions import exceptions
from utils.enums import UserTypeEnum


class UserBase(BaseModel):
    first_name: str = Field(...)
    last_name: Optional[str] = Field(None)
    email: EmailStr = Field(...)
    gender: str = Field(...)
    nationality: Optional[str] = Field(...)
    location: Optional[str] = Field(None)
    is_active: bool = Field(default=True)
    profile_pic: Optional[str] = Field(None)
    about: Optional[str] = Field(None)
    user_type: Optional[str] = Field(UserTypeEnum.mentee.value)


class UserSignup(UserBase):
    password: str = Field(..., min_length=5)
    password_confirmation: str = Field(...)

    model_config = ConfigDict(from_attributes=True, validate_assignment=True,
                              arbitrary_types_allowed=True)

    @field_validator("email")
    def validate_email(cls, email) -> Any:
        if '@' not in email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=exceptions.INVALID_EMAIL
            )
        return email


class UserResponse(UserBase):
    id: int = Field(...)

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    first_name: Optional[str] = Field(None)
    last_name: Optional[str] = Field(None)
    nationality: Optional[str] = Field(...)
    location: Optional[str] = Field(None)
    profile_pic: Optional[str] = Field(None)
    about: Optional[str] = Field(None)


class UserLogin(BaseModel):
    email: EmailStr = Field(...)
    password: str = Field(...)

    model_config = ConfigDict(from_attributes=True)


class TokenData(BaseModel):
    id: Optional[str] = Field(default=None)


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(...)


class ForgotPasswordRequest(BaseModel):
    email: EmailStr = Field(...)


class ResetPasswordRequest(BaseModel):
    token: str = Field(...)
    new_password: str = Field(...)


class AllUserResponse(UserBase):
    id: int
    date_created: datetime


class ErrorResponse(BaseModel):
    detail: str

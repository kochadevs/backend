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
from api.api_models.onboarding import (
    NewRoleValueResponse, JobSearchStatusResponse,
    IndustryResponse, RoleofInterestResponse, SkillsResponse, CareerGoalsResponse,
)


class SocialLinks(BaseModel):
    linkedin: Optional[str] = None
    twitter: Optional[str] = None
    website: Optional[str] = None
    portfolio: Optional[str] = None


class Availability(BaseModel):
    days: Optional[list[str]] = None  # ["Monday", "Tuesday", etc.]
    times: Optional[list[str]] = None  # ["9:00-12:00", "14:00-17:00", etc.]


class UserBase(BaseModel):
    first_name: str = Field(...)
    last_name: Optional[str] = Field(None)
    email: EmailStr = Field(...)
    gender: Optional[str] = Field(None)  # Made optional for step-based signup
    nationality: Optional[str] = Field(None)  # Country
    location: Optional[str] = Field(None)  # City/State
    phone: Optional[str] = Field(None)  # Phone number
    is_active: bool = Field(default=False)
    email_verified: bool = Field(default=False)
    profile_pic: Optional[str] = Field(None)
    cover_photo: Optional[str] = Field(None)
    about: Optional[str] = Field(None)  # Bio
    user_type: Optional[str] = Field(UserTypeEnum.regular.value)  # Default to regular
    social_links: Optional[SocialLinks] = Field(None)
    availability: Optional[Availability] = Field(None)


class UserSignup(UserBase):
    """Full signup model - for backwards compatibility"""
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


class UserSignupStep1(BaseModel):
    """Step 1: Create Account - Basic info"""
    first_name: str = Field(..., min_length=1)
    last_name: Optional[str] = Field(None)
    email: EmailStr = Field(...)
    password: str = Field(..., min_length=5)
    password_confirmation: str = Field(...)

    model_config = ConfigDict(from_attributes=True, validate_assignment=True)

    @field_validator("email")
    def validate_email(cls, email) -> Any:
        if '@' not in email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=exceptions.INVALID_EMAIL
            )
        return email.lower()


class UserSignupStep2(BaseModel):
    """Step 2: Profile Details"""
    gender: str = Field(...)
    phone: Optional[str] = Field(None)
    nationality: str = Field(...)  # Country
    location: Optional[str] = Field(None)  # City/State

    model_config = ConfigDict(from_attributes=True)


class VerifyEmailRequest(BaseModel):
    """Verify email with magic link token"""
    token: str = Field(...)


class ResendVerificationRequest(BaseModel):
    """Resend verification email"""
    email: EmailStr = Field(...)


class UserTypeUpdateRequest(BaseModel):
    """Update user type from regular to mentor/mentee"""
    user_type: str = Field(...)

    @field_validator("user_type")
    def validate_user_type(cls, user_type) -> Any:
        if user_type not in ["mentor", "mentee"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User type must be either 'mentor' or 'mentee'"
            )
        return user_type


class UserResponse(UserBase):
    id: int = Field(...)
    new_role_values: Optional[list[NewRoleValueResponse]] = None
    new_role_values: Optional[list[NewRoleValueResponse]] = None
    job_search_status: Optional[list[JobSearchStatusResponse]] = None
    role_of_interest: Optional[list[RoleofInterestResponse]] = None
    industry: Optional[list[IndustryResponse]] = None
    skills: Optional[list[SkillsResponse]] = None
    career_goals: Optional[list[CareerGoalsResponse]] = None

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    first_name: Optional[str] = Field(None)
    last_name: Optional[str] = Field(None)
    gender: Optional[str] = Field(None)
    nationality: Optional[str] = Field(None)  # Country
    location: Optional[str] = Field(None)  # City/State
    phone: Optional[str] = Field(None)
    profile_pic: Optional[str] = Field(None)
    cover_photo: Optional[str] = Field(None)
    about: Optional[str] = Field(None)  # Bio
    current_role: Optional[str] = Field(None)
    social_links: Optional[SocialLinks] = Field(None)
    availability: Optional[Availability] = Field(None)


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

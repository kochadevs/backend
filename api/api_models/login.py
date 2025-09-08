"""
Login and authentication related Pydantic models.
"""
from pydantic import BaseModel, ConfigDict, EmailStr, Field
# from datetime import date
from typing import Optional
from api.api_models.onboarding import NewRoleValueResponse


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
    new_role_values: Optional[list[NewRoleValueResponse]] = None

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
    user_profile: Optional[UserResponse]

    model_config = ConfigDict(from_attributes=True)


class UserNewRoleValue(BaseModel):
    new_role_values: list[int]

    model_config = ConfigDict(from_attributes=True)


class JobSearchStatusModel(BaseModel):
    job_search_status: list[int]

    model_config = ConfigDict(from_attributes=True)


class RoleOfInterestModel(BaseModel):
    roles_of_interest: list[int]

    model_config = ConfigDict(from_attributes=True)


class IndustryModel(BaseModel):
    industries: list[int]

    model_config = ConfigDict(from_attributes=True)


class SkillsModel(BaseModel):
    skills: list[int]

    model_config = ConfigDict(from_attributes=True)


class CareerGoalsModel(BaseModel):
    career_goals: list[int]

    model_config = ConfigDict(from_attributes=True)

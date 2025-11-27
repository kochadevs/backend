"""
Login and authentication related Pydantic models.
"""
from pydantic import BaseModel, ConfigDict, EmailStr, Field
# from datetime import date
from typing import Optional
from api.api_models.onboarding import (
    NewRoleValueResponse, JobSearchStatusResponse,
    IndustryResponse, RoleofInterestResponse, SkillsResponse, CareerGoalsResponse,
    MentoringFrequencyResponse, MentoringFormatResponse,
)
from utils.enums import UserTypeEnum


class SocialLinksResponse(BaseModel):
    linkedin: Optional[str] = None
    twitter: Optional[str] = None
    website: Optional[str] = None
    portfolio: Optional[str] = None


class AvailabilityResponse(BaseModel):
    days: Optional[list[str]] = None
    times: Optional[list[str]] = None


class ProfessionalBackgroundData(BaseModel):
    """Professional background nested object"""
    current_role: Optional[str] = None
    company: Optional[str] = None
    years_of_experience: Optional[int] = None
    industry: Optional[list[IndustryResponse]] = []
    skills: Optional[list[SkillsResponse]] = []

    model_config = ConfigDict(from_attributes=True)


class GoalsData(BaseModel):
    """Goals nested object"""
    career_goals: Optional[list[CareerGoalsResponse]] = []
    long_term_goals: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class MentoringPreferencesData(BaseModel):
    """Mentoring preferences nested object"""
    mentoring_frequency: Optional[list[MentoringFrequencyResponse]] = []
    mentoring_format: Optional[list[MentoringFormatResponse]] = []
    preferred_skills: Optional[list[SkillsResponse]] = []
    preferred_industries: Optional[list[IndustryResponse]] = []

    model_config = ConfigDict(from_attributes=True)


class UserResponse(BaseModel):
    id: int
    first_name: str
    last_name: Optional[str] = None
    email: EmailStr
    gender: Optional[str] = None
    nationality: Optional[str] = None  # Country
    location: Optional[str] = None  # City/State
    phone: Optional[str] = None
    is_active: bool
    email_verified: Optional[bool] = False
    profile_pic: Optional[str] = None
    cover_photo: Optional[str] = None
    about: Optional[str] = None  # Bio
    user_type: UserTypeEnum
    social_links: Optional[dict] = None
    availability: Optional[dict] = None

    # Nested onboarding data
    professional_background: Optional[ProfessionalBackgroundData] = None
    goals: Optional[GoalsData] = None
    mentoring_preferences: Optional[MentoringPreferencesData] = None

    # Onboarding status
    code_of_conduct_accepted: bool = False
    onboarding_completed: bool = False
    is_onboarded: bool = False

    # Legacy fields (kept for backward compatibility, can be removed later)
    new_role_values: Optional[list[NewRoleValueResponse]] = None
    job_search_status: Optional[list[JobSearchStatusResponse]] = None
    role_of_interest: Optional[list[RoleofInterestResponse]] = None

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

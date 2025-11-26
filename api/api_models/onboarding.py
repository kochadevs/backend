"""
Pydantic models for the onboarding models
"""
from typing import Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from db.models.onboarding import (
    NewRoleValue, JobSearchStatus, RoleofInterest, Industry, Skills,
    CareerGoals, MentoringFrequency, MentoringFormat
)


class OnboardingBase(BaseModel):
    id: int
    date_created: datetime
    last_modified: datetime
    name: str


class NewRoleValueResponse(OnboardingBase):
    pass

    model_config = ConfigDict(from_attributes=True)


class JobSearchStatusResponse(OnboardingBase):
    pass

    model_config = ConfigDict(from_attributes=True)


class IndustryResponse(OnboardingBase):
    pass

    model_config = ConfigDict(from_attributes=True)


class SkillsResponse(OnboardingBase):
    pass

    model_config = ConfigDict(from_attributes=True)


class CareerGoalsResponse(OnboardingBase):
    pass

    model_config = ConfigDict(from_attributes=True)


class RoleofInterestResponse(OnboardingBase):
    category: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class MentoringFrequencyResponse(OnboardingBase):
    pass

    model_config = ConfigDict(from_attributes=True)


class MentoringFormatResponse(OnboardingBase):
    pass

    model_config = ConfigDict(from_attributes=True)


# Onboarding Submission Models
class ProfessionalBackgroundRequest(BaseModel):
    """Professional Background section of onboarding"""
    current_role: Optional[str] = None
    company: Optional[str] = None
    years_of_experience: Optional[int] = None
    industry_ids: Optional[list[int]] = []  # Multi-select
    skill_ids: Optional[list[int]] = []  # Tag selector

    model_config = ConfigDict(from_attributes=True)


class GoalsRequest(BaseModel):
    """Goals section of onboarding (for mentees)"""
    career_goal_ids: Optional[list[int]] = []  # Short-term goals (card selection)
    long_term_goals: Optional[str] = None  # Free text

    model_config = ConfigDict(from_attributes=True)


class MentoringPreferencesRequest(BaseModel):
    """Mentoring Preferences section (for mentors and mentees)"""
    mentoring_frequency_ids: Optional[list[int]] = []
    mentoring_format_ids: Optional[list[int]] = []
    preferred_skill_ids: Optional[list[int]] = []  # Skills they want to mentor/learn
    preferred_industry_ids: Optional[list[int]] = []  # Industries of interest

    model_config = ConfigDict(from_attributes=True)


class CompleteOnboardingRequest(BaseModel):
    """
    Complete onboarding submission - sent when user agrees to code of conduct.
    Fields required depend on user_type:
    - Regular users: professional_background only
    - Mentors: professional_background + mentoring_preferences
    - Mentees: professional_background + goals + mentoring_preferences
    """
    professional_background: ProfessionalBackgroundRequest
    goals: Optional[GoalsRequest] = None  # Required for mentees
    mentoring_preferences: Optional[MentoringPreferencesRequest] = None  # Required for mentors and mentees
    code_of_conduct_accepted: bool  # Must be True

    model_config = ConfigDict(from_attributes=True)


# Onboarding Response Models (for fetching user's onboarding data)
class ProfessionalBackgroundResponse(BaseModel):
    """Professional Background section response"""
    current_role: Optional[str] = None
    company: Optional[str] = None
    years_of_experience: Optional[int] = None
    industries: Optional[list[IndustryResponse]] = []
    skills: Optional[list[SkillsResponse]] = []

    model_config = ConfigDict(from_attributes=True)


class GoalsResponse(BaseModel):
    """Goals section response (for mentees)"""
    career_goals: Optional[list[CareerGoalsResponse]] = []  # Short-term goals
    long_term_goals: Optional[str] = None  # Free text

    model_config = ConfigDict(from_attributes=True)


class MentoringPreferencesResponse(BaseModel):
    """Mentoring Preferences section response (for mentors and mentees)"""
    mentoring_frequency: Optional[list[MentoringFrequencyResponse]] = []
    mentoring_format: Optional[list[MentoringFormatResponse]] = []

    model_config = ConfigDict(from_attributes=True)


class UserOnboardingDataResponse(BaseModel):
    """
    Complete onboarding data for a user - structured by section.
    Sections returned depend on user_type and what they've completed.
    """
    is_onboarded: bool
    user_type: str
    professional_background: Optional[ProfessionalBackgroundResponse] = None
    goals: Optional[GoalsResponse] = None
    mentoring_preferences: Optional[MentoringPreferencesResponse] = None

    model_config = ConfigDict(from_attributes=True)

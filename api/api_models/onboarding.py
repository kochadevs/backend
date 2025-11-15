"""
Pydantic models for the onboarding models
"""
from typing import Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from db.models.onboarding import (
    NewRoleValue, JobSearchStatus, RoleofInterest, Industry, Skills,
    CareerGoals
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

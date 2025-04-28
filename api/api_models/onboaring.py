"""
Pydantic models for the onboarding models
"""
from typing import Optional
from pydantic import BaseModel
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


class RoleofInterestResponse(OnboardingBase):
    category: Optional[str] = None

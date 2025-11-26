"""
Pydantic models for Annual Targets
"""
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime, date
from utils.enums import AnnualTargetStatusEnum


class AnnualTargetBase(BaseModel):
    objective: str = Field(..., description="The target objective/goal")
    measured_by: Optional[str] = Field(None, description="How progress is measured")
    completed_by: Optional[date] = Field(None, description="Target completion date")
    upload_path: Optional[str] = Field(None, description="Path to uploaded document")
    status: AnnualTargetStatusEnum = Field(default=AnnualTargetStatusEnum.not_started)

    model_config = ConfigDict(from_attributes=True)


class AnnualTargetCreate(BaseModel):
    objective: str = Field(..., min_length=1, description="The target objective/goal")
    measured_by: Optional[str] = Field(None, description="How progress is measured")
    completed_by: Optional[date] = Field(None, description="Target completion date")
    upload_path: Optional[str] = Field(None, description="Path to uploaded document")

    model_config = ConfigDict(from_attributes=True)


class AnnualTargetUpdate(BaseModel):
    objective: Optional[str] = Field(None, min_length=1)
    measured_by: Optional[str] = Field(None)
    completed_by: Optional[date] = Field(None)
    upload_path: Optional[str] = Field(None)
    status: Optional[AnnualTargetStatusEnum] = Field(None)

    model_config = ConfigDict(from_attributes=True)


class AnnualTargetResponse(AnnualTargetBase):
    id: int
    user_id: int
    date_created: datetime
    last_modified: datetime

    model_config = ConfigDict(from_attributes=True)


class ProfileCompletionResponse(BaseModel):
    """Response model for profile completion calculation"""
    user_type: str
    profile_completion_percentage: float
    annual_target_completion_percentage: float
    overall_completion_percentage: float
    profile_details: dict
    annual_targets_summary: dict

    model_config = ConfigDict(from_attributes=True)

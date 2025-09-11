"""
API models for the community groups
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class GroupCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    description: Optional[str] = None
    is_public: Optional[bool] = True


class GroupOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    created_by: Optional[int]
    is_public: bool
    created_at: datetime

    class Config:
        from_attributes = True

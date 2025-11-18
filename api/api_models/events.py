"""
Serializer for the event model
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class EventBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None)
    start_date: datetime = Field(...)
    end_date: datetime = Field(...)
    start_time: str = Field(..., pattern=r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$')  # HH:MM format
    end_time: str = Field(..., pattern=r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$')  # HH:MM format
    location: Optional[str] = Field(None)
    image_url: Optional[str] = Field(None)


class EventCreate(EventBase):
    """Schema for creating a new event"""
    model_config = ConfigDict(from_attributes=True)


class EventUpdate(BaseModel):
    """Schema for updating an event"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None)
    start_date: Optional[datetime] = Field(None)
    end_date: Optional[datetime] = Field(None)
    start_time: Optional[str] = Field(None, pattern=r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$')
    end_time: Optional[str] = Field(None, pattern=r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$')
    location: Optional[str] = Field(None)
    image_url: Optional[str] = Field(None)
    is_active: Optional[bool] = Field(None)

    model_config = ConfigDict(from_attributes=True)


class EventResponse(EventBase):
    """Schema for event response"""
    id: int = Field(...)
    date_created: datetime = Field(...)
    last_modified: datetime = Field(...)
    is_active: bool = Field(...)
    created_by: int = Field(...)

    model_config = ConfigDict(from_attributes=True)

"""
API Models for the mentors module
"""
from datetime import datetime
from pydantic import BaseModel
from typing import Optional
from api.api_models.user import UserResponse


class MentorPackageBase(BaseModel):
    name: str
    description: str
    price: float
    duration: int


class MentorPackageCreate(MentorPackageBase):
    pass


class MentorPackageResponse(MentorPackageBase):
    id: int
    date_created: datetime
    last_modified: datetime
    is_active: bool
    user_id: int

    class Config:
        from_attributes = True


class MentorBookingBase(BaseModel):
    mentor_id: int
    mentor_package_id: int
    booking_date: datetime
    notes: str | None = None


class MentorBookingCreate(MentorBookingBase):
    pass


class MentorBookingResponse(MentorBookingBase):
    id: int
    date_created: datetime
    last_modified: datetime
    status: str

    class Config:
        from_attributes = True


class MentorBookingDetailedResponse(BaseModel):
    """
    Enhanced booking response with mentor, mentee, and package details
    """
    id: int
    booking_date: datetime
    status: str
    notes: Optional[str] = None
    date_created: datetime
    last_modified: datetime
    mentor: UserResponse
    mentee: UserResponse
    mentor_package: MentorPackageResponse
    is_busy: bool = True

    class Config:
        from_attributes = True


class BookingSlot(BaseModel):
    """
    Represents a time slot with booking status
    """
    date: datetime
    is_busy: bool
    booking: Optional[MentorBookingDetailedResponse] = None


class MentorScheduleResponse(BaseModel):
    """
    Response containing mentor's schedule with busy slots
    """
    mentor_id: int
    bookings: list[MentorBookingDetailedResponse]
    total_bookings: int

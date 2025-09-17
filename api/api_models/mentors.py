"""
API Models for the mentors module
"""
from datetime import datetime
from pydantic import BaseModel


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

"""
Keep track of all enums
"""
from enum import Enum


class GenderEnum(str, Enum):
    Male = "Male"
    Female = "Female"


class UserTypeEnum(str, Enum):
    mentor = "mentor"
    mentee = "mentee"


class MentorBookingStatusEnum(str, Enum):
    pending = "pending"
    accepted: str = "accepted"
    confirmed = "confirmed"
    rejected = "rejected"
    cancelled = "cancelled"
    completed = "completed"

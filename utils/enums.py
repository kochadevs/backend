"""
Keep track of all enums
"""
from enum import Enum


class GenderEnum(str, Enum):
    Male = "Male"
    Female = "Female"


class UserTypeEnum(str, Enum):
    regular = "regular"  # Default type, can later become mentor or mentee
    mentor = "mentor"
    mentee = "mentee"
    admin = "admin"


class MentorBookingStatusEnum(str, Enum):
    pending = "pending"
    accepted: str = "accepted"
    confirmed = "confirmed"
    rejected = "rejected"
    cancelled = "cancelled"
    completed = "completed"


class RoomTypeEnum(str, Enum):
    direct: str = "direct"
    group: str = "group"


class AnnualTargetStatusEnum(str, Enum):
    not_started = "not_started"
    in_progress = "in_progress"
    completed = "completed"
    overdue = "overdue"

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

"""
User model
"""
from sqlalchemy import (
    Boolean,
    Column,
    Enum,
    String,
    Integer,
    TIMESTAMP,
    Text,
    text,
    func,
    JSON
)
from db.database import Base
from utils.enums import UserTypeEnum
from sqlalchemy.orm import relationship
from db.models.user_association import (
    user_new_role_assosciation, user_job_search_status_assosciation,
    user_role_of_interest_assosciation, user_industry_assosciation,
    user_skills_assosciation, user_career_goals_assosciation
)


class User(Base):
    __tablename__: str = "users"
    id = Column(Integer, primary_key=True, index=True)
    date_created = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    last_modified = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
        onupdate=func.now(),
    )

    # Common fields moved from profiles
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=True)
    email = Column(String, nullable=False, unique=True)
    gender = Column(String, nullable=True)  # Made nullable for step-based signup
    nationality = Column(String, nullable=True)  # Renamed conceptually to "country"
    location = Column(String, nullable=True)  # City/State
    phone = Column(String, nullable=True)  # New field for phone number
    profile_pic = Column(String, nullable=True)
    cover_photo = Column(String, nullable=True)  # New field for cover photo
    is_active = Column(Boolean, nullable=False, default=False)
    email_verified = Column(Boolean, nullable=False, default=False)  # New field for email verification
    current_role = Column(String, nullable=True)
    about = Column(Text, nullable=True)  # Bio section
    user_type = Column(
        Enum(UserTypeEnum, values_callable=lambda obj: [e.value for e in obj]),
        nullable=False, default=UserTypeEnum.regular  # Changed default to regular
    )

    # Social links stored as JSON
    social_links = Column(JSON, nullable=True)  # {"linkedin": "", "twitter": "", "website": "", "portfolio": ""}

    # Availability stored as JSON
    availability = Column(JSON, nullable=True)  # {"days": ["Monday", "Tuesday"], "times": ["9:00-12:00"]}

    # Auth fields
    password = Column(String, nullable=False)

    # Onabording responses
    new_role_values = relationship(
        "NewRoleValue", secondary=user_new_role_assosciation, backref="users"
    )
    job_search_status = relationship(
        "JobSearchStatus", secondary=user_job_search_status_assosciation,
        backref="users"
    )
    role_of_interest = relationship(
        "RoleofInterest", secondary=user_role_of_interest_assosciation,
        backref="users"
    )
    industry = relationship(
        "Industry", secondary=user_industry_assosciation, backref="users"
    )
    skills = relationship(
        "Skills", secondary=user_skills_assosciation, backref="users"
    )
    career_goals = relationship(
        "CareerGoals", secondary=user_career_goals_assosciation, backref="users"
    )
    groups = relationship(
        "Group",
        secondary="group_membership",
        back_populates="members"
    )

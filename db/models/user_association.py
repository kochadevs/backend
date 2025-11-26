from db.database import Base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, TIMESTAMP, ForeignKey, Table


user_new_role_assosciation = Table(
    "user_new_role_assosciation",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("new_role_value_id", Integer, ForeignKey("new_role_value.id", ondelete="CASCADE"), primary_key=True),
)


user_job_search_status_assosciation = Table(
    "user_job_search_status_assosciation",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("job_search_status_id", Integer, ForeignKey("job_search_status.id", ondelete="CASCADE"), primary_key=True)
)


user_role_of_interest_assosciation = Table(
    "user_role_of_interest_assosciation",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("role_of_interest_id", Integer, ForeignKey("role_of_interest.id", ondelete="CASCADE"), primary_key=True)
)


user_industry_assosciation = Table(
    "user_industry_assosciation",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("industry_id", Integer, ForeignKey("industries.id", ondelete="CASCADE"), primary_key=True)
)


user_skills_assosciation = Table(
    "user_skills_assosciation",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("skills_id", Integer, ForeignKey("skills.id", ondelete="CASCADE"), primary_key=True)
)


user_career_goals_assosciation = Table(
    "user_career_goals_assosciation",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("career_goals_id", Integer, ForeignKey("career_goals.id", ondelete="CASCADE"), primary_key=True)
)


user_mentoring_frequency_assosciation = Table(
    "user_mentoring_frequency_assosciation",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("mentoring_frequency_id", Integer, ForeignKey("mentoring_frequency.id", ondelete="CASCADE"), primary_key=True)
)


user_mentoring_format_assosciation = Table(
    "user_mentoring_format_assosciation",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("mentoring_format_id", Integer, ForeignKey("mentoring_format.id", ondelete="CASCADE"), primary_key=True)
)

"""
Onboarding
"""
from typing import Any
from db.database import Base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, TIMESTAMP, text, String, func


class NewRoleValue(Base):
    __tablename__ = "new_role_value"
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
    name = Column(String, nullable=False, unique=True)

    def __str__(self) -> int:
        return self.name


class JobSearchStatus(Base):
    __tablename__ = "job_search_status"
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
    name = Column(String, nullable=False, unique=True)


class RoleofInterest(Base):
    __tablename__ = "role_of_interest"
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
    name = Column(String, nullable=False, unique=True)
    category = Column(String, nullable=True)


class Industry(Base):
    __tablename__ = "industries"
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
    name = Column(String, nullable=False, unique=True)


class Skills(Base):
    __tablename__ = "skills"
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
    name = Column(String, nullable=False, unique=True)


class CareerGoals(Base):
    __tablename__ = "career_goals"
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
    name = Column(String, nullable=False, unique=True)


class MentoringFrequency(Base):
    __tablename__ = "mentoring_frequency"
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
    name = Column(String, nullable=False, unique=True)  # "weekly", "bi-weekly", "monthly"


class MentoringFormat(Base):
    __tablename__ = "mentoring_format"
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
    name = Column(String, nullable=False, unique=True)  # "video", "phone", "chat", "in-person"

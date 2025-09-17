"""
Models relating to the mentor matching
"""
from sqlalchemy import (
    Column, Enum, ForeignKey, Integer, TIMESTAMP, text, String, func, Boolean,
)
from sqlalchemy.orm import relationship

from db.database import Base
from utils.enums import MentorBookingStatusEnum


class MentorPackage(Base):
    __tablename__ = "mentor_packages"
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
    description = Column(String, nullable=True)
    price = Column(Integer, nullable=False)
    duration = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    users = relationship(
        "User", foreign_keys=[user_id], backref="mentor_packages"
    )


class MentorBooking(Base):
    __tablename__ = "mentor_bookings"
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
    mentor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    mentee_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    mentor_package_id = Column(Integer, ForeignKey("mentor_packages.id"), nullable=False)
    booking_date = Column(TIMESTAMP(timezone=True), nullable=False)
    status = Column(
        Enum(
            MentorBookingStatusEnum, values_callable=lambda obj: [e.value for e in obj]
        ), nullable=False, default=MentorBookingStatusEnum.pending)
    notes = Column(String, nullable=True)

    mentor = relationship(
        "User", foreign_keys=[mentor_id], backref="mentor_bookings_as_mentor"
    )
    mentee = relationship(
        "User", foreign_keys=[mentee_id], backref="mentor_bookings_as_mentee"
    )
    mentor_package = relationship("MentorPackage", backref="mentor_bookings")

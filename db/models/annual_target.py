"""
Annual Target model for user goal tracking
"""
from sqlalchemy import (
    Column, Enum, ForeignKey, Integer, TIMESTAMP, text, String, func, Text, Date
)
from sqlalchemy.orm import relationship

from db.database import Base
from utils.enums import AnnualTargetStatusEnum


class AnnualTarget(Base):
    __tablename__ = "annual_targets"
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
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    objective = Column(Text, nullable=False)
    measured_by = Column(String, nullable=True)  # How to measure progress
    completed_by = Column(Date, nullable=True)  # Target completion date
    upload_path = Column(String, nullable=True)  # Path to uploaded document/proof
    status = Column(
        Enum(AnnualTargetStatusEnum, values_callable=lambda obj: [e.value for e in obj]),
        nullable=False, default=AnnualTargetStatusEnum.not_started
    )

    # Relationship
    user = relationship("User", backref="annual_targets")

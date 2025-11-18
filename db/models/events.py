"""
Events model
"""
from sqlalchemy import (
    Column,
    String,
    Integer,
    TIMESTAMP,
    Text,
    text,
    func,
    Boolean
)
from db.database import Base


class Event(Base):
    __tablename__: str = "events"

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

    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    start_date = Column(TIMESTAMP(timezone=True), nullable=False)
    end_date = Column(TIMESTAMP(timezone=True), nullable=False)
    start_time = Column(String, nullable=False)  # Format: "HH:MM"
    end_time = Column(String, nullable=False)  # Format: "HH:MM"
    location = Column(String, nullable=True)
    image_url = Column(String, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_by = Column(Integer, nullable=False)  # Admin user ID

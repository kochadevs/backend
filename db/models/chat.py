"""
Models for chat-related database tables.
"""
from datetime import datetime, timezone
from sqlalchemy.sql import expression
from sqlalchemy import (
    Boolean, Column, Index, Integer, String, ForeignKey, DateTime, Text,
    Enum, func
)
from sqlalchemy.orm import relationship, mapped_column, Mapped

from utils.enums import RoomTypeEnum
from db.database import Base


class ChatRoom(Base):
    __tablename__ = "chat_rooms"

    id = Column(Integer, primary_key=True, index=True)
    date_created: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        index=True
    )
    last_modified: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )
    name = Column(String, unique=True, index=True)
    chat_type = Column(Enum(RoomTypeEnum), default=RoomTypeEnum.direct)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    is_public = Column(Boolean, nullable=False, server_default=expression.false())

    members = relationship(
        "ChatRoomMember", back_populates="chat_room", cascade="all, delete-orphan"
    )
    messages = relationship(
        "Message", back_populates="chat_room"
    )

    __table_args__ = (
        Index("ix_chat_rooms_date_created", "date_created"),
    )


class ChatRoomMember(Base):
    __tablename__ = "chat_room_members"

    id = Column(Integer, primary_key=True, index=True)
    date_created: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        index=True
    )
    last_modified: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    chat_room_id = Column(Integer, ForeignKey("chat_rooms.id", ondelete="CASCADE"), nullable=False)
    is_admin = Column(Boolean, nullable=False, server_default=expression.false())
    joined_at = Column(DateTime(timezone=True), server_default=func.now())

    chat_room = relationship(
        "ChatRoom", back_populates="members"
    )


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    date_created: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        index=True
    )
    last_modified: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )
    chat_room_id = Column(Integer, ForeignKey("chat_rooms.id", ondelete="CASCADE"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    content = Column(Text, nullable=False)
    edited = Column(Boolean, nullable=False, server_default=expression.false())
    deleted = Column(Boolean, nullable=False, server_default=expression.false())

    chat_room = relationship(
        "ChatRoom", back_populates="messages"
    )


class MessageDelivery(Base):
    __tablename__ = "message_deliveries"

    id = Column(Integer, primary_key=True, index=True)
    date_created: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        index=True
    )
    last_modified: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )
    message_id = Column(Integer, ForeignKey("messages.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    read_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index("ux_message_user", "message_id", "user_id", unique=True),
    )

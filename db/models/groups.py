"""
Model for the groups table used for posts
"""
from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy import DateTime, ForeignKey, Text, String

from db.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Group(Base):
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(primary_key=True)
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
    name: Mapped[str] = mapped_column(String(150), nullable=False, unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_by: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    # Optional: visibility flags (public/private)
    is_public: Mapped[bool] = mapped_column(default=True, nullable=False)

    # relationship: posts in this group
    posts: Mapped[List["Post"]] = relationship(
        back_populates="group", cascade="all, delete-orphan"
    )
    members: Mapped[List["User"]] = relationship(
        "User",
        secondary="group_membership",
        back_populates="groups"
    )


class GroupMembership(Base):
    __tablename__ = "group_membership"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    group_id: Mapped[int] = mapped_column(
        ForeignKey("groups.id", ondelete="CASCADE"), primary_key=True
    )
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    # role: Mapped[str] = mapped_column(String(50), default="member", nullable=False)  # e.g., member, admin

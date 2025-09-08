"""
Model for the posts table
"""
from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy import DateTime, ForeignKey, Index, Text, literal
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.database import Base


class Post(Base):
    __tablename__ = "posts"

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

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True)

    content: Mapped[str] = mapped_column(Text)

    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True, index=True)

    # Relationships
    comments: Mapped[List["Comment"]] = relationship(
        back_populates="post", cascade="all, delete-orphan"
    )
    reactions: Mapped[List["Reaction"]] = relationship(
        back_populates="post", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index(
            "ix_posts_created_id_desc",
            "date_created",
            "id",
            postgresql_using="btree",
            postgresql_ops={"created_at": "DESC", "id": "DESC"},
        ),  # helper for keyset scans
    )

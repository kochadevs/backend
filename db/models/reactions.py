"""
Common reaction models for the database.
"""
from typing import Optional
from datetime import datetime, timezone
from sqlalchemy import (
    DateTime, ForeignKey, CheckConstraint,
    String, UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.database import Base
from db.models.posts import Post
from db.models.comments import Comment


class Reaction(Base):
    __tablename__ = "reactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    date_created: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        index=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    post_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("posts.id", ondelete="CASCADE"), nullable=True
    )
    comment_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("comments.id", ondelete="CASCADE"), nullable=True
    )
    type: Mapped[str] = mapped_column(String(32))  # e.g., "like", "clap", "love", etc.

    post: Mapped[Optional[Post]] = relationship(back_populates="reactions")
    comment: Mapped[Optional[Comment]] = relationship(back_populates="reactions")

    # Exactly one of (post_id, comment_id) must be non-null
    __table_args__ = (
        # Each user can only react once per target (post/comment) with a given type
        UniqueConstraint("user_id", "type", "post_id", "comment_id", name="ux_reactions_user_target_type"),

        # Enforce that exactly one of post_id or comment_id is set
        CheckConstraint(
            "(post_id IS NOT NULL AND comment_id IS NULL) OR (post_id IS NULL AND comment_id IS NOT NULL)",
            name="ck_reactions_target_exclusivity"
        ),
    )

"""
Model for the comments table
"""
from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy import DateTime, ForeignKey, Index, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.database import Base
from db.models.posts import Post


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True)
    date_created: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc), index=True)
    last_modified: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc))

    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    parent_comment_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("comments.id", ondelete="CASCADE"),
        nullable=True, index=True
    )
    content: Mapped[str] = mapped_column(Text)

    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True, index=True)

    # Relations
    post: Mapped[Post] = relationship(back_populates="comments")
    parent: Mapped[Optional["Comment"]] = relationship(
        remote_side="Comment.id", back_populates="children"
    )
    children: Mapped[List["Comment"]] = relationship(
        back_populates="parent", cascade="all, delete-orphan"
    )
    reactions: Mapped[List["Reaction"]] = relationship(
        back_populates="comment", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index(
            "ix_comments_post_parent_created",
            "post_id", "parent_comment_id", "date_created"
        ),
    )

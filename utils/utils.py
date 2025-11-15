"""
Helper functions for cursor-based pagination.
"""
from typing import Any, Tuple
from datetime import datetime
from base64 import urlsafe_b64encode, urlsafe_b64decode
from fastapi import HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.posts import Post
from db.models.comments import Comment
from db.models.reactions import Reaction
from db.models.chat import ChatRoomMember


def _encode_cursor(ts: datetime, id_: int) -> str:
    payload = f"{ts.isoformat()}|{id_}".encode()
    return urlsafe_b64encode(payload).decode()


def _decode_cursor(cursor: str) -> Tuple[datetime, int]:
    try:
        raw = urlsafe_b64decode(cursor.encode()).decode()
        ts_s, id_s = raw.split("|")
        ts = datetime.fromisoformat(ts_s)
        id_ = int(id_s)
        return ts, id_
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid cursor")


def _visible_posts_where() -> Any:
    return Post.deleted_at.is_(None)


def _visible_comments_where() -> Any:
    return Comment.deleted_at.is_(None)


# Count subqueries (cheap aggregates)
subq_post_comment_count = (
    select(Comment.post_id, func.count(Comment.id).label("cnt"))
    .where(_visible_comments_where(), Comment.parent_comment_id.is_(None))
    .group_by(Comment.post_id)
    .subquery()
)


subq_post_reaction_count = (
    select(Reaction.post_id, func.count(Reaction.id).label("cnt"))
    .where(Reaction.post_id.is_not(None))
    .group_by(Reaction.post_id)
    .subquery()
)


subq_comment_replies_count = (
    select(Comment.parent_comment_id.label("pid"), func.count(Comment.id).label("cnt"))
    .where(_visible_comments_where(), Comment.parent_comment_id.is_not(None))
    .group_by(Comment.parent_comment_id)
    .subquery()
)


subq_comment_reaction_count = (
    select(Reaction.comment_id, func.count(Reaction.id).label("cnt"))
    .where(Reaction.comment_id.is_not(None))
    .group_by(Reaction.comment_id)
    .subquery()
)


async def _validate_room_membership(
    db: AsyncSession, user_id: int, room_id: int
) -> bool:
    result = await db.execute(
        select(ChatRoomMember).where(
            ChatRoomMember.user_id == user_id,
            ChatRoomMember.chat_room_id == room_id
        )
    )
    membership = result.scalars().first()
    return membership is not None


def generate_room_name(sender_email: str, recipient_email: str) -> str:
    """
    Generate a hash-based room name for direct chats
    """
    emails = sorted([sender_email, recipient_email])
    combined = "|".join(emails).encode()
    print(f"Generated room name for {emails}: {combined}")
    return urlsafe_b64encode(combined).decode()

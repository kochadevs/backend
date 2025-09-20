"""
All feed related routes are defined here.
"""
from typing import List, Optional
from datetime import datetime, timezone

from sqlalchemy.orm import Session
from sqlalchemy import select, func, insert
from fastapi import APIRouter, Depends, HTTPException, Query, status

from db.models.user import User
from db.models.posts import Post
from db.models.groups import Group
from db.models.comments import Comment
from db.models.reactions import Reaction
from api.api_models.posts import (
    PostCreate, PostBriefOut, PostOut, PostsPage,
    CommentCreate, CommentOut, CommentsPage,
    ReactionIn, ReactionOut
)

from db.database import get_db
from core.exceptions import exceptions
from utils.oauth2 import get_current_user
from utils.utils import (
    subq_comment_reaction_count,
    subq_post_comment_count,
    subq_post_reaction_count,
    subq_comment_replies_count,
    _encode_cursor,
    _decode_cursor,
    _visible_posts_where,
    _visible_comments_where
)

feed_router = APIRouter(prefix="/feed", tags=["Feed"])


# Create a post
@feed_router.post("/posts", response_model=PostBriefOut, status_code=status.HTTP_201_CREATED)
def create_post(
        payload: PostCreate,
        db: Session = Depends(get_db),
        user: User = Depends(get_current_user),
):
    # If group_id provided, validate group exists and is accessible
    if payload.group_id is not None:
        g = db.get(Group, payload.group_id)
        if not g:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid group")
        if not g.is_public and g.created_by != user.id:
            # Simple visibility rule: only owner can post to private group (adjust as needed)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not allowed to post in this group")
    else:
        payload.group_id = None
    post = Post(user_id=user.id, content=payload.content, group_id=payload.group_id)
    db.add(post)
    db.commit()
    db.refresh(post)

    # Attach counts (zeros)
    return PostBriefOut(
        id=post.id,
        user=user,
        group=post.group,
        content=post.content,
        date_created=post.date_created,
        last_modified=post.last_modified,
        comments_count=0,
        reactions_count=0,
    )


# Soft delete a post
@feed_router.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    post_id: int, db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    post = db.get(Post, post_id)
    if not post or post.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=exceptions.POST_NOT_FOUND
        )
    if post.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=exceptions.NOT_ALLOWED
        )
    post.deleted_at = datetime.now(timezone.utc)
    db.commit()
    return


# List posts (keyset pagination)
@feed_router.get("/posts", response_model=PostsPage)
def list_posts(
    db: Session = Depends(get_db),
    limit: int = Query(20, ge=1, le=100),
    cursor: Optional[str] = Query(None, description="Opaque cursor from previous page"),
    group_id: Optional[int] = Query(None, description="Filter by sub-community. If omitted, browse community posts)."),
):
    stmt = (
        select(
            Post,
            func.coalesce(subq_post_comment_count.c.cnt, 0).label("comments_count"),
            func.coalesce(subq_post_reaction_count.c.cnt, 0).label("reactions_count"),
        )
        .join(subq_post_comment_count, subq_post_comment_count.c.post_id == Post.id, isouter=True)
        .join(subq_post_reaction_count, subq_post_reaction_count.c.post_id == Post.id, isouter=True)
        .where(_visible_posts_where())
    )
    if group_id is not None:
        # validate group exists and is public or accessible (simple rule)
        g = db.get(Group, group_id)
        if not g:
            raise HTTPException(404, "Group not found")
        if not g.is_public:
            raise HTTPException(403, "Group is private")
    stmt = stmt.where(Post.group_id == group_id)

    # Keyset condition
    if cursor:
        ts, last_id = _decode_cursor(cursor)
        stmt = stmt.where(
            (Post.date_created < ts) | ((Post.date_created == ts) & (Post.id < last_id))
        )

    stmt = stmt.order_by(Post.date_created.desc(), Post.id.desc()).limit(limit + 1)

    rows = db.execute(stmt).all()
    items = []
    next_cursor = None

    for row in rows[:limit]:
        post: Post = row[0]
        user = db.query(User).filter(User.id == post.user_id).first()
        items.append(
            PostBriefOut(
                id=post.id,
                user=user,
                group=post.group,
                content=post.content,
                date_created=post.date_created,
                last_modified=post.last_modified,
                comments_count=row.comments_count,
                reactions_count=row.reactions_count,
            )
        )

    if len(rows) > limit:
        last_post: Post = rows[limit - 1][0]
        next_cursor = _encode_cursor(last_post.date_created, last_post.id)

    return PostsPage(items=items, next_cursor=next_cursor)


# Get post detail + first page of top-level comments
@feed_router.get("/posts/{post_id}", response_model=PostOut)
def get_post_detail(
    post_id: int,
    db: Session = Depends(get_db),
    comments_limit: int = Query(10, ge=1, le=100),
    comments_cursor: Optional[str] = Query(None),
):
    # Fetch post + counts
    stmt = (
        select(
            Post,
            func.coalesce(
                subq_post_comment_count.c.cnt, 0).label("comments_count"),
            func.coalesce(
                subq_post_reaction_count.c.cnt, 0).label("reactions_count"),
        )
        .join(subq_post_comment_count, subq_post_comment_count.c.post_id == Post.id, isouter=True)
        .join(subq_post_reaction_count, subq_post_reaction_count.c.post_id == Post.id, isouter=True)
        .where(Post.id == post_id, _visible_posts_where())
        .limit(1)
    )

    row = db.execute(stmt).first()
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=exceptions.POST_NOT_FOUND
        )
    post: Post = row[0]

    # Fetch first page of top-level comments (for convenience)
    comments_page = list_comments(
        post_id=post_id,
        parent_comment_id=None,
        limit=comments_limit,
        cursor=comments_cursor,
        db=db,
    )
    user = db.query(User).filter(User.id == post.user_id).first()

    return PostOut(
        id=post.id,
        user=user,
        group=post.group,
        content=post.content,
        date_created=post.date_created,
        last_modified=post.last_modified,
        comments_count=row.comments_count,
        reactions_count=row.reactions_count,
        top_level_comments=comments_page,
    )


# Create a comment (top-level or reply)
@feed_router.post("/posts/{post_id}/comments", response_model=CommentOut, status_code=status.HTTP_201_CREATED)
def create_comment(
    post_id: int,
    payload: CommentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    # Validate post exists and visible
    post = db.get(Post, post_id)
    if not post or post.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=exceptions.POST_NOT_FOUND
        )

    # If replying to a comment, ensure it belongs to same post and is visible
    if payload.parent_comment_id is not None:
        parent = db.get(Comment, payload.parent_comment_id)
        if not parent or parent.deleted_at is not None or parent.post_id != post_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=exceptions.INVALID_PARENT_COMMENT
            )

    c = Comment(
        post_id=post_id,
        user_id=user.id,
        parent_comment_id=payload.parent_comment_id,
        content=payload.content,
    )
    db.add(c)
    db.commit()
    db.refresh(c)

    # Compose brief counts (0 replies at creation; 0 reactions)
    return CommentOut(
        id=c.id,
        user_id=c.user_id,
        content=c.content,
        date_created=c.date_created,
        last_modified=c.last_modified,
        replies_count=0,
        reactions_count=0,
    )


# Soft delete a comment
@feed_router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(
    comment_id: int, db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    c = db.get(Comment, comment_id)
    if not c or c.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=exceptions.COMMENT_NOT_FOUND
        )
    if c.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=exceptions.NOT_ALLOWED
        )
    c.deleted_at = datetime.now(timezone.utc)
    db.commit()
    return


# List comments for a post and optional parent (top-level or replies) with keyset pagination
@feed_router.get("/posts/{post_id}/comments", response_model=CommentsPage)
def list_comments(
    post_id: int,
    parent_comment_id: Optional[int] = Query(None, description="Null for top-level; otherwise replies under this comment"),
    limit: int = Query(20, ge=1, le=100),
    cursor: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    # Validate post exists
    post = db.get(Post, post_id)
    if not post or post.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=exceptions.POST_NOT_FOUND
        )

    # If fetching replies, validate the parent comment belongs to this post
    if parent_comment_id is not None:
        parent = db.get(Comment, parent_comment_id)
        if not parent or parent.deleted_at is not None or parent.post_id != post_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=exceptions.INVALID_PARENT_COMMENT
            )

    # Base statement: only visible comments, correct post and parent
    stmt = (
        select(
            Comment,
            func.coalesce(subq_comment_replies_count.c.cnt, 0).label("replies_count"),
            func.coalesce(subq_comment_reaction_count.c.cnt, 0).label("reactions_count"),
        )
        .where(
            Comment.post_id == post_id,
            _visible_comments_where(),
            (
                Comment.parent_comment_id.is_(None)
                if parent_comment_id is None
                else Comment.parent_comment_id == parent_comment_id
            ),
        )
        .join(subq_comment_replies_count, subq_comment_replies_count.c.pid == Comment.id, isouter=True)
        .join(subq_comment_reaction_count, subq_comment_reaction_count.c.comment_id == Comment.id, isouter=True)
    )

    if cursor:
        ts, last_id = _decode_cursor(cursor)
        stmt = stmt.where((Comment.date_created < ts) | ((Comment.date_created == ts) & (Comment.id < last_id)))

    stmt = stmt.order_by(Comment.date_created.desc(), Comment.id.desc()).limit(limit + 1)

    rows = db.execute(stmt).all()
    items: List[CommentOut] = []
    next_cursor = None

    for row in rows[:limit]:
        c: Comment = row[0]
        items.append(
            CommentOut(
                id=c.id,
                user_id=c.user_id,
                content=c.content,
                date_created=c.date_created,
                last_modified=c.last_modified,
                replies_count=row.replies_count,
                reactions_count=row.reactions_count,
            )
        )

    if len(rows) > limit:
        last_c: Comment = rows[limit - 1][0]
        next_cursor = _encode_cursor(last_c.date_created, last_c.id)

    return CommentsPage(items=items, next_cursor=next_cursor)


# Upsert/Toggle reaction on a post
@feed_router.put("/posts/{post_id}/reactions", response_model=ReactionOut)
def react_to_post(
    post_id: int,
    payload: ReactionIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    post = db.get(Post, post_id)
    if not post or post.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=exceptions.POST_NOT_FOUND
        )

    # Upsert with PostgreSQL ON CONFLICT via insert(...).on_conflict_do_update
    stmt = (
        insert(Reaction)
        .values(user_id=user.id, post_id=post_id, comment_id=None, type=payload.type)
        .on_conflict_do_update(
            index_elements=[Reaction.user_id, Reaction.type, Reaction.post_id],
            set_={"date_created": func.now()},
        )
        .returning(Reaction)
    )
    r: Reaction = db.execute(stmt).scalar_one()
    db.commit()
    return ReactionOut.model_validate(r)


# Remove reaction from a post
@feed_router.delete("/posts/{post_id}/reactions", status_code=status.HTTP_204_NO_CONTENT)
def unreact_post(
    post_id: int,
    type: str = Query(..., min_length=1, max_length=32),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    deleted = db.query(Reaction).filter(
        Reaction.user_id == user.id,
        Reaction.post_id == post_id, Reaction.type == type
    ).delete(synchronize_session=False)
    if deleted == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=exceptions.REACTION_NOT_FOUND
        )
    db.commit()
    return


# Upsert/Toggle reaction on a comment
@feed_router.put("/comments/{comment_id}/reactions", response_model=ReactionOut)
def react_to_comment(
    comment_id: int,
    payload: ReactionIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    c = db.get(Comment, comment_id)
    if not c or c.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=exceptions.COMMENT_NOT_FOUND
        )

    stmt = (
        insert(Reaction)
        .values(user_id=user.id, post_id=None, comment_id=comment_id, type=payload.type)
        .on_conflict_do_update(
            index_elements=[Reaction.user_id, Reaction.type, Reaction.comment_id],
            set_={"date_created": func.now()},
        )
        .returning(Reaction)
    )
    r: Reaction = db.execute(stmt).scalar_one()
    db.commit()
    return ReactionOut.model_validate(r)


# Remove reaction from a comment
@feed_router.delete("/comments/{comment_id}/reactions", status_code=status.HTTP_204_NO_CONTENT)
def unreact_comment(
    comment_id: int,
    type: str = Query(..., min_length=1, max_length=32),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    deleted = db.query(Reaction).filter(
        Reaction.user_id == user.id,
        Reaction.comment_id == comment_id,
        Reaction.type == type
    ).delete(synchronize_session=False)

    if deleted == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=exceptions.REACTION_NOT_FOUND
        )
    db.commit()
    return

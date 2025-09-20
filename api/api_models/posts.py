"""
Pydantic models for posts and related entities.
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

from api.api_models.login import UserResponse
from api.api_models.groups import GroupOut


class ReactionIn(BaseModel):
    type: str = Field(min_length=1, max_length=32)


class ReactionOut(BaseModel):
    id: int
    user_id: int
    type: str
    date_created: datetime

    class Config:
        from_attributes = True


class CommentCreate(BaseModel):
    content: str = Field(min_length=1, max_length=20_000)
    parent_comment_id: Optional[int] = None


class CommentBriefOut(BaseModel):
    id: int
    user: UserResponse
    content: str
    date_created: datetime
    last_modified: datetime
    replies_count: int
    reactions_count: int

    class Config:
        from_attributes = True


class CommentOut(CommentBriefOut):
    # Full object can include nested replies if needed; here we keep it brief and paginate replies separately.
    pass


class CommentsPage(BaseModel):
    items: List[CommentOut]
    next_cursor: Optional[str]


class PostCreate(BaseModel):
    content: str = Field(min_length=1, max_length=50_000)
    group_id: Optional[int] = None


class PostBriefOut(BaseModel):
    id: int
    user: UserResponse
    group: Optional[GroupOut]
    content: str
    date_created: datetime
    last_modified: datetime
    comments_count: int
    reactions_count: int

    class Config:
        from_attributes = True


class PostOut(PostBriefOut):
    # For post detail, you can include first page of top-level comments.
    top_level_comments: Optional[CommentsPage] = None


class PostsPage(BaseModel):
    items: List[PostBriefOut]
    next_cursor: Optional[str]

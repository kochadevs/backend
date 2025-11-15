"""
Other routes for the chat: history, rooms, members, etc.
"""
from ast import List
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, status, Query

from db.models.user import User
from db.database import async_get_db
from utils.oauth2 import get_current_user
from utils.utils import _validate_room_membership
from db.models.chat import ChatRoom, ChatRoomMember, Message
from api.api_models.chat import ChatRoomCreate, ChatRoomResponse, MessageResponse


chat_utils_router = APIRouter(
    prefix="/chat/utils",
    tags=["Chat Utilities"]
)


@chat_utils_router.post("rooms", status_code=status.HTTP_201_CREATED, response_model=ChatRoomResponse)
async def create_room(
    chat_room_data: ChatRoomCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(async_get_db)
):
    """
    Create a new chat room
    """
    room = ChatRoom(
        name=chat_room_data.name,
        is_public=chat_room_data.is_public,
        chat_type=chat_room_data.chat_type,
        created_by=user.id
    )
    db.add(room)
    await db.flush()

    member = ChatRoomMember(
        chat_room_id=room.id,
        user_id=user.id,
        is_admin=True
    )
    db.add(member)
    await db.commit()
    await db.refresh(room)
    return room


@chat_utils_router.get("/rooms/messages", response_model=list[MessageResponse])
async def get_user_room_messages(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(async_get_db)
):
    """
    Fetch messages from multiple rooms the user is a member of
    """
    # Validate membership for each room
    result1 = await db.execute(
        select(ChatRoom.id).join(ChatRoomMember).where(
            ChatRoomMember.user_id == user.id
        ).offset(0).limit(20).order_by(ChatRoom.date_created.desc())
    )
    room_ids = result1.scalars().all()
    result = await db.execute(
        select(Message).options(
            selectinload(Message.chat_room)
        ).where(Message.chat_room_id.in_(room_ids), Message.deleted.is_(False)).order_by(
            Message.date_created.desc()
        ).offset(0).limit(100)
    )
    messages = result.scalars().all()
    return messages


@chat_utils_router.get("/rooms", response_model=list[ChatRoomResponse])
async def list_rooms(
    skip: int = 0,
    limit: int = Query(default=10, lte=50),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(async_get_db)
):
    """
    List all chat rooms the user is a member of
    """
    result = await db.execute(
        select(ChatRoom).join(ChatRoomMember).where(ChatRoomMember.user_id == user.id).offset(skip).limit(limit)
    )
    rooms = result.scalars().all()
    return rooms


@chat_utils_router.get("/rooms/{room_id}", response_model=ChatRoomResponse)
async def get_room(
    room_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(async_get_db)
):
    """
    Get details of a specific chat room by ID
    """
    result = await db.execute(
        select(ChatRoom).where(ChatRoom.id == room_id)
    )
    room = result.scalars().first()
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat room not found"
        )

    is_member = await _validate_room_membership(db, user.id, room_id)
    if not is_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this chat room"
        )

    return room


@chat_utils_router.get("rooms/{room_id}/messages", response_model=list[MessageResponse])
async def room_history(
    room_id: int,
    skip: int = 0,
    limit: int = Query(default=20, lte=100),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(async_get_db)
):
    """
    Fetch chat history for a specific room
    """
    is_member = await _validate_room_membership(db, user.id, room_id)
    if not is_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this chat room"
        )

    result = await db.execute(
        select(Message).options(
            selectinload(Message.chat_room)
        ).where(Message.chat_room_id == room_id, Message.deleted.is_(False)).order_by(
            Message.date_created.desc()
        ).offset(skip).limit(limit)
    )
    messages = result.scalars().all()
    return messages

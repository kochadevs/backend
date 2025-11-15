"""
Pydantic model for the chat application.
"""
from datetime import datetime
from pydantic import BaseModel, Field


class ChatBase(BaseModel):
    name: str = Field(..., description="Name of the chat room")
    chat_type: str = Field("direct", description="Type of the chat room, e.g., direct or group")
    is_public: bool = Field(False, description="Whether the chat room is public or private")


class ChatRoomCreate(ChatBase):
    pass


class ChatRoomResponse(ChatBase):
    id: int = Field(..., description="Unique identifier for the chat room")
    date_created: datetime
    last_modified: datetime
    created_by: int | None = Field(None, description="ID of the user who created the chat room")

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    id: int
    date_created: datetime
    last_modified: datetime
    chat_room: ChatRoomResponse
    sender_id: int
    content: str
    edited: bool

    class Config:
        from_attributes = True

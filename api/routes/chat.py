"""
The main chat endpoint
"""
import json
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.database import async_get_db
from core.config import settings
from db.models.user import User
from db.models.chat import ChatRoom, ChatRoomMember, Message, MessageDelivery
from services.chat_manager import ConnectionManager
from services.pubsub_manager import RedisPubSubManager
from utils.oauth2 import get_current_user_from_request
from utils.utils import _validate_room_membership, generate_room_name


chat_router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)
manager = ConnectionManager()
pubsub_manager = RedisPubSubManager(redis_url=settings.REDIS_URL)


@chat_router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(...),
    db: AsyncSession = Depends(async_get_db),
):
    """
    WebSocket endpoint for real-time chat communication.
    Requires a valid token and room_id as query parameters.
    """
    await websocket.accept()

    # try:
    while True:
        user: User = await get_current_user_from_request(token, db)
        data = await websocket.receive_json()

        if not data:
            await websocket.send_json({"error": "Invalid action"})
            continue
        # data should be :
        # {"action": "join_room"/"leave_room"/"message", "room_id": int, "content": str}
        action = data.get("action")
        if action == "join_room":
            room_id = data.get("room_id")
            # print(f"User {user.id} joining room {room_id}")
            if not room_id:
                # Check if there is recipient_id for direct chat
                recipient_id = data.get("recipient_id")
                if recipient_id:
                    recipient = await db.get(User, recipient_id)
                    if not recipient:
                        await websocket.send_json({"error": "Invalid room or recipient"})
                        continue
                    room_name = generate_room_name(user.email, recipient.email)
                    room_id_qq = select(ChatRoom.id).where(ChatRoom.name == room_name)
                    room_result = await db.execute(room_id_qq)
                    room_id = room_result.scalar_one_or_none()
                    print(room_id)
                    if not room_id:
                        # create the room
                        new_room = ChatRoom(
                            name=room_name,
                            is_public=False,
                            chat_type="direct",
                            created_by=user.id
                        )
                        db.add(new_room)
                        await db.flush()
                        new_member1 = ChatRoomMember(
                            chat_room_id=new_room.id,
                            user_id=user.id,
                            is_admin=False
                        )
                        db.add(new_member1)
                        new_member2 = ChatRoomMember(
                            chat_room_id=new_room.id,
                            user_id=recipient.id,
                            is_admin=False
                        )
                        db.add(new_member2)
                        await db.commit()
                        room_id = new_room.id
                # await websocket.send_json({"error": "Invalid room or membership"})
                # continue
            room = await db.get(ChatRoom, room_id)
            if not room:
                await websocket.send_json({"error": "Room does not exist"})
                continue
            is_member = await _validate_room_membership(db, user.id, room_id)
            if not is_member and not room.is_public:
                await websocket.send_json({"error": "Not a member of the room"})
                continue
            await manager.add_user_to_room(user.id, room_id, websocket)
            await websocket.send_json({"action": "joined_room", "room_id": room_id})

        elif action == "leave_room":
            room_id = data.get("room_id")
            if not room_id:
                await websocket.send_json({"error": "Invalid room"})
                continue
            await manager.remove_user_from_room(user.id, room_id)
            await websocket.send_json({"action": "left_room", "room_id": room_id})

        elif action == "send_message":
            room_id = data.get("room_id")
            content = data.get("content", "").strip()
            if not content:
                await websocket.send_json({"error": "Message content cannot be empty"})
                continue
            ok = await _validate_room_membership(db, user.id, room_id)
            room = await db.get(ChatRoom, room_id)
            if not room or (not ok and not room.is_public):
                await websocket.send_json({"error": "Not a member or not allowed"})
                continue

            mm = Message(
                chat_room_id=room_id,
                sender_id=user.id,
                content=content
            )
            db.add(mm)
            await db.flush()

            qq = select(
                ChatRoomMember.user_id
            ).where(
                ChatRoomMember.chat_room_id == room_id
            )
            result = await db.execute(qq)
            member_ids = [row[0] for row in result.all()]

            deliveries = []
            t_now = datetime.now(timezone.utc)
            for uid in member_ids:
                deliveries.append(
                    MessageDelivery(message_id=mm.id, user_id=uid, delivered_at=t_now, read_at=None)
                )
            db.add_all(deliveries)
            await db.commit()
            await db.refresh(mm)

            event = {
                "action": "message",
                "message": {
                    "id": mm.id,
                    "chat_room_id": mm.chat_room_id,
                    "sender_id": mm.sender_id,
                    "content": mm.content,
                    "date_created": mm.date_created.isoformat(),
                    "edited": mm.edited,
                    "deleted": mm.deleted
                }
            }

            await manager.broadcast_to_room(event, room_id)

            await pubsub_manager.publish_room(room_id, event)

        elif action == "typing":
            msg_id = data.get("message_id")
            now = datetime.now(timezone.utc)
            nq = select(MessageDelivery).where(
                MessageDelivery.message_id == msg_id,
                MessageDelivery.user_id == user.id
            )
            nr = await db.execute(nq)
            md = nr.scalar_one_or_none()
            if md:
                md.read_at = now
                await db.commit()
                event = {
                    "action": "typing",
                    "message_id": msg_id,
                    "user_id": user.id,
                    "read_at": now.isoformat()
                }

                await manager.broadcast_to_room(event, md.message.chat_room_id)
                await pubsub_manager.publish_room(md.message.chat_room_id, event)
        else:
            await websocket.send_json({"error": "Unknown action"})
    # except WebSocketDisconnect:
    #     await manager.disconnect(user.id)
    # except Exception as outer_exc:
    #     print(f"Error: WebSocket disconnected: {outer_exc.__str__()}")
    #     await manager.disconnect(user.id)
    #     try:
    #         await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
    #     except Exception:
    #         pass

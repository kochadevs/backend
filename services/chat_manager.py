"""
Management for the chat connection
"""
import asyncio
from typing import Dict, Set
from fastapi import WebSocket


class ConnectionManager:
    """
    Processes in-memory websockets per user and per-room membership
    """

    def __init__(self) -> None:
        self.active_connections: Dict[int, WebSocket] = {}
        self.room_members: Dict[int, Set[int]] = {}
        self.lock = asyncio.Lock()

    async def connect(self, user_id: int, websocket: WebSocket) -> None:
        """
        Connects a user to the websocket manager
        """
        # await websocket.accept()
        async with self.lock:
            self.active_connections[user_id] = websocket

    async def disconnect(self, user_id: int) -> None:
        """
        Disconnects a user from the websocket manager
        """
        async with self.lock:
            ws = self.active_connections.pop(user_id, None)
            for member in self.room_members.values():
                member.discard(user_id)
            if ws:
                await ws.close()

    async def add_user_to_room(self, user_id: int, room_id: int, websocket: WebSocket) -> None:
        """
        Adds a user to a chat room
        """
        async with self.lock:
            # print(f"Adding user {user_id} to room {room_id}")
            self.active_connections[user_id] = websocket
            members = self.room_members.setdefault(room_id, set())
            members.add(user_id)

    async def remove_user_from_room(self, user_id: int, room_id: int) -> None:
        """
        Removes a user from a chat room
        """
        async with self.lock:
            members = self.room_members.get(room_id)
            if members:
                members.discard(user_id)
                # if not members:
                #     del self.room_members[room_id]

    async def send_personal_message(self, message: str, user_id: int) -> None:
        """
        Sends a personal message to a user
        """
        # async with self.lock:
        websocket = self.active_connections.get(user_id)
        if websocket:
            await websocket.send_json(message)

    async def broadcast_to_room(self, message: str, room_id: int) -> None:
        """
        Broadcasts a message to all members of a chat room
        """
        async with self.lock:
            members = self.room_members.get(room_id, set())
        for user_id in members:
            websocket = self.active_connections.get(user_id)
            if websocket:
                await websocket.send_json(message)

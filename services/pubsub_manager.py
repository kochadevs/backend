"""
Managing the Pub/Sub service for real-time messaging using redis
"""
import json
import asyncio
from typing import Any
from redis.asyncio import Redis


class RedisPubSubManager:
    """
    Publishes events to redis channels `room:{room_id}`
    Each server instance subscribes to the relevant channels of the rooms to receive events
    This only handles publishing events to redis.
    Subscription is handled in chat_manager.py, requires subscription loop per instance
    """
    def __init__(self, redis_url: str) -> None:
        self.redis_url = redis_url
        self.redis: Redis | None = None

    async def connect(self) -> None:
        self.redis = await Redis.from_url(
            self.redis_url, encoding="utf-8", decode_responses=True)

    async def publish_room(self, room_id: int, event: dict):
        if not self.redis:
            await self.connect()
        channel = f"room:{room_id}"
        await self.redis.publish(channel, json.dumps(event))

    async def subscribe_loop(self, handle_event_cb) -> Any:
        if not self.redis:
            await self.connect()
        pubsub = self.redis.pubsub()
        await pubsub.psubscribe("room:*")
        async for message in pubsub.listen():
            if message is None:
                continue
            if message['type'] in ('pmessage', 'message'):
                channel = message.get('channel') or message.get('pattern')
                data = message.get('data')
                try:
                    event = json.loads(data)
                except Exception:
                    continue
                await handle_event_cb(channel, event)

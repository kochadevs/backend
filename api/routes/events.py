"""
Events routes for regular users
"""
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db.database import get_db
from db.models.user import User
from api.api_models.events import EventResponse
from services.events import EventService
from utils.oauth2 import get_current_user


events_router = APIRouter(prefix="/events", tags=["Events"])


@events_router.get("/upcoming", response_model=List[EventResponse])
async def get_upcoming_events(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get upcoming events (authenticated users)"""
    event_service = EventService(db)
    events = event_service.get_upcoming_events(skip=skip, limit=limit)
    return events


@events_router.get("/{event_id}", response_model=EventResponse)
async def get_event_detail(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get event details (authenticated users)"""
    event_service = EventService(db)
    event = event_service.get_event_by_id(event_id)
    return event

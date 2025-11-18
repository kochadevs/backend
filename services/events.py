"""
Service for event management
"""
import logging
from typing import List, Optional
from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_

from api.api_models.events import EventCreate, EventUpdate, EventResponse
from db.models.events import Event
from db.models.user import User
from db.repository.crud import Crud


logger = logging.getLogger(__name__)


class EventService:
    def __init__(self, db: Session):
        self.crud = Crud(db)
        self.db = db

    def create_event(self, event_data: EventCreate, admin_user: User) -> Event:
        """Create a new event (admin only)"""
        try:
            event_dict = event_data.model_dump()
            event_dict["created_by"] = admin_user.id
            
            event = self.crud.create(Event, event_dict)
            self.db.commit()
            return event

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating event: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    def get_event_by_id(self, event_id: int) -> Optional[Event]:
        """Get event by ID"""
        event = self.crud.get(Event, event_id)
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )
        return event

    def get_all_events(self, skip: int = 0, limit: int = 10, active_only: bool = False) -> List[Event]:
        """Get all events with pagination"""
        query = self.db.query(Event)
        if active_only:
            query = query.filter(Event.is_active.is_(True))

        return query.order_by(Event.event_date.desc()).offset(skip).limit(limit).all()

    def get_upcoming_events(self, skip: int = 0, limit: int = 10) -> List[Event]:
        """Get upcoming events (active events with future dates)"""
        now = datetime.now()
        return self.db.query(Event).filter(
            and_(
                Event.is_active.is_(True),
                Event.start_date >= now
            )
        ).order_by(Event.start_date.asc()).offset(skip).limit(limit).all()

    def update_event(self, event_id: int, event_data: EventUpdate) -> Event:
        """Update an event (admin only)"""
        try:
            event = self.get_event_by_id(event_id)
            
            update_data = event_data.model_dump(exclude_unset=True)
            updated_event = self.crud.update(event, update_data)
            self.db.commit()
            return updated_event

        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating event: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    def delete_event(self, event_id: int) -> bool:
        """Delete an event (admin only)"""
        try:
            event = self.get_event_by_id(event_id)
            self.db.delete(event)
            self.db.commit()
            return True

        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting event: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    def deactivate_event(self, event_id: int) -> Event:
        """Deactivate an event instead of deleting it (admin only)"""
        return self.update_event(event_id, EventUpdate(is_active=False))

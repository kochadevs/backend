"""
Admin routes for user and event management
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from db.database import get_db
from db.models.user import User
from api.api_models.user import AllUserResponse, AdminCreateRequest
from api.api_models.events import EventCreate, EventUpdate, EventResponse
from api.api_models.login import UserResponse
from services.user import UserService
from services.events import EventService
from utils.permissions import is_admin
from utils.oauth2 import get_current_user, get_password_hash
from utils.enums import UserTypeEnum
from core.exceptions import exceptions


admin_router = APIRouter(prefix="/admin", tags=["Admin"])


# User Management Routes
@admin_router.post("/users/create-admin", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_admin_user(
    admin_data: AdminCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(is_admin)
):
    """
    Create a new admin user (admin only).
    Only existing admins can create new admin accounts.
    """
    try:
        # Check if email already exists
        existing_user = db.query(User).filter(User.email == admin_data.email.lower()).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=exceptions.USER_EXISTS
            )

        # Create admin user
        new_admin = User(
            first_name=admin_data.first_name,
            last_name=admin_data.last_name,
            email=admin_data.email.lower(),
            password=get_password_hash(admin_data.password),
            gender=admin_data.gender,
            nationality=admin_data.nationality,
            location=admin_data.location,
            phone=admin_data.phone,
            user_type=UserTypeEnum.admin,
            is_active=True,  # Admins are active by default
            email_verified=True  # Admins don't need email verification
        )

        db.add(new_admin)
        db.commit()
        db.refresh(new_admin)

        return new_admin

    except HTTPException as e:
        db.rollback()
        raise e
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@admin_router.get("/users", response_model=List[AllUserResponse])
async def get_all_users(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(is_admin)
):
    """Get all users (admin only)"""
    user_service = UserService(db)
    users = user_service.get_all_users(skip=skip, limit=limit)
    return users


@admin_router.patch("/users/{user_id}/user-type")
async def change_user_type(
    user_id: int,
    new_user_type: UserTypeEnum,
    db: Session = Depends(get_db),
    current_user: User = Depends(is_admin)
):
    """Change a user's type (admin only)"""
    user_service = UserService(db)
    updated_user = user_service.update_user(user_id, {"user_type": new_user_type})
    return {
        "message": "User type updated successfully",
        "user_id": updated_user.id,
        "new_user_type": updated_user.user_type
    }


@admin_router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(is_admin)
):
    """Delete a user (admin only)"""
    user_service = UserService(db)
    user_service.delete_user(user_id)
    return {"message": "User deleted successfully"}


# Event Management Routes
@admin_router.post("/events", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(
    event_data: EventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(is_admin)
):
    """Create a new event (admin only)"""
    event_service = EventService(db)
    event = event_service.create_event(event_data, current_user)
    return event


@admin_router.get("/events", response_model=List[EventResponse])
async def get_all_events(
    skip: int = 0,
    limit: int = 10,
    active_only: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(is_admin)
):
    """Get all events with filters (admin only)"""
    event_service = EventService(db)
    events = event_service.get_all_events(skip=skip, limit=limit, active_only=active_only)
    return events


@admin_router.get("/events/{event_id}", response_model=EventResponse)
async def get_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(is_admin)
):
    """Get a specific event (admin only)"""
    event_service = EventService(db)
    event = event_service.get_event_by_id(event_id)
    return event


@admin_router.put("/events/{event_id}", response_model=EventResponse)
async def update_event(
    event_id: int,
    event_data: EventUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(is_admin)
):
    """Update an event (admin only)"""
    event_service = EventService(db)
    event = event_service.update_event(event_id, event_data)
    return event


@admin_router.delete("/events/{event_id}")
async def delete_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(is_admin)
):
    """Delete an event (admin only)"""
    event_service = EventService(db)
    event_service.delete_event(event_id)
    return {"message": "Event deleted successfully"}


@admin_router.patch("/events/{event_id}/deactivate")
async def deactivate_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(is_admin)
):
    """Deactivate an event (admin only)"""
    event_service = EventService(db)
    event = event_service.deactivate_event(event_id)
    return {"message": "Event deactivated successfully", "event": event}

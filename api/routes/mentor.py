"""
Route for the mentor resource.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import insert

from db.database import get_db
from db.models.user import User
from utils.enums import UserTypeEnum
from core.exceptions import exceptions
from utils.oauth2 import get_current_user
from db.models.mentors import MentorPackage, MentorBooking
from api.api_models.user import UserResponse
from api.api_models.mentors import (
    MentorPackageCreate, MentorPackageResponse,
    MentorBookingResponse, MentorBookingCreate
)


mentor_router = APIRouter(tags=["Mentor"], prefix="/mentors")


@mentor_router.get("/", response_model=list[UserResponse])
def get_mentors(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    if not user.user_type == UserTypeEnum.mentee:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only mentees can access this resource."
        )
    # Logic to fetch and return mentors would go here
    all_mentors = db.query(User).filter(
        User.user_type == UserTypeEnum.mentor,
        User.is_active.is__(True)
    ).all()
    return all_mentors


@mentor_router.post("/packages", response_model=MentorPackageResponse)
def create_mentor_package(
    package_data: MentorPackageCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    if not user.user_type == UserTypeEnum.mentor:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only mentors can create packages."
        )
    # Logic to create a mentor package would go here
    new_package = package_data.model_dump()
    new_package["user_id"] = user.id
    mentor_package = db.execute(
        insert(MentorPackage).values(**new_package).returning(MentorPackage)
    ).scalar_one()
    db.commit()
    return mentor_package


@mentor_router.get("/packages", response_model=list[MentorPackageResponse])
def get_mentors_packages(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    if not user.user_type == UserTypeEnum.mentee:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only mentees can access this resource."
        )
    # Logic to fetch and return mentor packages would go here
    all_packages = db.query(MentorPackage).filter(
        MentorPackage.is_active.is_(True)
    ).all()
    return all_packages


@mentor_router.get("/packages/me", response_model=list[MentorPackageResponse])
def get_my_mentor_packages(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    if not user.user_type == UserTypeEnum.mentor:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only mentors can access this resource."
        )
    # Logic to fetch and return the mentor's own packages would go here
    my_packages = db.query(MentorPackage).filter(
        MentorPackage.user_id == user.id
    ).all()
    return my_packages


@mentor_router.patch("/packages/{package_id}", response_model=MentorPackageResponse)
def update_mentor_package(
    package_id: int,
    package_data: MentorPackageCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    if not user.user_type == UserTypeEnum.mentor:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only mentors can update packages."
        )
    # Logic to update a mentor package would go here
    mentor_package = db.query(MentorPackage).filter(
        MentorPackage.id == package_id,
        MentorPackage.user_id == user.id
    ).first()
    if not mentor_package:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mentor package not found."
        )
    for key, value in package_data.model_dump(exclude_unset=True).items():
        setattr(mentor_package, key, value)
    db.commit()
    db.refresh(mentor_package)
    return mentor_package


@mentor_router.delete("/packages/{package_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_mentor_package(
    package_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    if not user.user_type == UserTypeEnum.mentor:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=exceptions.MENTOR_PACKAGE_FORBIDDEN
        )
    # Logic to delete a mentor package would go here
    mentor_package = db.query(MentorPackage).filter(
        MentorPackage.id == package_id,
        MentorPackage.user_id == user.id
    ).first()
    if not mentor_package:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=exceptions.MENTOR_PACKAGE_NOT_FOUND
        )
    db.delete(mentor_package)
    db.commit()
    return


@mentor_router.post(
    "/bookings/{mentor_id}/create", response_model=MentorBookingResponse
)
def create_mentor_booking(
    booking: MentorBookingCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    if not user.user_type == UserTypeEnum.mentee:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only mentees can create bookings."
        )
    # Logic to create a mentor booking would go here
    booking_data = booking.model_dump()
    booking_data["mentee_id"] = user.id
    created_booking = db.execute(insert(MentorBooking).values(**booking_data))
    db.commit()
    db.refresh(created_booking)
    return created_booking


@mentor_router.patch(
    "/bookings/{booking_id}/confirm", response_model=MentorBookingResponse
)
def confirm_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    if not user.user_type == UserTypeEnum.mentor:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only mentors can confirm bookings."
        )
    # Logic to confirm a booking would go here
    booking = db.query(MentorBooking).filter(
        MentorBooking.id == booking_id,
        MentorBooking.mentor_id == user.id
    ).first()
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=exceptions.MENTOR_BOOKING_NOT_FOUND
        )
    booking.status = "confirmed"
    db.commit()
    db.refresh(booking)
    return booking


@mentor_router.patch(
    "/bookings/{booking_id}/cancel", response_model=MentorBookingResponse
)
def cancel_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    if user.user_type not in [UserTypeEnum.mentor, UserTypeEnum.mentee]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only mentors or mentees can cancel bookings."
        )
    # Logic to cancel a booking would go here
    booking = db.query(MentorBooking).filter(
        MentorBooking.id == booking_id
    ).first()
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=exceptions.MENTOR_BOOKING_NOT_FOUND
        )
    if user.user_type == UserTypeEnum.mentor and booking.mentor_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=exceptions.MENTOR_BOOKING_FORBIDDEN
        )
    if user.user_type == UserTypeEnum.mentee and booking.mentee_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=exceptions.MENTEE_BOOKING_FORBIDDEN
        )
    booking.status = "canceled"
    db.commit()
    db.refresh(booking)
    return booking


@mentor_router.get(
    "/bookings/me", response_model=list[MentorBookingResponse]
)
def get_bookings_for_user(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    # Logic to fetch and return bookings for the current user would go here
    try:
        if user.user_type == UserTypeEnum.mentor:
            bookings = db.query(MentorBooking).filter(
                MentorBooking.mentor_id == user.id
            ).all()
        else:
            bookings = db.query(MentorBooking).filter(
                MentorBooking.mentee_id == user.id
            ).all()
        return bookings
    except (Exception, HTTPException) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@mentor_router.get(
    "/bookings/{booking_id}", response_model=MentorBookingResponse
)
def get_booking_details(
    booking_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    # Logic to fetch and return booking details would go here
    try:
        booking = db.query(MentorBooking).filter(
            MentorBooking.id == booking_id
        ).first()
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=exceptions.MENTOR_BOOKING_NOT_FOUND
            )
        if user.user_type == UserTypeEnum.mentor and booking.mentor_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=exceptions.MENTOR_BOOKING_FORBIDDEN
            )
        if user.user_type == UserTypeEnum.mentee and booking.mentee_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=exceptions.MENTEE_BOOKING_FORBIDDEN
            )
        return booking
    except (Exception, HTTPException) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@mentor_router.delete(
    "/bookings/{booking_id}", status_code=status.HTTP_204_NO_CONTENT
)
def delete_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    # Logic to delete a booking would go here
    try:
        booking = db.query(MentorBooking).filter(
            MentorBooking.id == booking_id
        ).first()
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=exceptions.MENTOR_BOOKING_NOT_FOUND
            )
        if user.user_type == UserTypeEnum.mentor and booking.mentor_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=exceptions.MENTOR_BOOKING_FORBIDDEN
            )
        if user.user_type == UserTypeEnum.mentee and booking.mentee_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=exceptions.MENTEE_BOOKING_FORBIDDEN
            )
        db.delete(booking)
        db.commit()
        return
    except (Exception, HTTPException) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

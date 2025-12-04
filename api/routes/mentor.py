"""
Route for the mentor resource.
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import or_, and_

from db.database import get_db
from db.models.user import User
from utils.enums import UserTypeEnum
from core.exceptions import exceptions
from utils.oauth2 import get_current_user
from db.models.mentors import MentorPackage, MentorBooking
from api.api_models.login import UserResponse
from api.api_models.mentors import (
    MentorPackageCreate, MentorPackageResponse,
    MentorBookingResponse, MentorBookingCreate,
    MentorScheduleResponse, MentorBookingDetailedResponse
)
from utils.enums import MentorBookingStatusEnum
from services.user import UserService


mentor_router = APIRouter(tags=["Mentor"], prefix="/mentors")


@mentor_router.get("/", response_model=list[UserResponse])
def get_mentors(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    user_service = UserService(db)
    mentors = db.query(User).filter(
        User.user_type == UserTypeEnum.mentor,
        User.is_active.is_(True)
    ).all()
    # Convert to UserResponse format (same as login response)
    mentor_profiles = [user_service.get_user_profile(mentor.id) for mentor in mentors]
    return mentor_profiles


@mentor_router.get("/mentees", response_model=list[UserResponse])
def get_all_mentees(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Get all mentees in the system.
    Only accessible by mentors.
    """

    user_service = UserService(db)
    mentees = db.query(User).filter(
        User.user_type == UserTypeEnum.mentee,
        User.is_active.is_(True)
    ).offset(skip).limit(limit).all()

    # Convert to UserResponse format (same as login response)
    mentee_profiles = [user_service.get_user_profile(mentee.id) for mentee in mentees]
    return mentee_profiles


@mentor_router.get("/mentees/me", response_model=list[UserResponse])
def get_my_mentees(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Get all mentees who have bookings with the current mentor.
    Returns unique mentees who have had at least one booking with the mentor.
    Only accessible by mentors.
    """
    if user.user_type != UserTypeEnum.mentor:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only mentors can access this resource."
        )
    
    user_service = UserService(db)
    
    # Get unique mentees who have bookings with this mentor
    mentee_ids = db.query(MentorBooking.mentee_id).filter(
        MentorBooking.mentor_id == user.id
    ).distinct().all()
    
    # Extract IDs from result tuples
    mentee_id_list = [mentee_id[0] for mentee_id in mentee_ids]
    
    # Fetch full user details for these mentees
    mentees = db.query(User).filter(
        User.id.in_(mentee_id_list),
        User.is_active.is_(True)
    ).all()
    
    # Convert to UserResponse format (same as login response)
    mentee_profiles = [user_service.get_user_profile(mentee.id) for mentee in mentees]
    return mentee_profiles


@mentor_router.get("/search", response_model=list[UserResponse])
def search_mentors(
    query: Optional[str] = Query(None, description="Search by name, role, or bio"),
    location: Optional[str] = Query(None, description="Filter by location (city/country)"),
    skill_ids: Optional[str] = Query(None, description="Comma-separated skill IDs"),
    industry_ids: Optional[str] = Query(None, description="Comma-separated industry IDs"),
    role_ids: Optional[str] = Query(None, description="Comma-separated role of interest IDs"),
    min_price: Optional[int] = Query(None, description="Minimum package price"),
    max_price: Optional[int] = Query(None, description="Maximum package price"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Search and filter mentors by various criteria.

    Examples:
    - /mentors/search?query=engineer
    - /mentors/search?location=Lagos
    - /mentors/search?skill_ids=1,2,3
    - /mentors/search?min_price=5000&max_price=20000
    - /mentors/search?query=software&location=Nigeria&skill_ids=5
    """
    try:
        # Base query - only active mentors
        mentor_query = db.query(User).filter(
            User.user_type == UserTypeEnum.mentor,
            User.is_active == True
        )

        # Text search in name, current_role, and about (bio)
        if query:
            search_filter = or_(
                User.first_name.ilike(f"%{query}%"),
                User.last_name.ilike(f"%{query}%"),
                User.current_role.ilike(f"%{query}%"),
                User.about.ilike(f"%{query}%")
            )
            mentor_query = mentor_query.filter(search_filter)

        # Filter by location (matches both nationality and location fields)
        if location:
            location_filter = or_(
                User.location.ilike(f"%{location}%"),
                User.nationality.ilike(f"%{location}%")
            )
            mentor_query = mentor_query.filter(location_filter)

        # Filter by skills
        if skill_ids:
            from db.models.onboarding import Skills
            skill_id_list = [int(sid.strip()) for sid in skill_ids.split(",") if sid.strip()]
            if skill_id_list:
                mentor_query = mentor_query.join(User.skills).filter(
                    Skills.id.in_(skill_id_list)
                )

        # Filter by industries
        if industry_ids:
            from db.models.onboarding import Industry
            industry_id_list = [int(iid.strip()) for iid in industry_ids.split(",") if iid.strip()]
            if industry_id_list:
                mentor_query = mentor_query.join(User.industry).filter(
                    Industry.id.in_(industry_id_list)
                )

        # Filter by roles of interest
        if role_ids:
            from db.models.onboarding import RoleofInterest
            role_id_list = [int(rid.strip()) for rid in role_ids.split(",") if rid.strip()]
            if role_id_list:
                mentor_query = mentor_query.join(User.role_of_interest).filter(
                    RoleofInterest.id.in_(role_id_list)
                )

        # Filter by package price range
        if min_price is not None or max_price is not None:
            # Join with mentor packages to filter by price
            mentor_query = mentor_query.join(User.mentor_packages).filter(
                MentorPackage.is_active == True
            )
            if min_price is not None:
                mentor_query = mentor_query.filter(MentorPackage.price >= min_price)
            if max_price is not None:
                mentor_query = mentor_query.filter(MentorPackage.price <= max_price)

        # Remove duplicates (in case of multiple package matches)
        mentor_query = mentor_query.distinct()

        # Apply pagination
        mentors = mentor_query.offset(skip).limit(limit).all()

        return mentors

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid parameter format: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


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
            detail=exceptions.MENTEES_RESTRICTION_TO_BOOKINGS
        )
    # Logic to create a mentor booking would go here
    booking_data = booking.model_dump()
    booking_data["mentee_id"] = user.id
    created_booking = MentorBooking(**booking_data)
    db.add(created_booking)
    db.commit()
    db.refresh(created_booking)
    return created_booking


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
    booking.status = MentorBookingStatusEnum.cancelled.value
    db.commit()
    db.refresh(booking)
    return booking


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
    booking.status = MentorBookingStatusEnum.confirmed.value
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
    "/bookings/schedule", response_model=MentorScheduleResponse
)
def get_mentor_schedule(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Get mentor's complete schedule with busy slots marked.
    Only accessible by mentors.
    """
    if user.user_type != UserTypeEnum.mentor:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only mentors can access their schedule."
        )

    try:
        # Fetch all bookings for the mentor with related data
        bookings = db.query(MentorBooking).filter(
            MentorBooking.mentor_id == user.id
        ).all()

        # Build detailed response with busy status
        detailed_bookings = []
        for booking in bookings:
            # Each booking represents a busy slot
            detailed_booking = MentorBookingDetailedResponse(
                id=booking.id,
                booking_date=booking.booking_date,
                status=booking.status.value if hasattr(booking.status, 'value') else booking.status,
                notes=booking.notes,
                date_created=booking.date_created,
                last_modified=booking.last_modified,
                mentor=booking.mentor,
                mentee=booking.mentee,
                mentor_package=booking.mentor_package,
                is_busy=True  # All bookings mark slots as busy
            )
            detailed_bookings.append(detailed_booking)

        return MentorScheduleResponse(
            mentor_id=user.id,
            bookings=detailed_bookings,
            total_bookings=len(detailed_bookings)
        )
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


@mentor_router.get("{mentor_id}/packages", response_model=list[MentorPackageResponse])
def get_packages_for_mentor(
    mentor_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Get all active packages for a specific mentor.
    """
    if not user.user_type == UserTypeEnum.mentee:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=exceptions.MENTEES_RESTRICTION_TO_PACKAGES
        )
    # Logic to fetch and return mentor packages would go here
    mentor = db.query(User).filter(
        User.id == mentor_id,
        User.user_type == UserTypeEnum.mentor,
        User.is_active.is_(True)
    ).first()
    if not mentor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mentor not found."
        )
    packages = db.query(MentorPackage).filter(
        MentorPackage.user_id == mentor_id,
        MentorPackage.is_active.is_(True)
    ).all()
    return packages


@mentor_router.get("{mentor_id}/details", response_model=UserResponse)
def get_mentor_details(
    mentor_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Get details of a specific mentor.
    """
    # Logic to fetch and return mentor details would go here
    mentor = db.query(User).filter(
        User.id == mentor_id,
        User.user_type == UserTypeEnum.mentor,
        User.is_active.is_(True)
    ).first()
    if not mentor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=exceptions.MENTOR_NOT_FOUND
        )
    return mentor


@mentor_router.get("/{mentor_id}/schedule", response_model=MentorScheduleResponse)
def get_specific_mentor_schedule(
    mentor_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Get a specific mentor's schedule with busy slots marked.
    Useful for mentees to see when a mentor is available.
    """
    # Verify the mentor exists and is active
    mentor = db.query(User).filter(
        User.id == mentor_id,
        User.user_type == UserTypeEnum.mentor,
        User.is_active.is_(True)
    ).first()

    if not mentor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=exceptions.MENTOR_NOT_FOUND
        )

    try:
        # Fetch all bookings for the specified mentor
        # Only show confirmed/accepted bookings to protect privacy
        bookings = db.query(MentorBooking).filter(
            MentorBooking.mentor_id == mentor_id,
            MentorBooking.status.in_([
                MentorBookingStatusEnum.confirmed,
                MentorBookingStatusEnum.accepted
            ])
        ).all()

        # Build detailed response
        detailed_bookings = []
        for booking in bookings:
            detailed_booking = MentorBookingDetailedResponse(
                id=booking.id,
                booking_date=booking.booking_date,
                status=booking.status.value if hasattr(booking.status, 'value') else booking.status,
                notes=None,  # Don't expose notes to other users
                date_created=booking.date_created,
                last_modified=booking.last_modified,
                mentor=booking.mentor,
                mentee=booking.mentee,
                mentor_package=booking.mentor_package,
                is_busy=True
            )
            detailed_bookings.append(detailed_booking)

        return MentorScheduleResponse(
            mentor_id=mentor_id,
            bookings=detailed_bookings,
            total_bookings=len(detailed_bookings)
        )
    except (Exception, HTTPException) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

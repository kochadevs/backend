"""
Dashboard API endpoints
"""
from datetime import datetime, timezone
from typing import Any, Optional
from pydantic import BaseModel

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from db.database import get_db
from db.models.user import User
from db.models.mentors import MentorBooking, MentorPackage
from utils.oauth2 import get_current_user
from utils.enums import MentorBookingStatusEnum, UserTypeEnum
from api.api_models.login import UserResponse


dashboard_router = APIRouter(tags=["Dashboard"], prefix="/dashboard")


class SessionCounts(BaseModel):
    scheduled: int = 0
    pending_approval: int = 0
    past_sessions: int = 0


class UpcomingSession(BaseModel):
    id: int
    booking_date: datetime
    status: str
    mentor_id: int
    mentor_name: str
    mentor_profile_pic: Optional[str] = None
    mentee_id: int
    mentee_name: str
    mentee_profile_pic: Optional[str] = None
    package_name: str
    package_duration: str
    notes: Optional[str] = None


class GoalProgress(BaseModel):
    id: int
    name: str
    completed: bool = False


class MentorInfo(BaseModel):
    id: int
    name: str
    profile_pic: Optional[str] = None
    current_role: Optional[str] = None
    skills: list[str] = []


class RecentMember(BaseModel):
    id: int
    name: str
    profile_pic: Optional[str] = None
    current_role: Optional[str] = None
    user_type: str
    location: Optional[str] = None
    joined_at: datetime


class DashboardResponse(BaseModel):
    user: UserResponse
    session_counts: SessionCounts
    upcoming_sessions: list[UpcomingSession]
    goals: list[GoalProgress]
    recommended_mentors: list[MentorInfo]
    recent_members: list[RecentMember]
    needs_user_type_selection: bool


@dashboard_router.get("/", response_model=DashboardResponse)
def get_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Get dashboard data for the current user"""
    try:
        user = db.query(User).filter(User.id == current_user.id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        now = datetime.now(timezone.utc)

        # Get session counts
        session_counts = SessionCounts()

        # Get bookings where user is either mentor or mentee
        user_bookings = db.query(MentorBooking).filter(
            or_(
                MentorBooking.mentor_id == user.id,
                MentorBooking.mentee_id == user.id
            )
        ).all()

        for booking in user_bookings:
            if booking.status == MentorBookingStatusEnum.pending:
                session_counts.pending_approval += 1
            elif booking.status in [MentorBookingStatusEnum.accepted, MentorBookingStatusEnum.confirmed]:
                if booking.booking_date > now:
                    session_counts.scheduled += 1
                else:
                    session_counts.past_sessions += 1
            elif booking.status == MentorBookingStatusEnum.completed:
                session_counts.past_sessions += 1

        # Get upcoming sessions (next 5)
        upcoming_bookings = db.query(MentorBooking).filter(
            or_(
                MentorBooking.mentor_id == user.id,
                MentorBooking.mentee_id == user.id
            ),
            MentorBooking.booking_date > now,
            MentorBooking.status.in_([
                MentorBookingStatusEnum.accepted,
                MentorBookingStatusEnum.confirmed,
                MentorBookingStatusEnum.pending
            ])
        ).order_by(MentorBooking.booking_date.asc()).limit(5).all()

        upcoming_sessions = []
        for booking in upcoming_bookings:
            mentor = db.query(User).filter(User.id == booking.mentor_id).first()
            mentee = db.query(User).filter(User.id == booking.mentee_id).first()
            package = db.query(MentorPackage).filter(MentorPackage.id == booking.mentor_package_id).first()

            upcoming_sessions.append(UpcomingSession(
                id=booking.id,
                booking_date=booking.booking_date,
                status=booking.status.value,
                mentor_id=booking.mentor_id,
                mentor_name=f"{mentor.first_name} {mentor.last_name or ''}".strip() if mentor else "Unknown",
                mentor_profile_pic=mentor.profile_pic if mentor else None,
                mentee_id=booking.mentee_id,
                mentee_name=f"{mentee.first_name} {mentee.last_name or ''}".strip() if mentee else "Unknown",
                mentee_profile_pic=mentee.profile_pic if mentee else None,
                package_name=package.name if package else "Unknown",
                package_duration=package.duration if package else "Unknown",
                notes=booking.notes
            ))

        # Get goals from career_goals
        goals = []
        if user.career_goals:
            for goal in user.career_goals:
                goals.append(GoalProgress(
                    id=goal.id,
                    name=goal.name,
                    completed=False  # This could be tracked separately in future
                ))

        # Get recommended mentors (for mentees)
        recommended_mentors = []
        if user.user_type in [UserTypeEnum.regular, UserTypeEnum.mentee]:
            mentors = db.query(User).filter(
                User.user_type == UserTypeEnum.mentor,
                User.is_active == True,
                User.id != user.id
            ).limit(5).all()

            for mentor in mentors:
                mentor_skills = [skill.name for skill in mentor.skills] if mentor.skills else []
                recommended_mentors.append(MentorInfo(
                    id=mentor.id,
                    name=f"{mentor.first_name} {mentor.last_name or ''}".strip(),
                    profile_pic=mentor.profile_pic,
                    current_role=mentor.current_role,
                    skills=mentor_skills
                ))

        # Get recent members (people who recently joined)
        recent_users = db.query(User).filter(
            User.is_active == True,
            User.id != user.id
        ).order_by(User.date_created.desc()).limit(5).all()

        recent_members = []
        for member in recent_users:
            recent_members.append(RecentMember(
                id=member.id,
                name=f"{member.first_name} {member.last_name or ''}".strip(),
                profile_pic=member.profile_pic,
                current_role=member.current_role,
                user_type=member.user_type.value,
                location=member.location,
                joined_at=member.date_created
            ))

        # Check if user needs to select user type
        needs_user_type_selection = user.user_type == UserTypeEnum.regular

        # Build user response
        user_response = UserResponse(
            id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            gender=user.gender,
            nationality=user.nationality,
            location=user.location,
            phone=user.phone,
            is_active=user.is_active,
            email_verified=user.email_verified,
            profile_pic=user.profile_pic,
            cover_photo=user.cover_photo,
            about=user.about,
            current_role=user.current_role,
            user_type=user.user_type,
            social_links=user.social_links,
            availability=user.availability,
            new_role_values=[{"id": r.id, "name": r.name} for r in user.new_role_values] if user.new_role_values else None,
            job_search_status=[{"id": j.id, "name": j.name} for j in user.job_search_status] if user.job_search_status else None,
            role_of_interest=[{"id": r.id, "name": r.name, "category": r.category} for r in user.role_of_interest] if user.role_of_interest else None,
            industry=[{"id": i.id, "name": i.name} for i in user.industry] if user.industry else None,
            skills=[{"id": s.id, "name": s.name} for s in user.skills] if user.skills else None,
            career_goals=[{"id": c.id, "name": c.name} for c in user.career_goals] if user.career_goals else None
        )

        return DashboardResponse(
            user=user_response,
            session_counts=session_counts,
            upcoming_sessions=upcoming_sessions,
            goals=goals,
            recommended_mentors=recommended_mentors,
            recent_members=recent_members,
            needs_user_type_selection=needs_user_type_selection
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@dashboard_router.get("/sessions", response_model=list[UpcomingSession])
def get_user_sessions(
    session_type: str = "all",  # all, scheduled, pending, past
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Get user's sessions with filtering"""
    try:
        now = datetime.now(timezone.utc)

        query = db.query(MentorBooking).filter(
            or_(
                MentorBooking.mentor_id == current_user.id,
                MentorBooking.mentee_id == current_user.id
            )
        )

        if session_type == "scheduled":
            query = query.filter(
                MentorBooking.booking_date > now,
                MentorBooking.status.in_([
                    MentorBookingStatusEnum.accepted,
                    MentorBookingStatusEnum.confirmed
                ])
            )
        elif session_type == "pending":
            query = query.filter(
                MentorBooking.status == MentorBookingStatusEnum.pending
            )
        elif session_type == "past":
            query = query.filter(
                or_(
                    MentorBooking.booking_date < now,
                    MentorBooking.status == MentorBookingStatusEnum.completed
                )
            )

        bookings = query.order_by(MentorBooking.booking_date.desc()).offset(skip).limit(limit).all()

        sessions = []
        for booking in bookings:
            mentor = db.query(User).filter(User.id == booking.mentor_id).first()
            mentee = db.query(User).filter(User.id == booking.mentee_id).first()
            package = db.query(MentorPackage).filter(MentorPackage.id == booking.mentor_package_id).first()

            sessions.append(UpcomingSession(
                id=booking.id,
                booking_date=booking.booking_date,
                status=booking.status.value,
                mentor_id=booking.mentor_id,
                mentor_name=f"{mentor.first_name} {mentor.last_name or ''}".strip() if mentor else "Unknown",
                mentor_profile_pic=mentor.profile_pic if mentor else None,
                mentee_id=booking.mentee_id,
                mentee_name=f"{mentee.first_name} {mentee.last_name or ''}".strip() if mentee else "Unknown",
                mentee_profile_pic=mentee.profile_pic if mentee else None,
                package_name=package.name if package else "Unknown",
                package_duration=package.duration if package else "Unknown",
                notes=booking.notes
            ))

        return sessions

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@dashboard_router.get("/recent-members", response_model=list[RecentMember])
def get_recent_members(
    skip: int = 0,
    limit: int = 10,
    user_type: Optional[str] = None,  # Filter by user type: mentor, mentee, regular
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Get recently joined members with optional filtering by user type"""
    try:
        query = db.query(User).filter(
            User.is_active == True,
            User.id != current_user.id
        )

        # Filter by user type if specified
        if user_type:
            if user_type == "mentor":
                query = query.filter(User.user_type == UserTypeEnum.mentor)
            elif user_type == "mentee":
                query = query.filter(User.user_type == UserTypeEnum.mentee)
            elif user_type == "regular":
                query = query.filter(User.user_type == UserTypeEnum.regular)

        # Order by most recent and apply pagination
        recent_users = query.order_by(User.date_created.desc()).offset(skip).limit(limit).all()

        recent_members = []
        for member in recent_users:
            recent_members.append(RecentMember(
                id=member.id,
                name=f"{member.first_name} {member.last_name or ''}".strip(),
                profile_pic=member.profile_pic,
                current_role=member.current_role,
                user_type=member.user_type.value,
                location=member.location,
                joined_at=member.date_created
            ))

        return recent_members

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

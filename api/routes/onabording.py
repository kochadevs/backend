from typing import Any, List
from fastapi import APIRouter, HTTPException, Request, Depends, status
from db.database import get_db
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.onboarding import (
    NewRoleValue, JobSearchStatus, RoleofInterest, Industry, Skills,
    CareerGoals, MentoringFrequency, MentoringFormat
)
from api.api_models.onboarding import (
    OnboardingBase, NewRoleValueResponse, RoleofInterestResponse,
    MentoringFrequencyResponse, MentoringFormatResponse,
    CompleteOnboardingRequest, UserOnboardingDataResponse,
    ProfessionalBackgroundResponse, GoalsResponse, MentoringPreferencesResponse
)
from db.models.user import User
from utils.oauth2 import get_current_user


onboarding_router = APIRouter(tags=["Onabording Questions"], prefix="/onbarding")


@onboarding_router.get("/new-role-values")
async def list_role_values(db: AsyncSession = Depends(get_db)) -> List[NewRoleValueResponse]:
    all_role_values = select(NewRoleValue)
    all_roles_result = db.execute(all_role_values)
    return all_roles_result.scalars().all()


@onboarding_router.get("/job-search-status")
async def list_job_search_status(db: AsyncSession = Depends(get_db)) -> List[OnboardingBase]:
    all_job_steach_status = select(JobSearchStatus)
    all_job_steach_statuses = db.execute(all_job_steach_status)
    return all_job_steach_statuses.scalars().all()


@onboarding_router.get("/role-interest")
async def list_role_of_interest(db: AsyncSession = Depends(get_db)) -> List[RoleofInterestResponse]:
    all_role_interest = select(RoleofInterest)
    all_role_interest_result = db.execute(all_role_interest)
    return all_role_interest_result.scalars().all()


@onboarding_router.get("/industry")
async def list_industries(db: AsyncSession = Depends(get_db)) -> List[OnboardingBase]:
    all_industries = select(Industry)
    all_industries_result = db.execute(all_industries)
    return all_industries_result.scalars().all()


@onboarding_router.get("/skills")
async def list_skills(db: AsyncSession = Depends(get_db)) -> List[OnboardingBase]:
    all_skills = select(Skills)
    all_skills_result = db.execute(all_skills)
    return all_skills_result.scalars().all()


@onboarding_router.get("/career-goals")
async def list_career_goals(db: AsyncSession = Depends(get_db)) -> List[OnboardingBase]:
    all_career_goals = select(CareerGoals)
    all_career_goals_result = db.execute(all_career_goals)
    return all_career_goals_result.scalars().all()


@onboarding_router.get("/mentoring-frequency")
async def list_mentoring_frequency(db: AsyncSession = Depends(get_db)) -> List[MentoringFrequencyResponse]:
    all_frequencies = select(MentoringFrequency)
    all_frequencies_result = db.execute(all_frequencies)
    return all_frequencies_result.scalars().all()


@onboarding_router.get("/mentoring-format")
async def list_mentoring_format(db: AsyncSession = Depends(get_db)) -> List[MentoringFormatResponse]:
    all_formats = select(MentoringFormat)
    all_formats_result = db.execute(all_formats)
    return all_formats_result.scalars().all()


@onboarding_router.post("/complete")
async def complete_onboarding(
    onboarding_data: CompleteOnboardingRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> dict:
    """
    Complete user onboarding - called when user agrees to code of conduct.
    Validates and saves all onboarding data based on user type.
    """
    # Validate code of conduct acceptance
    if not onboarding_data.code_of_conduct_accepted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You must accept the code of conduct to complete onboarding"
        )

    # Validate required sections based on user type
    if current_user.user_type == "mentee":
        if not onboarding_data.goals:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mentees must complete the Goals section"
            )
        if not onboarding_data.mentoring_preferences:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mentees must complete the Mentoring Preferences section"
            )
    elif current_user.user_type == "mentor":
        if not onboarding_data.mentoring_preferences:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mentors must complete the Mentoring Preferences section"
            )

    # Update professional background
    prof_bg = onboarding_data.professional_background
    current_user.current_role = prof_bg.current_role
    current_user.company = prof_bg.company
    current_user.years_of_experience = prof_bg.years_of_experience

    # Clear and update industry associations
    current_user.industry = []
    if prof_bg.industry_ids:
        industries = await db.execute(
            select(Industry).where(Industry.id.in_(prof_bg.industry_ids))
        )
        current_user.industry = list(industries.scalars().all())

    # Clear and update skills associations
    current_user.skills = []
    if prof_bg.skill_ids:
        skills = await db.execute(
            select(Skills).where(Skills.id.in_(prof_bg.skill_ids))
        )
        current_user.skills = list(skills.scalars().all())

    # Update goals (for mentees)
    if onboarding_data.goals:
        current_user.long_term_goals = onboarding_data.goals.long_term_goals

        # Clear and update career goals associations
        current_user.career_goals = []
        if onboarding_data.goals.career_goal_ids:
            career_goals = await db.execute(
                select(CareerGoals).where(CareerGoals.id.in_(onboarding_data.goals.career_goal_ids))
            )
            current_user.career_goals = list(career_goals.scalars().all())

    # Update mentoring preferences (for mentors and mentees)
    if onboarding_data.mentoring_preferences:
        prefs = onboarding_data.mentoring_preferences

        # Clear and update mentoring frequency
        current_user.mentoring_frequency = []
        if prefs.mentoring_frequency_ids:
            frequencies = await db.execute(
                select(MentoringFrequency).where(MentoringFrequency.id.in_(prefs.mentoring_frequency_ids))
            )
            current_user.mentoring_frequency = list(frequencies.scalars().all())

        # Clear and update mentoring format
        current_user.mentoring_format = []
        if prefs.mentoring_format_ids:
            formats = await db.execute(
                select(MentoringFormat).where(MentoringFormat.id.in_(prefs.mentoring_format_ids))
            )
            current_user.mentoring_format = list(formats.scalars().all())

    # Mark onboarding as complete
    current_user.code_of_conduct_accepted = True
    current_user.onboarding_completed = True

    # Save to database
    await db.commit()
    await db.refresh(current_user)

    return {
        "message": "Onboarding completed successfully",
        "user_id": current_user.id,
        "user_type": current_user.user_type,
        "onboarding_completed": True
    }


@onboarding_router.get("/my-data", response_model=UserOnboardingDataResponse)
async def get_my_onboarding_data(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> UserOnboardingDataResponse:
    """
    Get current user's onboarding data structured by section.
    Returns:
    - is_onboarded: boolean indicating if onboarding is complete
    - user_type: the user's type (regular, mentor, mentee)
    - professional_background: professional background data
    - goals: goals data (for mentees)
    - mentoring_preferences: mentoring preferences (for mentors and mentees)
    """
    # Refresh user to ensure we have all relationships loaded
    await db.refresh(current_user, [
        'industry', 'skills', 'career_goals',
        'mentoring_frequency', 'mentoring_format'
    ])

    # Build professional background
    professional_background = ProfessionalBackgroundResponse(
        current_role=current_user.current_role,
        company=current_user.company,
        years_of_experience=current_user.years_of_experience,
        industries=current_user.industry,
        skills=current_user.skills
    )

    # Build goals (for mentees)
    goals = None
    if current_user.user_type == "mentee":
        goals = GoalsResponse(
            career_goals=current_user.career_goals,
            long_term_goals=current_user.long_term_goals
        )

    # Build mentoring preferences (for mentors and mentees)
    mentoring_preferences = None
    if current_user.user_type in ["mentor", "mentee"]:
        mentoring_preferences = MentoringPreferencesResponse(
            mentoring_frequency=current_user.mentoring_frequency,
            mentoring_format=current_user.mentoring_format
        )

    return UserOnboardingDataResponse(
        is_onboarded=current_user.onboarding_completed,
        user_type=current_user.user_type.value if hasattr(current_user.user_type, 'value') else current_user.user_type,
        professional_background=professional_background,
        goals=goals,
        mentoring_preferences=mentoring_preferences
    )

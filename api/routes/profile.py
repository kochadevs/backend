"""
Profile and Annual Target APIs
"""
from typing import List
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_db
from db.models.user import User
from db.models.annual_target import AnnualTarget
from api.api_models.annual_target import (
    AnnualTargetCreate, AnnualTargetUpdate, AnnualTargetResponse,
    ProfileCompletionResponse
)
from utils.oauth2 import get_current_user
from services.profile_completion import ProfileCompletionService


profile_router = APIRouter(tags=["Profile"], prefix="/profile")


@profile_router.get("/completion", response_model=ProfileCompletionResponse)
async def get_profile_completion(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> ProfileCompletionResponse:
    """
    Get profile completion percentage for the current user.
    Includes:
    - Profile completion % (based on user type)
    - Annual target completion %
    - Overall completion % (average of both)
    """
    # Refresh user to load all relationships
    db.refresh(current_user, [
        'industry', 'skills', 'career_goals',
        'mentoring_frequency', 'mentoring_format', 'annual_targets'
    ])

    # Calculate profile completion
    profile_details = ProfileCompletionService.calculate_profile_completion(current_user)

    # Calculate annual target completion
    annual_targets_summary = ProfileCompletionService.calculate_annual_target_completion(
        current_user.annual_targets
    )

    # Calculate overall completion
    overall_percentage = ProfileCompletionService.calculate_overall_completion(
        profile_details["percentage"],
        annual_targets_summary["percentage"]
    )

    user_type = current_user.user_type.value if hasattr(current_user.user_type, 'value') else current_user.user_type

    return ProfileCompletionResponse(
        user_type=user_type,
        profile_completion_percentage=profile_details["percentage"],
        annual_target_completion_percentage=annual_targets_summary["percentage"],
        overall_completion_percentage=overall_percentage,
        profile_details=profile_details,
        annual_targets_summary=annual_targets_summary
    )


# Annual Target Endpoints
@profile_router.post("/annual-targets", response_model=AnnualTargetResponse, status_code=status.HTTP_201_CREATED)
async def create_annual_target(
    target: AnnualTargetCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> AnnualTarget:
    """Create a new annual target for the current user"""
    new_target = AnnualTarget(
        user_id=current_user.id,
        objective=target.objective,
        measured_by=target.measured_by,
        completed_by=target.completed_by,
        upload_path=target.upload_path
    )

    db.add(new_target)
    db.commit()
    db.refresh(new_target)

    return new_target


@profile_router.get("/annual-targets", response_model=List[AnnualTargetResponse])
async def get_my_annual_targets(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[AnnualTarget]:
    """Get all annual targets for the current user"""
    db.refresh(current_user, ['annual_targets'])
    return current_user.annual_targets


@profile_router.get("/annual-targets/{target_id}", response_model=AnnualTargetResponse)
async def get_annual_target(
    target_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> AnnualTarget:
    """Get a specific annual target by ID"""
    from sqlalchemy import select

    result = db.execute(
        select(AnnualTarget).where(
            AnnualTarget.id == target_id,
            AnnualTarget.user_id == current_user.id
        )
    )
    target = result.scalar_one_or_none()

    if not target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Annual target not found"
        )

    return target


@profile_router.patch("/annual-targets/{target_id}", response_model=AnnualTargetResponse)
async def update_annual_target(
    target_id: int,
    target_update: AnnualTargetUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> AnnualTarget:
    """Update an annual target"""
    from sqlalchemy import select

    result = db.execute(
        select(AnnualTarget).where(
            AnnualTarget.id == target_id,
            AnnualTarget.user_id == current_user.id
        )
    )
    target = result.scalar_one_or_none()

    if not target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Annual target not found"
        )

    # Update fields
    update_data = target_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(target, field, value)

    db.commit()
    db.refresh(target)

    return target


@profile_router.delete("/annual-targets/{target_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_annual_target(
    target_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete an annual target"""
    from sqlalchemy import select

    result = db.execute(
        select(AnnualTarget).where(
            AnnualTarget.id == target_id,
            AnnualTarget.user_id == current_user.id
        )
    )
    target = result.scalar_one_or_none()

    if not target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Annual target not found"
        )

    db.delete(target)
    db.commit()

    return None

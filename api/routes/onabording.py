from typing import Any, List
from fastapi import APIRouter, HTTPException, Request, Depends, status
from db.database import get_db
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.onboarding import (
    NewRoleValue, JobSearchStatus, RoleofInterest, Industry, Skills,
    CareerGoals
)
from api.api_models.onboarding import (
    OnboardingBase, NewRoleValueResponse, RoleofInterestResponse
)


onboarding_router = APIRouter(tags=["Onabording Questions"], prefix="/onbarding")


@onboarding_router.get("/new-role-values")
async def list_role_values(db: AsyncSession = Depends(get_db)) -> List[NewRoleValueResponse]:
    all_role_values = select(NewRoleValue)
    all_roles_result = db.execute(all_role_values)
    return all_roles_result.scalars().all()


@onboarding_router.get("/job-search-status")
async def list_job_search_status(db: AsyncSession = Depends(get_db)) -> List[OnboardingBase]:
    all_role_values = select(JobSearchStatus)
    all_roles_result = db.execute(all_role_values)
    return all_roles_result.scalars().all()


@onboarding_router.get("/role-interest")
async def list_role_of_interest(db: AsyncSession = Depends(get_db)) -> List[RoleofInterestResponse]:
    all_role_values = select(RoleofInterest)
    all_roles_result = db.execute(all_role_values)
    return all_roles_result.scalars().all()


@onboarding_router.get("/industry")
async def list_industries(db: AsyncSession = Depends(get_db)) -> List[OnboardingBase]:
    all_role_values = select(Industry)
    all_roles_result = db.execute(all_role_values)
    return all_roles_result.scalars().all()

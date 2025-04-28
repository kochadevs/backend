"""
Get iniital onboarding data in to the db on startapp
"""
from typing import Any
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from db.seed_data import (
    what_you_value_in_new_role, status_of_your_job_search,
    roles_user_is_interested_in, industries_of_interest,
    skills_you_have_or_enjoy_working_with, career_goals
)
from db.models.onboarding import (
    NewRoleValue, JobSearchStatus, RoleofInterest, Industry, Skills,
    CareerGoals
)


async def seed_initial_onboarding_data(db: AsyncSession) -> Any:
    """"""
    # try:
    print("Starting the seeding")
    for item in what_you_value_in_new_role:
        existing = select(NewRoleValue).where(NewRoleValue.name == item)
        role_result = await db.execute(existing)
        existing_value = role_result.scalar_one_or_none()
        if not existing_value and item:
            db.add(NewRoleValue(name=item))
    await db.flush()

    for status_item in status_of_your_job_search:
        existing_status = select(JobSearchStatus).where(
            JobSearchStatus.name == status_item
        )
        status_result = await db.execute(existing_status)
        if not status_result.scalar_one_or_none() and status_item:
            db.add(JobSearchStatus(name=status_item))
    await db.flush()

    for roles_key, roles_value in roles_user_is_interested_in.items():
        for roles_item in roles_value:
            existing_role = select(RoleofInterest).where(
                RoleofInterest.name == roles_item, RoleofInterest.category == roles_key
            )
            existing_role_result = await db.execute(existing_role)
            if not existing_role_result.scalar_one_or_none() and roles_item:
                db.add(RoleofInterest(name=roles_item, category=roles_key))
    await db.flush()

    for industry_item in industries_of_interest:
        existing_industry = select(Industry).where(Industry.name == industry_item)
        industry_result = await db.execute(existing_industry)
        if not industry_result.scalar_one_or_none() and industry_item:
            db.add(Industry(name=industry_item))
    await db.flush()

    for skill_item in skills_you_have_or_enjoy_working_with:
        existing_skill = select(Skills).where(Skills.name == skill_item)
        skill_result = await db.execute(existing_skill)
        if not skill_result.scalar_one_or_none() and skill_item:
            db.add(Skills(name=skill_item))
    await db.flush()

    for goal_item in career_goals:
        existing_goal = select(CareerGoals).where(CareerGoals.name == goal_item)
        goal_result = await db.execute(existing_goal)
        if not goal_result.scalar_one_or_none() and goal_item:
            db.add(CareerGoals(name=goal_item))
    await db.flush()
    await db.commit()
    # except Exception as onboarding_exception:
    #     await db.rollback()
    #     raise Exception(onboarding_exception.__str__())

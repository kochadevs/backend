"""
Routes for managing groups
"""
from typing import List
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status

from api.api_models.user import UserResponse
from db.database import get_db
from db.models.groups import Group
from core.exceptions import exceptions
from db.models.user import User
from utils.oauth2 import get_current_user
from api.api_models.groups import GroupCreate, GroupOut

groups_router = APIRouter(tags=["Groups"], prefix="/groups")


@groups_router.post("/", response_model=GroupOut, status_code=status.HTTP_201_CREATED)
def create_group(
    payload: GroupCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    # Basic uniqueness enforced by DB but check early
    exists = db.query(Group).filter(Group.name == payload.name).first()
    if exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=exceptions.GROUP_ALREADY_EXISTS
        )
    g = Group(
        name=payload.name,
        description=payload.description,
        created_by=user.id,
        is_public=payload.is_public
    )
    db.add(g)
    db.commit()
    db.refresh(g)
    return GroupOut.model_validate(g)


@groups_router.get("/my-groups", response_model=List[GroupOut])
def list_my_groups(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    try:
        groups = db.query(Group).filter(
            Group.members.any(id=user.id) | (Group.created_by == user.id)
        ).all()
        return [GroupOut.model_validate(g) for g in groups if g is not None]
    except (Exception, HTTPException) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@groups_router.get("/", response_model=List[GroupOut])
def list_groups(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    groups = db.query(Group).all()
    return [GroupOut.model_validate(g) for g in groups if g is not None]


@groups_router.get("/{group_id}", response_model=GroupOut)
def get_group(group_id: int, db: Session = Depends(get_db)):
    g = db.get(Group, group_id)
    if not g:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=exceptions.GROUP_NOT_FOUND)
    return GroupOut.model_validate(g)


@groups_router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_group(
    group_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    g = db.get(Group, group_id)
    if not g:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=exceptions.GROUP_NOT_FOUND)
    if g.created_by != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=exceptions.GROUP_FORBIDDEN)
    db.delete(g)
    db.commit()
    return


@groups_router.post("/{group_id}/join", status_code=status.HTTP_200_OK)
def join_group(
    group_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    g = db.get(Group, group_id)
    if not g:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=exceptions.GROUP_NOT_FOUND)
    if user in g.members:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=exceptions.GROUP_ALREADY_MEMBER)
    g.members.append(user)
    db.commit()
    return {"detail": "Joined group"}


@groups_router.post("/{group_id}/leave", status_code=status.HTTP_200_OK)
def leave_group(
    group_id: int,
    db: Session = Depends(get_db),
    user: int = Depends(get_current_user)
):
    g = db.get(Group, group_id)
    if not g:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=exceptions.GROUP_NOT_FOUND)
    if user not in g.members:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Not a member of the group")
    g.members.remove(user)
    db.commit()
    return {"detail": "Left group"}


@groups_router.get("/{group_id}/members", response_model=List[UserResponse])
def list_group_members(
    group_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    g = db.get(Group, group_id)
    if not g:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=exceptions.GROUP_NOT_FOUND)
    group_users = db.query(User).filter(
        User.groups.any(id=group_id) | (User.created_groups.any(id=group_id))
        ).all()
    return group_users

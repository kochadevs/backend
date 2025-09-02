"""
Authentication and Authorization APIs
"""
from typing import Any
# from datetime import datetime, timedelta

from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, File, UploadFile, status, Depends, HTTPException, Response

from sqlalchemy.orm import Session
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from jose import jwt

from api.api_models.user import (
    UserResponse, UserSignup, UserUpdate, AllUserResponse,
    ForgotPasswordRequest, ResetPasswordRequest
)
from db.database import get_db
from db.models.user import User
from core.config import settings
from core.exceptions import exceptions
from services.user import UserService
from api.api_models.login import Token
from utils.oauth2 import (
    get_access_token, get_current_user, get_refresh_token, create_reset_token,
    verify_reset_token, get_password_hash
)
# from utils.permissions import has_permission
from utils.mail_service import send_password_reset_email, send_password_reset_confirmation

auth_router = APIRouter(tags=["Auth"], prefix="/users")


@auth_router.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
async def signup(
    user: UserSignup,
    db: Session = Depends(get_db)
) -> Any:
    try:
        user_service = UserService(db)
        new_user = await user_service.create_user(user, creator=None)
        db.commit()
        db.refresh(new_user)
        return new_user
    except HTTPException as e:
        db.rollback()
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@auth_router.post("/login", response_model=Token, status_code=status.HTTP_200_OK)
def login(user: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)) -> Any:
    """Login with OAuth2 Password Form"""
    user_service = UserService(db)
    user_data = user_service.authenticate_user(user.username.lower(), user.password)
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=exceptions.USER_NOT_FOUND
        )
    token = get_access_token(str(user_data.id))
    refresh_token = get_refresh_token(str(user_data.id))
    profile = user_service.get_user_profile(user_data.id)
    return Token(
        id=user_data.id,
        access_token=token,
        refresh_token=refresh_token,
        token_type="Bearer",
        is_active=user_data.is_active,
        user_profile=profile,
    )


@auth_router.patch("/{user_id}", response_model=UserResponse)
def update(user_id: int, user: UserUpdate, db: Session = Depends(get_db)) -> Any:
    """Update the user"""
    user_service = UserService(db)
    updated_user = user_service.update_user(user_id, user)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=exceptions.USER_NOT_FOUND
        )
    return updated_user


@auth_router.post("/logout")
def logout(response: Response):
    response.set_cookie(key="st.token", value="", httponly=True, max_age=10, samesite="none", secure=True)
    return {"message": "Logout Successful"}


@auth_router.patch("/update-profile-pic/{user_id}", response_model=UserResponse)
async def update_profile_pic(user_id: int, profile_pic: UploadFile = File(...), db: Session = Depends(get_db)) -> Any:
    """Update user's profile picture"""
    user_service = UserService(db)
    updated_user = await user_service.update_profile_pic(user_id, profile_pic)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=exceptions.USER_NOT_FOUND
        )
    return updated_user


@auth_router.get(
    "/all",
    response_model=list[AllUserResponse])
async def list_users(db: AsyncSession = Depends(get_db), admin=Depends(get_current_user)) -> Any:
    """Return all users for the super admin"""
    try:

        stmt = select(User)
        return stmt
    except (Exception, HTTPException) as all_user_exception:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail=str(all_user_exception)
        )


@auth_router.post('/forgot-password')
async def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """
    Send a reset password email to the user.

    Args:
        request (ForgotPasswordRequest): The request containing the user's email.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        JSONResponse: A response indicating the result of sending the reset password email.
    """
    email = request.email.lower()
    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    reset_token = create_reset_token(email)

    result = await send_password_reset_email(
        email, reset_token, user.first_name, email_template=None)
    return result


@auth_router.post('/reset-password')
async def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)) -> dict:
    """
    Reset the user's password with a valid reset token.

    Args:
        request (ResetPasswordRequest): The request containing the reset token and new password.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        dict: A message indicating the result of the password reset.
    """
    try:
        email = verify_reset_token(request.token)
        email = email.lower()
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        hashed_password = get_password_hash(request.new_password)
        user.password = hashed_password
        user.is_active = True

        db.commit()
        db.refresh(user)
        await send_password_reset_confirmation(email, user.first_name)

        return {"message": "Password reset successful"}
    except HTTPException as e:
        raise e
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=exceptions.PASSWORD_RESET_ERROR
        )

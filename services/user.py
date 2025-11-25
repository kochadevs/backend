"""
Service for user creation
"""
import logging
from typing import Optional, List
from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from api.api_models.user import UserSignup, UserUpdate, UserResponse
from db.models.user import User
from db.repository.crud import Crud
from core.exceptions import exceptions
from core.config import settings
from utils.oauth2 import get_password_hash, verify_password


logger = logging.getLogger(__name__)


class UserService:
    def __init__(self, db: Session):
        self.crud = Crud(db)
        self.db = db
        # self.s3_handler = create_s3_uploader()

    async def create_user(self, user_data: UserSignup, creator: User = None) -> User:
        """Create a new user"""
        try:
            # Validate password confirmation
            if user_data.password != user_data.password_confirmation:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=exceptions.PASSWORDS_MISMATCH
                )

            # Check if user exists
            if self.get_user_by_email(user_data.email):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=exceptions.USER_EXISTS
                )
            new_user = user_data.model_dump().copy()
            # Prepare user data
            new_user.pop("password_confirmation", None)
            new_user["password"] = get_password_hash(new_user["password"])
            # Create user
            user = self.crud.create(User, new_user)
            self.db.flush()
            return user

        except HTTPException as e:
            raise e
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    def get_user_profile(self, user_id: int) -> UserResponse:
        """Get user's profile with all related data"""
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=exceptions.USER_NOT_FOUND
                )

            user_dict = {
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "gender": user.gender,
                "nationality": user.nationality,
                "location": user.location,
                "phone": user.phone,
                "is_active": user.is_active,
                "email_verified": user.email_verified,
                "profile_pic": user.profile_pic,
                "cover_photo": user.cover_photo,
                "about": user.about,
                "current_role": user.current_role,
                "user_type": user.user_type,
                "social_links": user.social_links,
                "availability": user.availability,
                "new_role_values": user.new_role_values,
                "job_search_status": user.job_search_status,
                "role_of_interest": user.role_of_interest,
                "industry": user.industry,
                "skills": user.skills,
                "career_goals": user.career_goals,
            }
            return UserResponse.model_validate(user_dict, from_attributes=True)

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return self.crud.get(User, user_id)

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.crud.get_by(User, email=email)

    async def _read_upload_file(self, upload_file: UploadFile) -> bytes:
        """Safely read contents of an UploadFile"""
        try:
            contents = await upload_file.read()
            await upload_file.seek(0)  # Reset file pointer
            return contents
        except Exception as e:
            logger.error(f"Error reading upload file: {str(e)}")
            raise ValueError(f"Failed to read upload file: {str(e)}")

    async def update_profile_pic(self, user_id: int, profile_pic_data: UploadFile) -> None:
        try:
            user = self.crud.get(User, user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=exceptions.USER_NOT_FOUND
                )

            self.db.commit()
            return user
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

    def delete_user(self, user_id: int) -> bool:
        """Delete a user"""
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )

            user.deleted = True
            self.db.commit()
            return True

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user credentials"""
        user = self.get_user_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=exceptions.USER_NOT_FOUND
            )
        if not verify_password(password, user.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=exceptions.INVALID_PASSWORD
            )
        return user

    def search_users(self, query: str, skip: int = 0, limit: int = 10) -> List[User]:
        """Search users by name or email"""
        return self.db.query(User).filter(
            or_(
                User.email.ilike(f"%{query}%"),
                User.first_name.ilike(f"%{query}%"),
                User.last_name.ilike(f"%{query}%")
            )
        ).offset(skip).limit(limit).all()

    def change_password(self, user_id: int, old_password: str, new_password: str) -> bool:
        """Change user password"""
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )

            if not verify_password(old_password, user.password):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid password"
                )

            hashed_password = get_password_hash(new_password)
            self.crud.update(user, {"password": hashed_password})
            return True

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

    def update_user(self, user_id: int, user_data: UserUpdate) -> User:
        """Update a user"""
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=exceptions.USER_NOT_FOUND
                )
            if isinstance(user_data, dict):
                update_data = user_data
            else:
                update_data = user_data.model_dump(exclude_unset=True)
            updated_user = self.crud.update(user, update_data)
            self.db.commit()
            return updated_user

        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

    def get_all_users(self, skip: int = 0, limit: int = 10) -> List[User]:
        """Get all users with pagination"""
        return self.db.query(User).offset(skip).limit(limit).all()

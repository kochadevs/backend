"""
OAuth 2 Authentication
"""
import re
import bcrypt
from typing import Optional
from contextvars import ContextVar
from jose import jwt, JWTError
from datetime import datetime, timedelta
from api.api_models.user import TokenData
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from core.config import settings
from core.exceptions import exceptions
from sqlalchemy.orm import Session

from db import database
from db.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/v1/users/login')


credential_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    now = datetime.now()
    expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({
        "exp": expire,
        "iat": now
    })
    encoded_jwt = jwt.encode(to_encode, settings.SECRET, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, settings.REFRESH_SECRET, algorithm=settings.ALGORITHM)
    return token


def get_access_token(sub: str) -> str:
    token = create_access_token({"sub": sub})
    return token


def get_refresh_token(sub: str) -> str:
    token = create_refresh_token({"sub": sub})
    return token


def verify_token(token: str, credential_exception):
    try:
        payload = jwt.decode(token, settings.SECRET, algorithms=settings.ALGORITHM)
        sub = payload.get('sub')
        if sub is None:
            raise credential_exception
        token_data = TokenData(id=sub)
    except JWTError:
        raise credential_exception

    return token_data


def verify_refresh_token(token: str):
    payload = jwt.decode(token, settings.REFRESH_SECRET, algorithms=settings.ALGORITHM)
    sub = payload.get('sub')
    if sub is None:
        return False
    return TokenData(id=sub)


# Get currently logged in User
def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(database.get_db)):

    payload = jwt.decode(token, settings.SECRET, algorithms=settings.ALGORITHM)
    token = verify_token(token, credential_exception)
    user = db.query(User).filter(User.id == token.id).first()
    if not user:
        raise credential_exception
    if not user.is_active:
        return False
    # Check if token was issued before role was modified
    token_iat = datetime.fromtimestamp(payload.get("iat")).astimezone()
    if user and datetime.now() > token_iat:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def create_reset_token(email: str) -> str:
    delta = timedelta(minutes=15)
    now = datetime.now()
    payload = {
        "sub": email,
        "iat": now,
        "exp": now + delta
    }
    return jwt.encode(payload, settings.SECRET, algorithm=settings.ALGORITHM)


def verify_reset_token(token: str) -> str:
    try:
        payload = jwt.decode(token, settings.SECRET, algorithms=settings.ALGORITHM)
        email = payload.get("sub")
        if not email or not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=exceptions.INVALID_TOKEN)
        expiration = payload.get("exp")
        if expiration:
            expiration_datetime = datetime.fromtimestamp(expiration)
            if datetime.now() > expiration_datetime:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=exceptions.TOKEN_EXPIRED)
        return email
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=exceptions.INVALID_TOKEN)


def hash_password(password: str) -> str:
    """ Hash a password using bcrypt"""
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password=pwd_bytes, salt=salt)
    return hashed_password.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str | bytes) -> bool:
    """Check if the provided password matches the stored password (hashed)"""
    password_byte_enc = plain_password.encode('utf-8')
    if isinstance(hashed_password, str):
        hashed_password: bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_byte_enc, hashed_password)


def get_password_hash(password: str) -> str:
    return hash_password(password)


current_user_id: ContextVar[Optional[int]] = ContextVar("current_user_id", default=None)
branch_context: ContextVar[int] = ContextVar("branch_id", default=None)


def set_current_user_id(user_id: int):
    current_user_id.set(user_id)


def get_current_user_id() -> Optional[int]:
    return current_user_id.get()

"""
All auth utilities go here
"""
import httpx
from fastapi import Request, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from supabase import Client, create_client
from core.config import settings
from jose import JWTError, jwt


SUPABASE_URL = settings.SUPABASE_URL
SUPABASE_KEY = settings.SUPABASE_KEY
SUPABASE_JWT_SECRET = settings.SUPABASE_JWT_SECRET


oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{SUPABASE_URL}/auth/v1/token")


credential_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_supabase_client() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)


def get_user_supabase_client(token: str) -> Client:
    client = create_client(SUPABASE_URL, SUPABASE_KEY)
    client.auth.session = {
        "access_token": token,
        "token_type": "Bearer"
    }
    return client


def get_current_user(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing token")

    token = auth_header.split(" ")[1]
    try:
        payload = jwt.decode(token, SUPABASE_JWT_SECRET, algorithms=["HS256"])
        return payload
    except JWTError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token")


async def signup_email(email: str, password: str):
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{SUPABASE_URL}/auth/v1/signup",
            headers={"apikey": SUPABASE_KEY, "Content-Type": "application/json"},
            json={"email": email, "password": password}
        )
        if resp.status_code != status.HTTP_200_OK:
            raise HTTPException(status_code=resp.status_code, detail=resp.json())
        return resp.json()


async def login_email(email: str, password: str):
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{SUPABASE_URL}/auth/v1/token",
            headers={"apikey": SUPABASE_KEY, "Content-Type": "application/json"},
            json={"email": email, "password": password, "grant_type": "password"}
        )
        if resp.status_code != status.HTTP_200_OK:
            raise HTTPException(status_code=resp.status_code, detail=resp.json())
        return resp.json()


def get_social_login_url(provider: str, redirect_url: str) -> str:
    return (
        f"{SUPABASE_URL}/auth/v1/authorize"
        f"?provider={provider}&redirect_to={redirect_url}"
    )

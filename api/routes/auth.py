"""
Authentication and Authorization APIs
"""
from core.config import settings
from fastapi import APIRouter, HTTPException, Request, Depends, status
from utils.auth import get_user_supabase_client
from utils.auth import get_current_user, get_social_login_url, signup_email, login_email

from api.api_models.user import AuthForm

auth_router = APIRouter(tags=["Auth"], prefix="/users")


SUPABASE_JWT_SECRET = settings.SUPABASE_JWT_SECRET


@auth_router.get("/me", status_code=status.HTTP_200_OK)
async def get_user_profile(request: Request):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    supabase = get_user_supabase_client(token)
    user_data = supabase.auth.get_user(token)
    return user_data


@auth_router.post("/auth/signup")
async def signup(form: AuthForm):
    return await signup_email(form.email, form.password)


@auth_router.post("/auth/login")
async def login(form: AuthForm):
    return await login_email(form.email, form.password)


@auth_router.get("/auth/social/{provider}")
def social_auth(provider: str, redirect_url: str):
    """
    Frontend should redirect to the returned URL.
    Provider options: google, github, facebook, etc.
    """
    return {"url": get_social_login_url(provider, redirect_url)}


@auth_router.get("/auth/callback")
async def auth_callback(request: Request):
    params = dict(request.query_params)

    access_token = params.get("access_token")
    refresh_token = params.get("refresh_token", None)
    expires_in = params.get("expires_in", None)
    token_type = params.get("token_type", None)
    provider_token = params.get("provider_token", None)

    creds_dict = {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expries_in": expires_in,
        "token_type": token_type,
        "provider_token": provider_token
    }

    if access_token:
        return creds_dict

    return HTTPException(status_code=400, content={"error": "Missing token"})

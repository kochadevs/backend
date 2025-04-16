"""
Authentication and Authorization APIs
"""
from core.config import settings
from fastapi import APIRouter, Request, Depends, HTTPException
from utils.auth import get_user_supabase_client
from utils.auth import get_current_user, get_social_login_url

auth_router = APIRouter(tags=["Auth"], prefix="/users")


SUPABASE_JWT_SECRET = settings.SUPABASE_JWT_SECRET


@auth_router.get("/me")
async def get_user_profile(request: Request, user=Depends(get_current_user)):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    supabase = get_user_supabase_client(token)
    user_data = supabase.auth.get_user()
    return {"supabase_user": user_data}


@auth_router.get("/auth/social/{provider}")
def social_auth(provider: str, redirect_url: str):
    """
    Frontend should redirect to the returned URL.
    Provider options: google, github, facebook, etc.
    """
    return {"url": get_social_login_url(provider, redirect_url)}

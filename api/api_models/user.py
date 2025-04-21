"""
API models for the user APIs
"""
from pydantic import BaseModel


class AuthForm(BaseModel):
    email: str
    password: str

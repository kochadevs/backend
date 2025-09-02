"""
Define the HTTP Exceptions to be raised
"""
from typing import Any
from fastapi import HTTPException, status


class CustomException:
    USER_EXISTS: str = "User with the email already exists"
    PASSWORDS_MISMATCH: str = "Passwords do not match"
    USER_NOT_FOUND: str = "User with specified email does not exist"
    INVALID_PASSWORD: str = "Invalid password specified for the user"
    UNAUTHORIZED_USER: str = "User is not authorized on the requested resource"
    INVALID_EMAIL: str = "Invalid email"
    INADEQUATE_PERMISSIONS: str = "You do not have permission to perform this action"
    PASSWORD_RESET_ERROR: str = "An error occurred while resetting the password."


exceptions = CustomException()

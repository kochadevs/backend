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
    INVALID_TOKEN: str = "Invalid token"
    TOKEN_EXPIRED: str = "Token has expired"
    REACTION_NOT_FOUND: str = "Reaction not found"
    COMMENT_NOT_FOUND: str = "Comment not found"
    POST_NOT_FOUND: str = "Post not found"
    INVALID_PARENT_COMMENT: str = "Invalid parent comment"
    NOT_ALLOWED: str = "You are not allowed to perform this action"
    GROUP_ALREADY_EXISTS: str = "Group with that name already exists"
    GROUP_NOT_FOUND: str = "Group not found"
    GROUP_FORBIDDEN: str = "Not authorized to delete this group"
    GROUP_ALREADY_MEMBER: str = "Already a member of the group"
    MENTOR_PACKAGE_NOT_FOUND: str = "Mentor package not found"
    MENTOR_PACKAGE_FORBIDDEN: str = "Only mentors can delete packages."
    MENTOR_BOOKING_FORBIDDEN: str = "Requested booking is not for this user (mentor)."
    MENTEE_BOOKING_FORBIDDEN: str = "Requested booking is not for this user (mentee)."
    MENTOR_BOOKING_NOT_FOUND: str = "Mentor booking not found"
    MENTEES_RESTRICTION_TO_PACKAGES: str = "Only mentees can book mentor packages."


exceptions = CustomException()

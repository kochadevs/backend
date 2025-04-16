"""
All exceptions should be stated here and only variables used to raise
"""


class CustomException:
    USER_EXISTS: str = "User with the email already exists"
    PASSWORDS_MISMATCH: str = "Passwords do not match"
    USER_NOT_FOUND: str = "User with specified email does not exist"
    INVALID_PASSWORD: str = "Invalid password specified for the user"
    UNAUTHORIZED_USER: str = "User is not authorized on the requested resource"


exceptions = CustomException()

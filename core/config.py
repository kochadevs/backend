"""
Configuration settings for the application
"""
import os
from dotenv import load_dotenv
from sqlalchemy import URL


load_dotenv()


class Settings:
    PROJECT_NAME: str = "Kocha Mentors CIC App"
    PROJECT_VERSION: str = "0.1.0"
    # Database Settings
    POSTGRES_USER: str = os.environ.get("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.environ.get("POSTGRES_PASSWORD", "postgres")
    POSTGRES_SERVER: str = os.environ.get("POSTGRES_SERVER", "postgres")
    POSTGRES_PORT: str | int = os.environ.get("POSTGRES_PORT", 5432)
    POSTGRES_DB: str = os.environ.get("POSTGRES_DB", "postgres")
    POSTGRES_TEST_DB: str = os.environ.get("POSTGRES_TEST_DB", "testkochadevappdb")
    DATABASE_URL: str | URL = os.environ.get(
        "POSTGRES_URL",
        f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"
    )
    # Redis connection
    REDIS_URL: str = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    # App specific
    SECRET: str = os.environ.get("SECRET", "ASq0nueapAebeopyxeU9QV3BCJw89LhJo")
    REFRESH_SECRET: str = os.environ.get("REFRESH_SECRET", "jYZVNaheqameBLHvTqbjYZVNrAZr3prHer5g6RJk")
    PRODUCTION_ENV: bool = False
    REFRESH_TOKEN_EXPIRE_MINUTES: str | int = os.environ.get(
        "REFRESH_TOKEN_EXPIRE_MINUTES", 60 * 30 * 24
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: str | int = os.environ.get(
        "ACCESS_TOKEN_EXPIRE_MINUTES", 60 * 30 * 24
    )
    ALGORITHM: str = os.environ.get("ALGORITHM", "HS256")
    BASE_URL: str = os.environ.get("BASE_URL", "http://localhost:3000")
    # Email settings
    EMAIL_SERVER: str = os.environ.get("EMAIL_SERVER", "smtp.gmail.com")
    EMAIL_PORT: str | int = os.environ.get("EMAIL_PORT", 587)
    EMAIL_SENDER: str = os.environ.get("EMAIL_SENDER")
    EMAIL_PASSWORD: str = os.environ.get("EMAIL_PASSWORD")
    URL_PATH: str = "/auth/reset_password"
    AWS_BUCKET_NAME: str | None = os.environ.get("AWS_BUCKET_NAME", None)
    AWS_REGION: str = os.environ.get("AWS_REGION", "eu-west-1")
    AWS_ACCESS_KEY: str | None = os.environ.get("AWS_ACCESS_KEY", None)
    AWS_SECRET_KEY: str | None = os.environ.get("AWS_SECRET_KEY", None)


settings = Settings()

"""
All configs and environmental variables should be loaded here before using
"""
import os
from dotenv import load_dotenv


load_dotenv()


class Settings:
    PROJECT_NAME: str = "Kocha AI App"
    PROJECT_VERSION: str = "0.1.0"
    PRODUCTION_ENV: bool = os.environ.get("PRODUCTION_ENV", False)

    SECRET: str = os.environ.get("SECRET", "QptkP62376v1TWYpILSOvpe06mo33doOJvF6pX3C")
    REFRESH_SECRET: str = os.environ.get("REFRESH_SECRET", "8XePaMVLwaF13arb1jZbmMrMp1jJnnvhQvv8ZoRI")

    SUPABASE_URL: str = os.environ.get("SUPABASE_URL")
    SUPABASE_KEY: str = os.environ.get("SUPABASE_KEY")
    SUPABASE_JWT_SECRET: str = os.environ.get("SUPABASE_JWT")
    SUPABASE_DB_URL: str = os.environ.get("DATABSE_URL")


settings = Settings()

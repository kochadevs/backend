from typing import Any
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from core.config import settings
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine


SQLALCHEMY_DB_URL = settings.SUPABASE_DB_URL


# engine = create_async_engine(DATABASE_URL, echo=False)
# SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# async def get_db():
#     async with SessionLocal() as session:
#         yield session


def set_up_db(production_env) -> tuple[Any, Any, Any]:
    """Setting up the env specific db"""
    if production_env:
        engine: Engine = create_async_engine(SQLALCHEMY_DB_URL)
    else:
        engine = create_async_engine(SQLALCHEMY_DB_URL)
    SessionLocal: Any = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    Base = declarative_base()
    return engine, SessionLocal, Base


engine, SessionLocal, Base = set_up_db(settings.PRODUCTION_ENV)


async def get_db() -> Any:
    async with SessionLocal() as db:
        yield db

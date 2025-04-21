from typing import Any
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from core.config import settings


SQLALCHEMY_DB_URL = settings.SUPABASE_DB_URL


engine: AsyncEngine = create_async_engine(
    SQLALCHEMY_DB_URL, echo=False, connect_args={"statement_cache_size": 0}
)
SessionLocal: Any = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()


async def get_db() -> Any:
    async with SessionLocal() as db:
        yield db

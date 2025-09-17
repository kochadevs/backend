"""
Entry point into the backend application
"""
from typing import Any
from fastapi import FastAPI
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

from db.database import get_db
from db.repository.seed import seed_initial_onboarding_data

from api.routes.auth import auth_router
from api.routes.onabording import onboarding_router
from api.routes.feed import feed_router
from api.routes.groups import groups_router
from api.routes.mentor import mentor_router


async def lifespan(db: Session) -> Any:
    await seed_initial_onboarding_data(db)
    db.commit()


@asynccontextmanager
async def startup_event(app: FastAPI):
    with next(get_db()) as db:
        await lifespan(db)
    yield


app = FastAPI(
    title="Kocha Mentors CIC API Spec",
    lifespan=startup_event,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def index() -> dict:
    return {"msg": "home"}


@app.get("/inactive")
def redirect() -> dict:
    return {"msg": "Account is Inactive. Kindly contact Administrator"}  # noqa: E501


v1_prefix = "/api/v1"
app.include_router(auth_router, prefix=v1_prefix)
app.include_router(onboarding_router, prefix=v1_prefix)
app.include_router(feed_router, prefix=v1_prefix)
app.include_router(groups_router, prefix=v1_prefix)
app.include_router(mentor_router, prefix=v1_prefix)

"""
Entry into the backend of the application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager

from db.database import get_db
from api.routes.auth import auth_router
from api.routes.onboarding import onboarding_router
from db.repository.seed import seed_initial_onboarding_data


# async def lifespan(db: Session) -> None:
#     await seed_initial_onboarding_data(db)


# @asynccontextmanager
# async def startup_event(app: FastAPI):
#     db_gen = get_db()
#     db = await anext(db_gen)

#     try:
#         await lifespan(db)
#         yield
#     finally:
#         await db_gen.aclose()


app = FastAPI()

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


v1_prefix = "/api/v1"

app.include_router(auth_router, prefix=v1_prefix)
app.include_router(onboarding_router, prefix=v1_prefix)

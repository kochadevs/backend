"""
Test configuration
"""
import uuid
from typing import Any
from datetime import date, datetime, timedelta
from fastapi.testclient import TestClient
# import pytest_asyncio
from sqlalchemy import TIMESTAMP, create_engine, text, Column, Integer, String, Boolean
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import ProgrammingError
import pytest
from unittest.mock import AsyncMock

from api.api_models.user import UserSignup
from core.config import settings
from db.database import Base, get_db
from db.models.user import User
from app import app
from db.repository.crud import Crud
from utils.mail_service import welcome_new_user

from db.repository.seed import seed_initial_onboarding_data

pg_user = settings.POSTGRES_USER
pg_pass = settings.POSTGRES_PASSWORD
pg_host = settings.POSTGRES_SERVER
pg_port = settings.POSTGRES_PORT
pg_test_db = settings.POSTGRES_TEST_DB
pg_db = settings.POSTGRES_DB


class TestModel(Base):
    __tablename__ = "test_model"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    date_created = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    deleted = Column(Boolean, default=False)


TEST_SQLALCHEMY_DATABASE_URL = f"postgresql://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_test_db}"
ADMIN_DATABASE_URL = f"postgresql://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}"

engine = create_engine(TEST_SQLALCHEMY_DATABASE_URL)

TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine)


def create_test_database() -> Any:
    """Creates the test database if it doesn't exist."""
    admin_engine = create_engine(ADMIN_DATABASE_URL)
    with admin_engine.connect() as conn:
        conn.execution_options(isolation_level="AUTOCOMMIT")
        try:
            conn.execute(text(f"CREATE DATABASE {pg_test_db}"))
        except ProgrammingError as e:
            if "already exists" not in str(e):
                raise  # Only ignore errors about an existing database


def drop_test_database() -> Any:
    """Drops the test database after tests are complete."""
    admin_engine = create_engine(ADMIN_DATABASE_URL)
    with admin_engine.connect() as conn:
        conn.execution_options(isolation_level="AUTOCOMMIT")
        conn.execute(text(f"DROP DATABASE IF EXISTS {pg_test_db}"))


@pytest.fixture(scope="session", autouse=True)
def setup_database() -> Any:
    # Create the test database and tables before tests
    create_test_database()
    Base.metadata.create_all(bind=engine)

    yield  # Run tests

    # Teardown: Drop all tables and close connections
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    drop_test_database()


@pytest.fixture()
def session() -> Any:
    db = TestingSessionLocal()
    try:
        db.commit()
        yield db
    finally:
        db.close()
        # Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def crud(session: Session) -> Any:
    return Crud(session)


@pytest.fixture()
def client(session: Session) -> Any:
    def override_get_db() -> Any:
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)


@pytest.fixture(autouse=True)
def create_roles(session: Session) -> None:
    db: Session = session

    seed_initial_onboarding_data(db)
    db.commit()


@pytest.fixture
def test_user(session: Session) -> User:
    """Create test user directly in DB"""
    from db.models.user import User
    from utils.oauth2 import get_password_hash
    unique_email = f"test_user_{uuid.uuid4().hex[:8]}@example.com"
    user = User(
        first_name="Test",
        last_name="User",
        email=unique_email,
        gender="Male",
        date_of_birth="2020-01-01",
        nationality="Ghanaian",
        primary_phone="1234567890",
        password=get_password_hash("test123")
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture
def mock_send_email(mocker) -> Any:
    return mocker.patch(
        'utils.mail_service.send_email',
        return_value={"message": "Email has been sent"}
    )

"""
Test configuration and fixtures
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app.models.user import User
from app.models.aircraft import Aircraft
from app.models.flight import Flight
from app.services.auth_service import get_password_hash


# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database for each test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    """Test client"""
    return TestClient(app)


@pytest.fixture
def sample_user(db_session):
    """Create a sample user for testing"""
    user = User(
        email="test@example.com",
        username="testuser",
        full_name="Test User",
        password_hash=get_password_hash("testpassword"),
        is_active=True,
        is_verified=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def sample_aircraft(db_session):
    """Create a sample aircraft for testing"""
    aircraft = Aircraft(
        name="Test Aircraft",
        model="Airbus A320",
        total_seats=180
    )
    db_session.add(aircraft)
    db_session.commit()
    db_session.refresh(aircraft)
    return aircraft


@pytest.fixture
def auth_headers(sample_user):
    """Get authentication headers for testing"""
    from app.services.auth_service import create_access_token
    
    token = create_access_token(data={"sub": sample_user.email})
    return {"Authorization": f"Bearer {token}"}
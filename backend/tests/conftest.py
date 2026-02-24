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
from app.models.seat import Seat
from app.models.booking import Booking
from app.services.auth_service import get_password_hash, create_access_token

# Test database URL (in-memory SQLite)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database dependency override"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def test_user(db_session):
    """Create a test user"""
    user = User(
        email="test@example.com",
        username="testuser",
        full_name="Test User",
        phone="+1234567890",
        password_hash=get_password_hash("testpassword"),
        is_active=True,
        is_verified=True,
        preferred_seat_class="ECONOMY",
        preferred_seat_position="WINDOW"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def auth_headers(test_user):
    """Create authentication headers for test user"""
    token = create_access_token(data={"sub": test_user.id, "email": test_user.email})
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def test_aircraft(db_session):
    """Create a test aircraft"""
    aircraft = Aircraft(
        model="Test Aircraft A320",
        total_seats=180
    )
    db_session.add(aircraft)
    db_session.commit()
    db_session.refresh(aircraft)
    return aircraft

@pytest.fixture
def test_flight(db_session, test_aircraft):
    """Create a test flight"""
    from datetime import datetime, timedelta
    
    flight = Flight(
        from_city="Test City A",
        to_city="Test City B",
        departure_time=datetime.utcnow() + timedelta(days=1),
        arrival_time=datetime.utcnow() + timedelta(days=1, hours=2),
        price=299.99,
        aircraft_id=test_aircraft.id
    )
    db_session.add(flight)
    db_session.commit()
    db_session.refresh(flight)
    return flight

@pytest.fixture
def test_seats(db_session, test_aircraft):
    """Create test seats"""
    seats = []
    for row in range(1, 4):  # 3 rows
        for col in ['A', 'B', 'C', 'D', 'E', 'F']:
            seat_class = "FIRST" if row == 1 else "BUSINESS" if row == 2 else "ECONOMY"
            seat = Seat(
                aircraft_id=test_aircraft.id,
                row=row,
                col=col,
                seat_number=f"{row}{col}",
                seat_class=seat_class
            )
            seats.append(seat)
            db_session.add(seat)
    
    db_session.commit()
    for seat in seats:
        db_session.refresh(seat)
    return seats
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.database import Base

class Flight(Base):
    __tablename__ = "FLIGHTS"

    id = Column(Integer, primary_key=True)
    from_city = Column(String(50), nullable=False)
    to_city = Column(String(50), nullable=False)
    from_airport_code = Column(String(10), nullable=True)  # e.g., "BOM", "DEL"
    to_airport_code = Column(String(10), nullable=True)    # e.g., "BOM", "DEL"
    departure_time = Column(DateTime, nullable=False)
    arrival_time = Column(DateTime, nullable=False)
    duration = Column(Integer, nullable=True)  # Duration in minutes
    price = Column(Float, nullable=False)
    airline = Column(String(100), nullable=True)  # e.g., "Safe Travel Airways"
    flight_number = Column(String(20), nullable=True)  # e.g., "ST101"
    aircraft_type = Column(String(50), nullable=True)  # e.g., "Airbus A320"
    aircraft_id = Column(Integer, ForeignKey("AIRCRAFTS.id"), nullable=False)

    aircraft = relationship("Aircraft")
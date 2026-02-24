from sqlalchemy import Column, Integer, String, ForeignKey, Identity
from sqlalchemy.orm import relationship
from app.database import Base

class Seat(Base):
    __tablename__ = "SEATS"

    id = Column(Integer, Identity(start=1), primary_key=True)
    aircraft_id = Column(Integer, ForeignKey("AIRCRAFTS.id"), nullable=False)
    row = Column(Integer, nullable=False)
    col = Column(String(1), nullable=False)
    seat_number = Column(String(5), nullable=False)  # e.g., "12A", "15F"
    seat_class = Column(String(20), nullable=False, default="ECONOMY")  # ECONOMY, BUSINESS, FIRST
    status = Column(String(20), nullable=False, default="AVAILABLE")
    
    aircraft = relationship("Aircraft")
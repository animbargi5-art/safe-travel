from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from app.database import Base

class Waitlist(Base):
    __tablename__ = "WAITLIST"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("USERS.id"), nullable=False)
    flight_id = Column(Integer, ForeignKey("FLIGHTS.id"), nullable=False)
    
    # Waitlist preferences
    preferred_seat_class = Column(String(20), nullable=True)  # ECONOMY, BUSINESS, FIRST, ANY
    preferred_seat_position = Column(String(20), nullable=True)  # WINDOW, AISLE, MIDDLE, ANY
    max_price = Column(Integer, nullable=True)  # Maximum price willing to pay
    
    # Waitlist status
    status = Column(String(20), nullable=False, default="ACTIVE")  # ACTIVE, ALLOCATED, EXPIRED, CANCELLED
    priority = Column(Integer, nullable=False)  # Lower number = higher priority
    
    # Contact preferences
    notify_email = Column(Boolean, default=True)
    notify_sms = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    allocated_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)  # When waitlist entry expires
    
    # Relationships
    user = relationship("User")
    flight = relationship("Flight")

    def __repr__(self):
        return f"<Waitlist(id={self.id}, user_id={self.user_id}, flight_id={self.flight_id}, status='{self.status}', priority={self.priority})>"
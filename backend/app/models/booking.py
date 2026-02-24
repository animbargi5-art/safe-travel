from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship

from app.database import Base
from app.constants.booking_status import BookingStatus

class Booking(Base):
    __tablename__ = "BOOKINGS"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("USERS.id"), nullable=False)

    flight_id = Column(Integer, ForeignKey("FLIGHTS.id"), nullable=False)
    seat_id = Column(Integer, ForeignKey("SEATS.id"), nullable=False)

    # Passenger details
    passenger_name = Column(String(100), nullable=True)
    passenger_email = Column(String(100), nullable=True)
    passenger_phone = Column(String(20), nullable=True)
    
    # Booking details
    price = Column(Float, nullable=True)  # Price at time of booking
    status = Column(String(20), nullable=False)
    group_booking_id = Column(String(50), nullable=True)  # For group bookings
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)

    # Relationships (simplified to avoid circular imports)
    user = relationship("User")
    flight = relationship("Flight")
    seat = relationship("Seat")
    # payments = relationship("Payment", back_populates="booking")

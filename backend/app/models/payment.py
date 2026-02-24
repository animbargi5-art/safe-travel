from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship

from app.database import Base

class Payment(Base):
    __tablename__ = "PAYMENTS"

    id = Column(Integer, primary_key=True)
    booking_id = Column(Integer, ForeignKey("BOOKINGS.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("USERS.id"), nullable=False)
    
    # Stripe integration
    stripe_payment_intent_id = Column(String(255), unique=True, nullable=False)
    stripe_charge_id = Column(String(255), nullable=True)
    
    # Payment details
    amount = Column(Float, nullable=False)
    currency = Column(String(3), nullable=False, default="USD")
    status = Column(String(20), nullable=False)
    
    # Refund tracking
    refunded_amount = Column(Float, nullable=True, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    refunded_at = Column(DateTime, nullable=True)
    
    # Relationships (simplified to avoid circular imports)
    booking = relationship("Booking")
    user = relationship("User")

    def __repr__(self):
        return f"<Payment(id={self.id}, booking_id={self.booking_id}, amount={self.amount}, status='{self.status}')>"
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.booking import Booking
from app.constants.booking_status import BookingStatus


def confirm_booking(db: Session, booking_id: int):
    booking = db.get(Booking, booking_id)

    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    if booking.status != BookingStatus.HOLD:
        raise HTTPException(
            status_code=409,
            detail="Only HOLD bookings can be confirmed"
        )

    booking.status = BookingStatus.CONFIRMED
    booking.expires_at = None

    db.commit()
    db.refresh(booking)
    return booking

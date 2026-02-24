from datetime import datetime
from sqlalchemy.orm import Session

from app.models.booking import Booking
from app.constants.booking_status import BookingStatus
from app.dharma.booking_dharma import check_dharma


def expire_old_bookings(db: Session):
    now = datetime.utcnow()

    expired = (
        db.query(Booking)
        .filter(
            Booking.status == BookingStatus.HOLD,
            Booking.expires_at <= now
        )
        .all()
    )

    for booking in expired:
        check_dharma(booking.status, BookingStatus.EXPIRED)
        booking.status = BookingStatus.EXPIRED

    if expired:
        db.commit()

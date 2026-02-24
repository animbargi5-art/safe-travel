from app.constants.booking_status import BookingStatus


ALLOWED_TRANSITIONS = {
    BookingStatus.HOLD: {
        BookingStatus.CONFIRMED,
        BookingStatus.EXPIRED,
        BookingStatus.CANCELLED,
    },
    BookingStatus.CONFIRMED: {
        BookingStatus.CANCELLED,
    },
    BookingStatus.EXPIRED: set(),
    BookingStatus.CANCELLED: set(),
}


def can_transition(from_status: BookingStatus, to_status: BookingStatus) -> bool:
    return to_status in ALLOWED_TRANSITIONS.get(from_status, set())

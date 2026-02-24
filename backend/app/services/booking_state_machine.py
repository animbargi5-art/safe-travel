from app.constants.booking_status import BookingStatus

ALLOWED_TRANSITIONS = {
    BookingStatus.HOLD: {
        BookingStatus.CONFIRMED,
        BookingStatus.EXPIRED,
    },
    BookingStatus.CONFIRMED: {
        BookingStatus.CANCELLED,
    },
}


def is_valid_transition(current: str, next_status: str) -> bool:
    try:
        current_state = BookingStatus(current)
        next_state = BookingStatus(next_status)
    except ValueError:
        return False

    return next_state in ALLOWED_TRANSITIONS.get(current_state, set())

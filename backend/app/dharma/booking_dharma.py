from app.constants.booking_status import BookingStatus

class DharmaViolation(Exception):
    pass

ALLOWED = {
    BookingStatus.HOLD: {
        BookingStatus.HOLD,        # refresh
        BookingStatus.CONFIRMED,   # payment success
        BookingStatus.EXPIRED
    },
    BookingStatus.EXPIRED: {
        BookingStatus.HOLD
    },
    BookingStatus.CONFIRMED: set(),  # irreversible
}

def check_dharma(old, new):
    if new not in ALLOWED.get(old, set()):
        raise DharmaViolation(f"{old} → {new} not allowed")

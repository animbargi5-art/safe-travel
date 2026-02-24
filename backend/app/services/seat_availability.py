from sqlalchemy.orm import Session
from sqlalchemy import case
from app.models.seat import Seat
from app.models.booking import Booking
from app.constants.booking_status import BookingStatus

from apscheduler.schedulers.background import BackgroundScheduler
from app.database import SessionLocal
from app.services.expire_bookings import expire_old_bookings

from app.models.flight import Flight

def start_scheduler():
    scheduler = BackgroundScheduler()

    scheduler.add_job(
        func=expire_job,
        trigger="interval",
        minutes=1,
        id="expire_bookings",
        replace_existing=True,
    )

    scheduler.start()


def expire_job():
    db = SessionLocal()
    try:
        expire_old_bookings(db)
    finally:
        db.close()


def get_available_seats(db: Session, flight_id: int):
    # 1️⃣ Get flight
    flight = db.query(Flight).filter(Flight.id == flight_id).first()

    if not flight:
        return []

    aircraft_id = flight.aircraft_id

    # 2️⃣ Seats already blocked for this flight
    blocked = (
        db.query(Booking.seat_id)
        .filter(
            Booking.flight_id == flight_id,
            Booking.status.in_([
                BookingStatus.HOLD,
                BookingStatus.CONFIRMED
            ])
        )
        .subquery()
    )

    # 3️⃣ Get all seats for this aircraft with status
    all_seats = (
        db.query(Seat)
        .filter(Seat.aircraft_id == aircraft_id)
        .all()
    )

    # 4️⃣ Set status based on availability
    seats_with_status = []
    blocked_seat_ids = [row[0] for row in db.query(blocked).all()]
    
    for seat in all_seats:
        seat_dict = {
            "id": seat.id,
            "row": seat.row,
            "col": seat.col,
            "seat_number": seat.seat_number,
            "seat_class": seat.seat_class,
            "status": "BOOKED" if seat.id in blocked_seat_ids else "AVAILABLE"
        }
        seats_with_status.append(seat_dict)

    return seats_with_status

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database_dep import get_db
from app.models.seat import Seat
from app.models.flight import Flight
from app.models.booking import Booking

from app.schemas.seat import SeatResponse
from app.services.seat_availability import get_available_seats

from app.services.seat_map_service import get_seat_map

router = APIRouter(prefix="/seats", tags=["Seats"])

@router.get("/map/{flight_id}")
def seat_map_api(
    flight_id: int,
    db: Session = Depends(get_db)
):
    return get_seat_map(db, flight_id)


@router.get("/available/{flight_id}", response_model=list[SeatResponse])
def available_seats_api(
    flight_id: int,
    db: Session = Depends(get_db)
):
    return get_available_seats(db, flight_id)


@router.get("/{flight_id}")
def get_seats(flight_id: int, db: Session = Depends(get_db)):
    booked_seats = db.query(Booking.seat_id).filter(
        and_(
            Booking.flight_id == flight_id,
            (
                (Booking.status == "CONFIRMED") |
                ((Booking.status == "LOCKED") & (Booking.expires_at > datetime.utcnow()))
            )
        )
    ).all()

    booked_seat_ids = [b[0] for b in booked_seats]

    seats = db.query(Seat).all()

    return {
        "available": [s for s in seats if s.id not in booked_seat_ids],
        "unavailable": booked_seat_ids
    }

@router.get("/available/{flight_id}")
def available_seats(flight_id: int, db: Session = Depends(get_db)):
    flight = db.get(Flight, flight_id)

    if not flight:
        return {"error": "Flight not found"}

    subquery = (
        db.query(Booking.seat_id)
        .filter(
            Booking.flight_id == flight_id,
            Booking.status.in_(["HOLD", "CONFIRMED"])
        )
        .subquery()
    )

    seats = (
        db.query(Seat)
        .filter(
            Seat.aircraft_id == flight.aircraft_id,
            ~Seat.id.in_(subquery)
        )
        .all()
    )

    return {
        "flight_id": flight_id,
        "available_seats": [
            {
                "seat_id": s.id,
                "seat_number": s.seat_number,
                "seat_class": s.seat_class
            }
            for s in seats
        ]
    }

@router.get("/availability/{flight_id}")
def seat_availability(
    flight_id: int,
    db: Session = Depends(get_db)
):
    return get_available_seats(db, flight_id)

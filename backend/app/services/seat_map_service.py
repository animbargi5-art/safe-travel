from sqlalchemy.orm import Session
from app.models.seat import Seat


def get_seat_map(db: Session, flight_id: int):
    seats = (
        db.query(Seat)
        .filter(Seat.flight_id == flight_id)
        .all()
    )

    seat_map = {}
    for seat in seats:
        row = seat.seat_number[:-1]
        seat_map.setdefault(row, []).append(seat.seat_number)

    return seat_map

def generate_seats_for_aircraft(db, aircraft):
    rows = aircraft.rows
    layout = aircraft.layout.split("_")  # ["ABC", "DEF"]

    for row in range(1, rows + 1):
        for block in layout:
            for col in block:
                seat = Seat(
                    aircraft_id=aircraft.id,
                    row=row,
                    col=col
                )
                db.add(seat)

    db.commit()
from app.models.aircraft import Aircraft
from app.models.seat import Seat

def create_airbus_a320(db):
    existing = db.query(Aircraft).filter(Aircraft.model == "Airbus A320").first()
    if existing:
        return existing

    aircraft = Aircraft(
        model="Airbus A320",
        seat_rows=30,
        layout="3-3"  # A320 typical layout
    )
    db.add(aircraft)
    db.commit()
    db.refresh(aircraft)

    # Create seats dynamically
    rows = 30   # 30 rows
    seats_per_row = ["A", "B", "C", "D", "E", "F"]

    for row in range(1, rows + 1):
        for letter in seats_per_row:
            # Determine seat class based on row
            if row <= 3:
                seat_class = "FIRST"
            elif row <= 10:
                seat_class = "BUSINESS"
            else:
                seat_class = "ECONOMY"
            
            seat = Seat(
                aircraft_id=aircraft.id,
                row=row,
                col=letter,
                seat_number=f"{row}{letter}",
                seat_class=seat_class
            )
            db.add(seat)

    db.commit()
    return aircraft

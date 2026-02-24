from app.database import SessionLocal
from app.models.aircraft import Aircraft
from app.models.seat import Seat

# Airbus A320 layout: 3-3 (A B C | D E F)
SEAT_COLUMNS = ["A", "B", "C", "D", "E", "F"]

def seed_airbus_a320():
    db = SessionLocal()

    # 1️⃣ Create aircraft
    aircraft = Aircraft(
        model="Airbus A320",
        seat_rows=30,
        layout="3-3"
    )
    db.add(aircraft)
    db.commit()
    db.refresh(aircraft)

    # 2️⃣ Create seats dynamically
    seats = []
    for row in range(1, 31):
        for col in SEAT_COLUMNS:
            seats.append(
                Seat(
                    aircraft_id=aircraft.id,
                    row=row,
                    col=col,
                    status="AVAILABLE"
                )
            )

    db.add_all(seats)
    db.commit()
    db.close()

    print("✅ Airbus A320 with seats created")

if __name__ == "__main__":
    seed_airbus_a320()

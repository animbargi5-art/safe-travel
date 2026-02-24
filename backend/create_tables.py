# =========================
# create_tables.py
# =========================
from app.database import engine, Base
import app.models.user
import app.models.aircraft
import app.models.flight
import app.models.seat
import app.models.booking

def create_tables():
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Done.")

if __name__ == "__main__":
    create_tables()

from sqlalchemy import Column, Integer, String, Identity
from app.database import Base

class Aircraft(Base):
    __tablename__ = "AIRCRAFTS"

    id = Column(
        Integer,
        Identity(start=1),
        primary_key=True
    )
    model = Column(String(50), nullable=False)
    seat_rows = Column(Integer, nullable=False)
    layout = Column(String(20), nullable=False)

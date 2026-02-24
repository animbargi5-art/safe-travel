from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class BookingCreate(BaseModel):
    flight_id: int
    seat_id: int
    user_id: int
    passenger_name: Optional[str] = None
    passenger_email: Optional[str] = None
    passenger_phone: Optional[str] = None

class BookingResponse(BaseModel):
    id: int
    user_id: int
    flight_id: int
    seat_id: int
    passenger_name: Optional[str]
    passenger_email: Optional[str]
    passenger_phone: Optional[str]
    price: Optional[float]
    status: str
    created_at: datetime
    expires_at: Optional[datetime]
    
    # Nested objects
    flight: Optional[dict] = None
    seat: Optional[dict] = None

    class Config:
        from_attributes = True

class BookingConfirm(BaseModel):
    passenger_name: str
    passenger_email: str
    passenger_phone: str
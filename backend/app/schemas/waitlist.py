from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any

class WaitlistCreate(BaseModel):
    flight_id: int
    preferred_seat_class: Optional[str] = "ANY"
    preferred_seat_position: Optional[str] = "ANY"
    max_price: Optional[int] = None
    notify_email: bool = True
    notify_sms: bool = False

class WaitlistResponse(BaseModel):
    id: int
    flight: Dict[str, Any]
    status: str
    priority: int
    created_at: datetime
    estimated_wait: Optional[str] = None

    class Config:
        from_attributes = True

class WaitlistStats(BaseModel):
    active_waitlist: int
    total_waitlist: int
    allocation_rate: float
"""
Group booking schemas for multi-passenger bookings
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class PassengerDetails(BaseModel):
    """Individual passenger details"""
    name: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., pattern=r'^[^@]+@[^@]+\.[^@]+$')
    phone: Optional[str] = Field(None, max_length=20)
    age: Optional[int] = Field(None, ge=0, le=120)
    special_requirements: Optional[str] = Field(None, max_length=500)


class GroupBookingRequest(BaseModel):
    """Request for group booking"""
    flight_id: int
    passengers: List[PassengerDetails] = Field(..., min_items=2, max_items=10)
    seat_preferences: Optional[str] = Field("together", description="together, window, aisle, mixed")
    seat_class_preference: Optional[str] = Field("ECONOMY", description="ECONOMY, BUSINESS, FIRST")
    special_requests: Optional[str] = Field(None, max_length=1000)


class GroupBookingResponse(BaseModel):
    """Response for group booking"""
    group_booking_id: str
    individual_bookings: List[dict]
    total_price: float
    seats_allocated: List[str]
    status: str
    created_at: datetime
    expires_at: datetime


class SeatAllocationStrategy(BaseModel):
    """Strategy for group seat allocation"""
    strategy: str = Field("keep_together", description="keep_together, spread_out, by_preference")
    max_separation: int = Field(2, description="Maximum rows between group members")
    prefer_aisle_access: bool = Field(True, description="Prefer seats with aisle access")
    allow_split_rows: bool = Field(True, description="Allow group to be split across rows")


class GroupBookingStats(BaseModel):
    """Statistics for group bookings"""
    total_group_bookings: int
    average_group_size: float
    most_popular_group_size: int
    successful_together_rate: float  # Percentage of groups seated together
    revenue_from_groups: float
"""
Flight schemas for API requests and responses
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date


class FlightSearchRequest(BaseModel):
    """Request schema for flight search"""
    from_city: Optional[str] = Field(None, description="Departure city")
    to_city: Optional[str] = Field(None, description="Destination city")
    departure_date: Optional[date] = Field(None, description="Departure date")
    return_date: Optional[date] = Field(None, description="Return date")
    min_price: Optional[float] = Field(None, ge=0, description="Minimum price")
    max_price: Optional[float] = Field(None, ge=0, description="Maximum price")
    sort_by: Optional[str] = Field("price", description="Sort by field")
    sort_order: Optional[str] = Field("asc", description="Sort order")
    limit: Optional[int] = Field(50, ge=1, le=100, description="Result limit")


class FlightSearchResponse(BaseModel):
    """Response schema for flight search results"""
    id: int
    from_city: str
    to_city: str
    from_airport_code: Optional[str] = None
    to_airport_code: Optional[str] = None
    departure_time: datetime
    arrival_time: Optional[datetime] = None
    duration: Optional[int] = None  # Duration in minutes
    price: float
    airline: Optional[str] = None
    flight_number: Optional[str] = None
    aircraft_type: Optional[str] = None
    available_seats: Optional[int] = None
    
    class Config:
        from_attributes = True


class FlightDetails(BaseModel):
    """Detailed flight information"""
    id: int
    from_city: str
    to_city: str
    from_airport_code: Optional[str] = None
    to_airport_code: Optional[str] = None
    departure_time: datetime
    arrival_time: Optional[datetime] = None
    duration: Optional[int] = None
    price: float
    airline: Optional[str] = None
    flight_number: Optional[str] = None
    aircraft_type: Optional[str] = None
    available_seats: Optional[int] = None
    total_seats: Optional[int] = None
    seat_classes: Optional[List[str]] = None
    amenities: Optional[List[str]] = None
    baggage_allowance: Optional[str] = None
    
    class Config:
        from_attributes = True


class PopularRoute(BaseModel):
    """Popular flight route information"""
    from_city: str
    to_city: str
    flight_count: int
    min_price: float
    avg_price: float


class CityList(BaseModel):
    """Available cities for flight search"""
    cities: List[str]
    departure_cities: List[str]
    destination_cities: List[str]


class PriceRange(BaseModel):
    """Price range information for flights"""
    min_price: float
    max_price: float
    avg_price: float


class FlightFilter(BaseModel):
    """Flight filter options"""
    departure_times: List[str] = ["morning", "afternoon", "evening", "night"]
    airlines: List[str] = []
    aircraft_types: List[str] = []
    price_ranges: List[dict] = [
        {"label": "Budget", "min": 0, "max": 5000},
        {"label": "Economy", "min": 5000, "max": 15000},
        {"label": "Premium", "min": 15000, "max": 30000},
        {"label": "Business", "min": 30000, "max": 100000}
    ]
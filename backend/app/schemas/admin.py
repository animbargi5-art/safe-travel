"""
Admin dashboard schemas for API requests and responses
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class AdminDashboardStats(BaseModel):
    """Overall dashboard statistics"""
    total_users: int
    total_flights: int
    total_bookings: int
    confirmed_bookings: int
    total_revenue: float
    recent_bookings: int  # Last 30 days
    recent_revenue: float  # Last 30 days
    popular_routes: List[Dict[str, Any]]


class FlightManagement(BaseModel):
    """Flight data for admin management"""
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
    total_bookings: int
    confirmed_bookings: int


class BookingManagement(BaseModel):
    """Booking data for admin management"""
    id: int
    user_email: str
    user_name: Optional[str] = None
    passenger_name: Optional[str] = None
    passenger_email: Optional[str] = None
    flight_route: str
    flight_number: Optional[str] = None
    departure_time: datetime
    seat_number: Optional[str] = None
    seat_class: Optional[str] = None
    price: Optional[float] = None
    status: str
    payment_status: Optional[str] = None
    created_at: datetime
    expires_at: Optional[datetime] = None


class UserManagement(BaseModel):
    """User data for admin management"""
    id: int
    email: str
    username: str
    full_name: Optional[str] = None
    phone: Optional[str] = None
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    total_bookings: int
    total_spent: float
    last_booking_date: Optional[datetime] = None


class RevenueStats(BaseModel):
    """Revenue statistics"""
    total_revenue: float
    avg_transaction: float
    total_transactions: int
    daily_revenue: List[Dict[str, Any]]
    top_routes: List[Dict[str, Any]]


class FlightCreate(BaseModel):
    """Schema for creating new flights"""
    from_city: str = Field(..., min_length=2, max_length=50)
    to_city: str = Field(..., min_length=2, max_length=50)
    from_airport_code: Optional[str] = Field(None, max_length=10)
    to_airport_code: Optional[str] = Field(None, max_length=10)
    departure_time: datetime
    arrival_time: datetime
    price: float = Field(..., gt=0)
    airline: Optional[str] = Field(None, max_length=100)
    flight_number: Optional[str] = Field(None, max_length=20)
    aircraft_type: Optional[str] = Field(None, max_length=50)
    aircraft_id: int


class FlightUpdate(BaseModel):
    """Schema for updating flights"""
    from_city: Optional[str] = Field(None, min_length=2, max_length=50)
    to_city: Optional[str] = Field(None, min_length=2, max_length=50)
    from_airport_code: Optional[str] = Field(None, max_length=10)
    to_airport_code: Optional[str] = Field(None, max_length=10)
    departure_time: Optional[datetime] = None
    arrival_time: Optional[datetime] = None
    price: Optional[float] = Field(None, gt=0)
    airline: Optional[str] = Field(None, max_length=100)
    flight_number: Optional[str] = Field(None, max_length=20)
    aircraft_type: Optional[str] = Field(None, max_length=50)


class SystemHealth(BaseModel):
    """System health status"""
    database_status: str
    recent_activity: Dict[str, int]
    timestamp: str


class AdminAction(BaseModel):
    """Admin action log"""
    action: str
    target_type: str  # 'flight', 'booking', 'user'
    target_id: int
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime
    admin_user_id: int


class BulkAction(BaseModel):
    """Bulk action request"""
    action: str  # 'cancel', 'confirm', 'delete'
    target_ids: List[int]
    reason: Optional[str] = None


class AdminNotification(BaseModel):
    """Admin notification"""
    id: int
    title: str
    message: str
    type: str  # 'info', 'warning', 'error', 'success'
    is_read: bool
    created_at: datetime
    expires_at: Optional[datetime] = None


class AdminSettings(BaseModel):
    """Admin system settings"""
    site_name: str = "Safe Travel"
    maintenance_mode: bool = False
    booking_hold_minutes: int = 10
    max_bookings_per_user: int = 10
    email_notifications_enabled: bool = True
    payment_processing_enabled: bool = True
    auto_seat_allocation_enabled: bool = True
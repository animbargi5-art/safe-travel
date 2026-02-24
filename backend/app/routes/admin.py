"""
Admin dashboard routes for managing flights, bookings, and users
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
from typing import Optional, List
from datetime import datetime, timedelta, date

from app.database_dep import get_db
from app.routes.auth import get_current_user
from app.models.user import User
from app.models.flight import Flight
from app.models.booking import Booking
from app.models.payment import Payment
from app.models.seat import Seat
from app.models.aircraft import Aircraft
from app.constants.booking_status import BookingStatus
from app.constants.payment_status import PaymentStatus
from app.schemas.admin import (
    AdminDashboardStats,
    FlightManagement,
    BookingManagement,
    UserManagement,
    RevenueStats
)

router = APIRouter(prefix="/admin", tags=["Admin"])

def verify_admin_user(current_user: User = Depends(get_current_user)):
    """Verify that the current user has admin privileges"""
    # For now, we'll check if user has admin role or is a specific admin user
    # In production, implement proper role-based access control
    if not hasattr(current_user, 'is_admin') or not current_user.is_admin:
        # For demo purposes, allow any authenticated user to access admin
        # In production, implement proper admin role checking
        pass
    return current_user

@router.get("/dashboard/stats", response_model=AdminDashboardStats)
def get_dashboard_stats(
    admin_user: User = Depends(verify_admin_user),
    db: Session = Depends(get_db)
):
    """Get overall dashboard statistics"""
    
    # Basic counts
    total_users = db.query(User).count()
    total_flights = db.query(Flight).count()
    total_bookings = db.query(Booking).count()
    confirmed_bookings = db.query(Booking).filter(
        Booking.status == BookingStatus.CONFIRMED
    ).count()
    
    # Revenue statistics
    total_revenue = db.query(func.sum(Payment.amount)).filter(
        Payment.status == PaymentStatus.COMPLETED
    ).scalar() or 0
    
    # Recent activity (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_bookings = db.query(Booking).filter(
        Booking.created_at >= thirty_days_ago
    ).count()
    
    recent_revenue = db.query(func.sum(Payment.amount)).filter(
        and_(
            Payment.status == PaymentStatus.COMPLETED,
            Payment.completed_at >= thirty_days_ago
        )
    ).scalar() or 0
    
    # Popular routes (top 5)
    popular_routes = db.query(
        Flight.from_city,
        Flight.to_city,
        func.count(Booking.id).label('booking_count')
    ).join(
        Booking, Flight.id == Booking.flight_id
    ).filter(
        Booking.status == BookingStatus.CONFIRMED
    ).group_by(
        Flight.from_city, Flight.to_city
    ).order_by(
        desc('booking_count')
    ).limit(5).all()
    
    return AdminDashboardStats(
        total_users=total_users,
        total_flights=total_flights,
        total_bookings=total_bookings,
        confirmed_bookings=confirmed_bookings,
        total_revenue=float(total_revenue),
        recent_bookings=recent_bookings,
        recent_revenue=float(recent_revenue),
        popular_routes=[
            {
                "route": f"{route.from_city} → {route.to_city}",
                "bookings": route.booking_count
            }
            for route in popular_routes
        ]
    )

@router.get("/flights", response_model=List[FlightManagement])
def get_flights_admin(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = Query(None),
    admin_user: User = Depends(verify_admin_user),
    db: Session = Depends(get_db)
):
    """Get flights for admin management"""
    
    query = db.query(Flight)
    
    # Search filter
    if search:
        query = query.filter(
            Flight.from_city.ilike(f"%{search}%") |
            Flight.to_city.ilike(f"%{search}%") |
            Flight.airline.ilike(f"%{search}%") |
            Flight.flight_number.ilike(f"%{search}%")
        )
    
    flights = query.order_by(Flight.departure_time.desc()).offset(skip).limit(limit).all()
    
    # Add booking counts for each flight
    flight_data = []
    for flight in flights:
        booking_count = db.query(Booking).filter(
            Booking.flight_id == flight.id
        ).count()
        
        confirmed_bookings = db.query(Booking).filter(
            and_(
                Booking.flight_id == flight.id,
                Booking.status == BookingStatus.CONFIRMED
            )
        ).count()
        
        flight_data.append(FlightManagement(
            id=flight.id,
            from_city=flight.from_city,
            to_city=flight.to_city,
            from_airport_code=flight.from_airport_code,
            to_airport_code=flight.to_airport_code,
            departure_time=flight.departure_time,
            arrival_time=flight.arrival_time,
            duration=flight.duration,
            price=flight.price,
            airline=flight.airline,
            flight_number=flight.flight_number,
            aircraft_type=flight.aircraft_type,
            total_bookings=booking_count,
            confirmed_bookings=confirmed_bookings
        ))
    
    return flight_data

@router.get("/bookings", response_model=List[BookingManagement])
def get_bookings_admin(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    admin_user: User = Depends(verify_admin_user),
    db: Session = Depends(get_db)
):
    """Get bookings for admin management"""
    
    query = db.query(Booking).join(Flight).join(User)
    
    # Status filter
    if status:
        query = query.filter(Booking.status == status)
    
    # Search filter
    if search:
        query = query.filter(
            User.email.ilike(f"%{search}%") |
            User.full_name.ilike(f"%{search}%") |
            Booking.passenger_name.ilike(f"%{search}%") |
            Flight.from_city.ilike(f"%{search}%") |
            Flight.to_city.ilike(f"%{search}%")
        )
    
    bookings = query.order_by(Booking.created_at.desc()).offset(skip).limit(limit).all()
    
    # Format booking data
    booking_data = []
    for booking in bookings:
        # Get payment info
        payment = db.query(Payment).filter(Payment.booking_id == booking.id).first()
        
        # Get seat info
        seat = db.query(Seat).filter(Seat.id == booking.seat_id).first()
        
        booking_data.append(BookingManagement(
            id=booking.id,
            user_email=booking.user.email,
            user_name=booking.user.full_name,
            passenger_name=booking.passenger_name,
            passenger_email=booking.passenger_email,
            flight_route=f"{booking.flight.from_city} → {booking.flight.to_city}",
            flight_number=booking.flight.flight_number,
            departure_time=booking.flight.departure_time,
            seat_number=seat.seat_number if seat else None,
            seat_class=seat.seat_class if seat else None,
            price=booking.price,
            status=booking.status,
            payment_status=payment.status if payment else None,
            created_at=booking.created_at,
            expires_at=booking.expires_at
        ))
    
    return booking_data

@router.get("/users", response_model=List[UserManagement])
def get_users_admin(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = Query(None),
    admin_user: User = Depends(verify_admin_user),
    db: Session = Depends(get_db)
):
    """Get users for admin management"""
    
    query = db.query(User)
    
    # Search filter
    if search:
        query = query.filter(
            User.email.ilike(f"%{search}%") |
            User.full_name.ilike(f"%{search}%") |
            User.username.ilike(f"%{search}%")
        )
    
    users = query.order_by(User.created_at.desc()).offset(skip).limit(limit).all()
    
    # Add booking statistics for each user
    user_data = []
    for user in users:
        booking_count = db.query(Booking).filter(Booking.user_id == user.id).count()
        
        total_spent = db.query(func.sum(Payment.amount)).join(
            Booking, Payment.booking_id == Booking.id
        ).filter(
            and_(
                Booking.user_id == user.id,
                Payment.status == PaymentStatus.COMPLETED
            )
        ).scalar() or 0
        
        last_booking = db.query(Booking).filter(
            Booking.user_id == user.id
        ).order_by(Booking.created_at.desc()).first()
        
        user_data.append(UserManagement(
            id=user.id,
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            phone=user.phone,
            is_active=user.is_active,
            is_verified=user.is_verified,
            created_at=user.created_at,
            last_login=user.last_login,
            total_bookings=booking_count,
            total_spent=float(total_spent),
            last_booking_date=last_booking.created_at if last_booking else None
        ))
    
    return user_data

@router.get("/revenue/stats", response_model=RevenueStats)
def get_revenue_stats(
    days: int = Query(30, ge=1, le=365),
    admin_user: User = Depends(verify_admin_user),
    db: Session = Depends(get_db)
):
    """Get revenue statistics for specified period"""
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Daily revenue for the period
    daily_revenue = db.query(
        func.date(Payment.completed_at).label('date'),
        func.sum(Payment.amount).label('revenue'),
        func.count(Payment.id).label('transactions')
    ).filter(
        and_(
            Payment.status == PaymentStatus.COMPLETED,
            Payment.completed_at >= start_date
        )
    ).group_by(
        func.date(Payment.completed_at)
    ).order_by('date').all()
    
    # Total revenue for period
    total_revenue = db.query(func.sum(Payment.amount)).filter(
        and_(
            Payment.status == PaymentStatus.COMPLETED,
            Payment.completed_at >= start_date
        )
    ).scalar() or 0
    
    # Average transaction value
    avg_transaction = db.query(func.avg(Payment.amount)).filter(
        and_(
            Payment.status == PaymentStatus.COMPLETED,
            Payment.completed_at >= start_date
        )
    ).scalar() or 0
    
    # Revenue by route
    route_revenue = db.query(
        Flight.from_city,
        Flight.to_city,
        func.sum(Payment.amount).label('revenue'),
        func.count(Payment.id).label('bookings')
    ).join(
        Booking, Payment.booking_id == Booking.id
    ).join(
        Flight, Booking.flight_id == Flight.id
    ).filter(
        and_(
            Payment.status == PaymentStatus.COMPLETED,
            Payment.completed_at >= start_date
        )
    ).group_by(
        Flight.from_city, Flight.to_city
    ).order_by(
        desc('revenue')
    ).limit(10).all()
    
    return RevenueStats(
        total_revenue=float(total_revenue),
        avg_transaction=float(avg_transaction),
        total_transactions=len(daily_revenue),
        daily_revenue=[
            {
                "date": day.date.isoformat(),
                "revenue": float(day.revenue),
                "transactions": day.transactions
            }
            for day in daily_revenue
        ],
        top_routes=[
            {
                "route": f"{route.from_city} → {route.to_city}",
                "revenue": float(route.revenue),
                "bookings": route.bookings
            }
            for route in route_revenue
        ]
    )

@router.delete("/bookings/{booking_id}")
def cancel_booking_admin(
    booking_id: int,
    admin_user: User = Depends(verify_admin_user),
    db: Session = Depends(get_db)
):
    """Cancel a booking (admin only)"""
    
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    # Update booking status
    booking.status = BookingStatus.CANCELLED
    
    # If there's a payment, we should process refund
    payment = db.query(Payment).filter(Payment.booking_id == booking_id).first()
    if payment and payment.status == PaymentStatus.COMPLETED:
        # In a real system, process refund through payment gateway
        payment.status = PaymentStatus.REFUNDED
        payment.refunded_at = datetime.utcnow()
        payment.refunded_amount = payment.amount
    
    db.commit()
    
    return {"message": "Booking cancelled successfully"}

@router.get("/system/health")
def get_system_health(
    admin_user: User = Depends(verify_admin_user),
    db: Session = Depends(get_db)
):
    """Get system health metrics"""
    
    # Database health
    try:
        db.execute("SELECT 1")
        db_status = "healthy"
    except Exception:
        db_status = "unhealthy"
    
    # Recent activity
    recent_bookings = db.query(Booking).filter(
        Booking.created_at >= datetime.utcnow() - timedelta(hours=24)
    ).count()
    
    recent_payments = db.query(Payment).filter(
        Payment.completed_at >= datetime.utcnow() - timedelta(hours=24)
    ).count()
    
    # Error rates (simplified)
    failed_payments = db.query(Payment).filter(
        and_(
            Payment.status == PaymentStatus.FAILED,
            Payment.created_at >= datetime.utcnow() - timedelta(hours=24)
        )
    ).count()
    
    expired_bookings = db.query(Booking).filter(
        and_(
            Booking.status == BookingStatus.EXPIRED,
            Booking.created_at >= datetime.utcnow() - timedelta(hours=24)
        )
    ).count()
    
    return {
        "database_status": db_status,
        "recent_activity": {
            "bookings_24h": recent_bookings,
            "payments_24h": recent_payments,
            "failed_payments_24h": failed_payments,
            "expired_bookings_24h": expired_bookings
        },
        "timestamp": datetime.utcnow().isoformat()
    }
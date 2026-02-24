"""
Group booking routes for multi-passenger bookings
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database_dep import get_db
from app.routes.auth import get_current_user
from app.models.user import User
from app.schemas.group_booking import (
    GroupBookingRequest,
    GroupBookingResponse,
    GroupBookingStats
)
from app.services.group_booking_service import GroupBookingService

router = APIRouter(prefix="/group-booking", tags=["Group Booking"])

@router.post("/create", response_model=GroupBookingResponse)
def create_group_booking(
    booking_request: GroupBookingRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a group booking for multiple passengers
    """
    
    try:
        service = GroupBookingService(db)
        
        result = service.create_group_booking(
            user_id=current_user.id,
            flight_id=booking_request.flight_id,
            passengers=booking_request.passengers,
            seat_preferences=booking_request.seat_preferences,
            seat_class_preference=booking_request.seat_class_preference
        )
        
        return GroupBookingResponse(**result)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create group booking"
        )

@router.post("/confirm/{group_booking_id}")
def confirm_group_booking(
    group_booking_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Confirm a group booking
    """
    
    try:
        service = GroupBookingService(db)
        
        result = service.confirm_group_booking(
            group_booking_id=group_booking_id,
            user_id=current_user.id
        )
        
        return result
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to confirm group booking"
        )

@router.delete("/cancel/{group_booking_id}")
def cancel_group_booking(
    group_booking_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cancel a group booking
    """
    
    try:
        service = GroupBookingService(db)
        
        result = service.cancel_group_booking(
            group_booking_id=group_booking_id,
            user_id=current_user.id
        )
        
        return result
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel group booking"
        )

@router.get("/my-groups")
def get_my_group_bookings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's group bookings
    """
    
    from app.models.booking import Booking
    from sqlalchemy import and_
    
    # Get all group bookings for the user
    group_bookings = db.query(Booking.group_booking_id).filter(
        and_(
            Booking.user_id == current_user.id,
            Booking.group_booking_id.isnot(None)
        )
    ).distinct().all()
    
    result = []
    for group_id_tuple in group_bookings:
        group_id = group_id_tuple[0]
        
        # Get all bookings in this group
        bookings = db.query(Booking).filter(
            Booking.group_booking_id == group_id
        ).all()
        
        if bookings:
            # Load related data
            for booking in bookings:
                booking.flight = db.query(Flight).filter(Flight.id == booking.flight_id).first()
                booking.seat = db.query(Seat).filter(Seat.id == booking.seat_id).first()
            
            group_info = {
                "group_booking_id": group_id,
                "passenger_count": len(bookings),
                "status": bookings[0].status,  # All should have same status
                "flight": {
                    "id": bookings[0].flight.id,
                    "from_city": bookings[0].flight.from_city,
                    "to_city": bookings[0].flight.to_city,
                    "departure_time": bookings[0].flight.departure_time
                } if bookings[0].flight else None,
                "total_price": sum(booking.price for booking in bookings if booking.price),
                "created_at": bookings[0].created_at,
                "expires_at": bookings[0].expires_at,
                "passengers": [
                    {
                        "name": booking.passenger_name,
                        "seat_number": booking.seat.seat_number if booking.seat else None
                    }
                    for booking in bookings
                ]
            }
            
            result.append(group_info)
    
    return result

@router.get("/stats", response_model=GroupBookingStats)
def get_group_booking_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get group booking statistics (admin only)
    """
    
    # In production, add admin role check here
    
    try:
        service = GroupBookingService(db)
        stats = service.get_group_booking_stats()
        
        return GroupBookingStats(**stats)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get group booking statistics"
        )

@router.get("/availability/{flight_id}")
def check_group_availability(
    flight_id: int,
    passenger_count: int,
    seat_class: str = "ECONOMY",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Check if a flight can accommodate a group booking
    """
    
    try:
        service = GroupBookingService(db)
        available_seats = service._get_available_seats(flight_id, seat_class)
        
        can_accommodate = len(available_seats) >= passenger_count
        
        # Check if group can be seated together
        seats_together = 0
        if can_accommodate:
            allocated = service._allocate_together(available_seats, passenger_count)
            seats_together = len(allocated)
        
        return {
            "flight_id": flight_id,
            "passenger_count": passenger_count,
            "seat_class": seat_class,
            "can_accommodate": can_accommodate,
            "available_seats": len(available_seats),
            "seats_together": seats_together,
            "can_seat_together": seats_together == passenger_count
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check group availability"
        )
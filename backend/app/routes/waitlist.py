"""
Waitlist API Routes
Railway-style waitlist system for automatic seat allocation
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database_dep import get_db
from app.routes.auth import get_current_user
from app.models.user import User
from app.services.waitlist_service import WaitlistService
from app.schemas.waitlist import WaitlistCreate, WaitlistResponse, WaitlistStats

router = APIRouter(prefix="/waitlist", tags=["Waitlist"])

@router.post("/join", response_model=dict)
def join_waitlist(
    waitlist_data: WaitlistCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Join waitlist for a flight (like railway booking)
    """
    try:
        service = WaitlistService(db)
        
        result = service.add_to_waitlist(
            user_id=current_user.id,
            flight_id=waitlist_data.flight_id,
            preferred_seat_class=waitlist_data.preferred_seat_class,
            preferred_seat_position=waitlist_data.preferred_seat_position,
            max_price=waitlist_data.max_price,
            notify_email=waitlist_data.notify_email,
            notify_sms=waitlist_data.notify_sms
        )
        
        if result["success"]:
            return {
                "message": result["message"],
                "waitlist_position": result["waitlist_position"],
                "estimated_wait_time": result["estimated_wait_time"],
                "waitlist_id": result["waitlist_id"]
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to join waitlist"
        )

@router.get("/my-waitlist", response_model=List[WaitlistResponse])
def get_my_waitlist(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's waitlist entries
    """
    try:
        service = WaitlistService(db)
        waitlist_entries = service.get_user_waitlist(current_user.id)
        
        return waitlist_entries
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch waitlist"
        )

@router.delete("/{waitlist_id}")
def cancel_waitlist_entry(
    waitlist_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cancel a waitlist entry
    """
    try:
        service = WaitlistService(db)
        result = service.cancel_waitlist_entry(waitlist_id, current_user.id)
        
        if result["success"]:
            return {"message": result["message"]}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel waitlist entry"
        )

@router.get("/flight/{flight_id}/stats", response_model=WaitlistStats)
def get_flight_waitlist_stats(
    flight_id: int,
    db: Session = Depends(get_db)
):
    """
    Get waitlist statistics for a flight
    """
    try:
        service = WaitlistService(db)
        stats = service.get_flight_waitlist_stats(flight_id)
        
        return stats
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch waitlist stats"
        )

@router.post("/process-cancellation/{booking_id}")
def process_cancellation_allocation(
    booking_id: int,
    db: Session = Depends(get_db)
):
    """
    Process automatic allocation when a booking is cancelled
    This is called internally when bookings are cancelled
    """
    try:
        from app.models.booking import Booking
        
        # Get the cancelled booking
        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found"
            )
        
        service = WaitlistService(db)
        result = service.process_cancellation_allocation(booking)
        
        return {
            "allocated": result["allocated"],
            "details": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process cancellation allocation"
        )
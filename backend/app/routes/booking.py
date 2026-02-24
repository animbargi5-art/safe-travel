from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database_dep import get_db
from app.schemas.booking import BookingResponse, BookingConfirm, BookingCreate
from app.services.booking_service import (
    hold_seat, 
    confirm_booking, 
    get_user_bookings, 
    get_booking_details
)
from app.services.auto_seat_allocation import (
    auto_allocate_seat,
    get_seat_allocation_options,
    SeatPreference,
    SeatAllocationStrategy
)
from app.routes.auth import get_current_user

router = APIRouter(prefix="/booking", tags=["Booking"])


@router.post("/hold", response_model=BookingResponse)
def hold_seat_api(
    flight_id: int,
    seat_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        booking = hold_seat(
            db=db,
            flight_id=flight_id,
            seat_id=seat_id,
            user_id=current_user.id
        )
        return booking
    except Exception as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.post("/confirm/{booking_id}", response_model=BookingResponse)
def confirm_booking_api(
    booking_id: int,
    passenger_data: BookingConfirm,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        booking = confirm_booking(
            db=db, 
            booking_id=booking_id, 
            user_id=current_user.id,
            passenger_data=passenger_data.dict()
        )
        return booking
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/my-bookings", response_model=List[BookingResponse])
def get_my_bookings_api(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    bookings = get_user_bookings(db, current_user.id)
    return bookings


@router.get("/{booking_id}", response_model=BookingResponse)
def get_booking_api(
    booking_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    booking = get_booking_details(db, booking_id, current_user.id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking


@router.post("/auto-allocate")
def auto_allocate_seat_api(
    flight_id: int,
    seat_class_preference: str = None,
    position_preference: str = None,
    strategy: str = SeatAllocationStrategy.BEST_AVAILABLE,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Automatically allocate and hold the best available seat
    Uses user preferences if not specified
    """
    try:
        # Use user preferences as defaults
        if not seat_class_preference:
            seat_class_preference = current_user.preferred_seat_class or "ECONOMY"
        if not position_preference:
            position_preference = current_user.preferred_seat_position or SeatPreference.ANY
        
        # Find the best seat
        best_seat = auto_allocate_seat(
            db=db,
            flight_id=flight_id,
            seat_class_preference=seat_class_preference,
            position_preference=position_preference,
            strategy=strategy
        )
        
        if not best_seat:
            raise HTTPException(status_code=404, detail="No available seats found")
        
        # Hold the allocated seat
        booking = hold_seat(
            db=db,
            flight_id=flight_id,
            seat_id=best_seat.id,
            user_id=current_user.id
        )
        
        return {
            "booking": booking,
            "seat": {
                "id": best_seat.id,
                "seat_number": best_seat.seat_number,
                "seat_class": best_seat.seat_class,
                "row": best_seat.row,
                "col": best_seat.col
            },
            "allocation_reason": f"Auto-allocated using {strategy} strategy with {position_preference} preference"
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/allocation-options/{flight_id}")
def get_allocation_options_api(
    flight_id: int,
    db: Session = Depends(get_db)
):
    """
    Get seat allocation options and recommendations for a flight
    """
    try:
        options = get_seat_allocation_options(db, flight_id)
        return options
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{booking_id}")
def cancel_booking_api(
    booking_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cancel a booking and trigger waitlist allocation
    """
    try:
        from app.services.booking_service import cancel_booking
        
        result = cancel_booking(
            db=db,
            booking_id=booking_id,
            user_id=current_user.id
        )
        
        return {
            "message": result["message"],
            "waitlist_allocation": result.get("waitlist_allocation")
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
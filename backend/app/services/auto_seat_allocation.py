"""
Automatic seat allocation service
Intelligently assigns the best available seats based on user preferences and seat class
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.models.seat import Seat
from app.models.booking import Booking
from app.models.flight import Flight
from app.constants.booking_status import BookingStatus
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)

class SeatPreference:
    WINDOW = "WINDOW"
    AISLE = "AISLE" 
    MIDDLE = "MIDDLE"
    ANY = "ANY"

class SeatAllocationStrategy:
    BEST_AVAILABLE = "BEST_AVAILABLE"  # Best seats first (front, window/aisle)
    RANDOM = "RANDOM"  # Random available seat
    BACK_TO_FRONT = "BACK_TO_FRONT"  # Fill from back
    FRONT_TO_BACK = "FRONT_TO_BACK"  # Fill from front

def get_seat_position_type(seat_col: str) -> str:
    """Determine if seat is window, aisle, or middle"""
    # For typical A-B-C-D-E-F layout
    if seat_col in ['A', 'F']:
        return SeatPreference.WINDOW
    elif seat_col in ['C', 'D']:
        return SeatPreference.AISLE
    else:
        return SeatPreference.MIDDLE

def calculate_seat_score(seat: Seat, preference: str = SeatPreference.ANY) -> int:
    """
    Calculate a score for seat desirability
    Higher score = better seat
    """
    score = 0
    
    # Row preference (front rows are generally better)
    if seat.row <= 5:  # First class area
        score += 100
    elif seat.row <= 15:  # Business/premium area
        score += 50
    else:  # Economy
        score += max(0, 30 - seat.row)  # Prefer front of economy
    
    # Position preference
    position = get_seat_position_type(seat.col)
    if preference == SeatPreference.WINDOW and position == SeatPreference.WINDOW:
        score += 30
    elif preference == SeatPreference.AISLE and position == SeatPreference.AISLE:
        score += 30
    elif preference == SeatPreference.ANY:
        if position == SeatPreference.WINDOW:
            score += 20
        elif position == SeatPreference.AISLE:
            score += 15
        # Middle seats get no bonus
    
    # Seat class bonus
    if seat.seat_class == "FIRST":
        score += 200
    elif seat.seat_class == "BUSINESS":
        score += 100
    
    return score

def get_available_seats_for_flight(db: Session, flight_id: int) -> List[Seat]:
    """Get all available seats for a flight"""
    
    # Get flight to find aircraft
    flight = db.query(Flight).filter(Flight.id == flight_id).first()
    if not flight:
        return []
    
    # Get seats that are not booked or held
    blocked_seat_ids = (
        db.query(Booking.seat_id)
        .filter(
            Booking.flight_id == flight_id,
            Booking.status.in_([BookingStatus.HOLD, BookingStatus.CONFIRMED])
        )
        .subquery()
    )
    
    available_seats = (
        db.query(Seat)
        .filter(
            Seat.aircraft_id == flight.aircraft_id,
            ~Seat.id.in_(blocked_seat_ids)
        )
        .all()
    )
    
    return available_seats

def auto_allocate_seat(
    db: Session, 
    flight_id: int,
    seat_class_preference: str = "ECONOMY",
    position_preference: str = SeatPreference.ANY,
    strategy: str = SeatAllocationStrategy.BEST_AVAILABLE
) -> Optional[Seat]:
    """
    Automatically allocate the best available seat based on preferences
    
    Args:
        db: Database session
        flight_id: Flight ID to allocate seat for
        seat_class_preference: Preferred seat class (ECONOMY, BUSINESS, FIRST)
        position_preference: Preferred position (WINDOW, AISLE, MIDDLE, ANY)
        strategy: Allocation strategy
    
    Returns:
        Best available seat or None if no seats available
    """
    
    available_seats = get_available_seats_for_flight(db, flight_id)
    
    if not available_seats:
        logger.warning(f"No available seats for flight {flight_id}")
        return None
    
    # Filter by seat class preference if specified
    if seat_class_preference != "ANY":
        preferred_class_seats = [s for s in available_seats if s.seat_class == seat_class_preference]
        if preferred_class_seats:
            available_seats = preferred_class_seats
        # If no seats in preferred class, fall back to any available
    
    # Apply allocation strategy
    if strategy == SeatAllocationStrategy.BEST_AVAILABLE:
        # Score all seats and pick the best
        scored_seats = [
            (seat, calculate_seat_score(seat, position_preference)) 
            for seat in available_seats
        ]
        scored_seats.sort(key=lambda x: x[1], reverse=True)
        best_seat = scored_seats[0][0]
        
        logger.info(f"Auto-allocated seat {best_seat.seat_number} (score: {scored_seats[0][1]}) for flight {flight_id}")
        return best_seat
        
    elif strategy == SeatAllocationStrategy.FRONT_TO_BACK:
        # Sort by row ascending
        available_seats.sort(key=lambda s: (s.row, s.col))
        return available_seats[0]
        
    elif strategy == SeatAllocationStrategy.BACK_TO_FRONT:
        # Sort by row descending
        available_seats.sort(key=lambda s: (s.row, s.col), reverse=True)
        return available_seats[0]
        
    elif strategy == SeatAllocationStrategy.RANDOM:
        import random
        return random.choice(available_seats)
    
    # Default fallback
    return available_seats[0]

def get_seat_allocation_options(db: Session, flight_id: int) -> dict:
    """
    Get available seat allocation options for a flight
    Returns statistics about available seats by class and position
    """
    
    available_seats = get_available_seats_for_flight(db, flight_id)
    
    if not available_seats:
        return {
            "total_available": 0,
            "by_class": {},
            "by_position": {},
            "recommendations": []
        }
    
    # Count by class
    by_class = {}
    for seat in available_seats:
        by_class[seat.seat_class] = by_class.get(seat.seat_class, 0) + 1
    
    # Count by position
    by_position = {}
    for seat in available_seats:
        position = get_seat_position_type(seat.col)
        by_position[position] = by_position.get(position, 0) + 1
    
    # Generate recommendations
    recommendations = []
    
    # Best overall seat
    best_seat = auto_allocate_seat(db, flight_id, "ANY", SeatPreference.ANY, SeatAllocationStrategy.BEST_AVAILABLE)
    if best_seat:
        recommendations.append({
            "type": "best_overall",
            "seat": {
                "id": best_seat.id,
                "seat_number": best_seat.seat_number,
                "seat_class": best_seat.seat_class,
                "position": get_seat_position_type(best_seat.col)
            },
            "description": "Best available seat overall"
        })
    
    # Best window seat
    window_seat = auto_allocate_seat(db, flight_id, "ANY", SeatPreference.WINDOW, SeatAllocationStrategy.BEST_AVAILABLE)
    if window_seat and window_seat.id != best_seat.id:
        recommendations.append({
            "type": "best_window",
            "seat": {
                "id": window_seat.id,
                "seat_number": window_seat.seat_number,
                "seat_class": window_seat.seat_class,
                "position": get_seat_position_type(window_seat.col)
            },
            "description": "Best window seat"
        })
    
    # Best aisle seat
    aisle_seat = auto_allocate_seat(db, flight_id, "ANY", SeatPreference.AISLE, SeatAllocationStrategy.BEST_AVAILABLE)
    if aisle_seat and aisle_seat.id not in [best_seat.id, window_seat.id if window_seat else None]:
        recommendations.append({
            "type": "best_aisle",
            "seat": {
                "id": aisle_seat.id,
                "seat_number": aisle_seat.seat_number,
                "seat_class": aisle_seat.seat_class,
                "position": get_seat_position_type(aisle_seat.col)
            },
            "description": "Best aisle seat"
        })
    
    return {
        "total_available": len(available_seats),
        "by_class": by_class,
        "by_position": by_position,
        "recommendations": recommendations
    }
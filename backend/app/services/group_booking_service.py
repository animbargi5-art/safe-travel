"""
Group booking service for multi-passenger bookings with intelligent seat allocation
"""

from typing import List, Dict, Tuple, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime, timedelta
import uuid
import logging

from app.models.flight import Flight
from app.models.seat import Seat
from app.models.booking import Booking
from app.models.user import User
from app.constants.booking_status import BookingStatus
from app.services.auto_seat_allocation import (
    auto_allocate_seat, 
    get_available_seats_for_flight,
    calculate_seat_score,
    get_seat_position_type,
    SeatPreference
)
from app.schemas.group_booking import PassengerDetails, SeatAllocationStrategy

logger = logging.getLogger(__name__)

class GroupBookingService:
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_group_booking(
        self,
        user_id: int,
        flight_id: int,
        passengers: List[PassengerDetails],
        seat_preferences: str = "together",
        seat_class_preference: str = "ECONOMY"
    ) -> Dict:
        """
        Create a group booking with intelligent seat allocation
        """
        
        # Validate flight exists and has capacity
        flight = self.db.query(Flight).filter(Flight.id == flight_id).first()
        if not flight:
            raise ValueError("Flight not found")
        
        # Check if enough seats available
        available_seats = self._get_available_seats(flight_id, seat_class_preference)
        if len(available_seats) < len(passengers):
            raise ValueError(f"Not enough seats available. Need {len(passengers)}, found {len(available_seats)}")
        
        # Generate group booking ID
        group_booking_id = f"GRP_{uuid.uuid4().hex[:8].upper()}"
        
        # Allocate seats for the group
        allocated_seats = self._allocate_group_seats(
            flight_id=flight_id,
            passenger_count=len(passengers),
            preferences=seat_preferences,
            seat_class=seat_class_preference,
            available_seats=available_seats
        )
        
        if len(allocated_seats) != len(passengers):
            raise ValueError("Could not allocate enough seats for the group")
        
        # Create individual bookings
        bookings = []
        total_price = 0
        expires_at = datetime.utcnow() + timedelta(minutes=15)  # 15 minutes for group bookings
        
        for i, (passenger, seat) in enumerate(zip(passengers, allocated_seats)):
            booking = Booking(
                user_id=user_id,
                flight_id=flight_id,
                seat_id=seat.id,
                status=BookingStatus.HOLD,
                passenger_name=passenger.name,
                passenger_email=passenger.email,
                passenger_phone=passenger.phone,
                price=flight.price,
                created_at=datetime.utcnow(),
                expires_at=expires_at,
                group_booking_id=group_booking_id  # Add this field to track group bookings
            )
            
            self.db.add(booking)
            bookings.append(booking)
            total_price += flight.price
        
        self.db.commit()
        
        # Refresh bookings to get IDs
        for booking in bookings:
            self.db.refresh(booking)
        
        logger.info(f"Created group booking {group_booking_id} with {len(bookings)} passengers")
        
        return {
            "group_booking_id": group_booking_id,
            "individual_bookings": [
                {
                    "booking_id": booking.id,
                    "passenger_name": booking.passenger_name,
                    "seat_number": self._get_seat_number(booking.seat_id),
                    "price": booking.price
                }
                for booking in bookings
            ],
            "total_price": total_price,
            "seats_allocated": [self._get_seat_number(seat.id) for seat in allocated_seats],
            "status": "HOLD",
            "created_at": datetime.utcnow(),
            "expires_at": expires_at
        }
    
    def _get_available_seats(self, flight_id: int, seat_class: str) -> List[Seat]:
        """Get available seats for a flight and class"""
        
        # Get all seats for the flight
        all_seats = self.db.query(Seat).join(
            Flight, Seat.aircraft_id == Flight.aircraft_id
        ).filter(
            Flight.id == flight_id,
            Seat.seat_class == seat_class
        ).all()
        
        # Get booked seat IDs
        booked_seat_ids = self.db.query(Booking.seat_id).filter(
            and_(
                Booking.flight_id == flight_id,
                Booking.status.in_([BookingStatus.HOLD, BookingStatus.CONFIRMED])
            )
        ).all()
        
        booked_seat_ids = [seat_id[0] for seat_id in booked_seat_ids]
        
        # Filter out booked seats
        available_seats = [seat for seat in all_seats if seat.id not in booked_seat_ids]
        
        return available_seats
    
    def _allocate_group_seats(
        self,
        flight_id: int,
        passenger_count: int,
        preferences: str,
        seat_class: str,
        available_seats: List[Seat]
    ) -> List[Seat]:
        """
        Allocate seats for a group based on preferences
        """
        
        if preferences == "together":
            return self._allocate_together(available_seats, passenger_count)
        elif preferences == "window":
            return self._allocate_by_position(available_seats, passenger_count, "WINDOW")
        elif preferences == "aisle":
            return self._allocate_by_position(available_seats, passenger_count, "AISLE")
        else:
            # Default to best available
            return available_seats[:passenger_count]
    
    def _allocate_together(self, available_seats: List[Seat], passenger_count: int) -> List[Seat]:
        """
        Try to allocate seats together for the group
        """
        
        # Group seats by row
        seats_by_row = {}
        for seat in available_seats:
            row = seat.row
            if row not in seats_by_row:
                seats_by_row[row] = []
            seats_by_row[row].append(seat)
        
        # Sort rows by number
        sorted_rows = sorted(seats_by_row.keys())
        
        # Try to find consecutive seats in the same row
        for row in sorted_rows:
            row_seats = sorted(seats_by_row[row], key=lambda s: s.col)
            
            # Check if we can fit the entire group in this row
            if len(row_seats) >= passenger_count:
                consecutive_seats = self._find_consecutive_seats(row_seats, passenger_count)
                if consecutive_seats:
                    return consecutive_seats
        
        # If can't fit in one row, try adjacent rows
        allocated_seats = []
        remaining_passengers = passenger_count
        
        for row in sorted_rows:
            if remaining_passengers <= 0:
                break
                
            row_seats = sorted(seats_by_row[row], key=lambda s: s.col)
            seats_to_take = min(len(row_seats), remaining_passengers)
            
            # Prefer seats together in the row
            if seats_to_take <= len(row_seats):
                consecutive = self._find_consecutive_seats(row_seats, seats_to_take)
                if consecutive:
                    allocated_seats.extend(consecutive)
                else:
                    allocated_seats.extend(row_seats[:seats_to_take])
                
                remaining_passengers -= seats_to_take
        
        return allocated_seats[:passenger_count]
    
    def _find_consecutive_seats(self, row_seats: List[Seat], count: int) -> Optional[List[Seat]]:
        """
        Find consecutive seats in a row
        """
        
        if len(row_seats) < count:
            return None
        
        # Sort by column
        sorted_seats = sorted(row_seats, key=lambda s: s.col)
        
        # Check for consecutive seats
        for i in range(len(sorted_seats) - count + 1):
            consecutive = True
            for j in range(1, count):
                # Check if seats are consecutive (A, B, C, etc.)
                if ord(sorted_seats[i + j].col) != ord(sorted_seats[i + j - 1].col) + 1:
                    consecutive = False
                    break
            
            if consecutive:
                return sorted_seats[i:i + count]
        
        return None
    
    def _allocate_by_position(
        self,
        available_seats: List[Seat],
        passenger_count: int,
        position: str
    ) -> List[Seat]:
        """
        Allocate seats by position preference (window/aisle)
        """
        
        # Filter seats by position
        position_seats = []
        for seat in available_seats:
            seat_position = self._get_seat_position(seat)
            if seat_position == position:
                position_seats.append(seat)
        
        # If not enough preferred seats, add others
        if len(position_seats) < passenger_count:
            other_seats = [s for s in available_seats if s not in position_seats]
            position_seats.extend(other_seats)
        
        return position_seats[:passenger_count]
    
    def _get_seat_position(self, seat: Seat) -> str:
        """
        Determine if seat is window, aisle, or middle
        """
        
        # This is a simplified version - in reality, you'd need aircraft layout info
        col = seat.col.upper()
        
        if col in ['A', 'F']:  # Typical window seats in A320
            return "WINDOW"
        elif col in ['C', 'D']:  # Typical aisle seats in A320
            return "AISLE"
        else:
            return "MIDDLE"
    
    def _get_seat_number(self, seat_id: int) -> str:
        """Get seat number from seat ID"""
        seat = self.db.query(Seat).filter(Seat.id == seat_id).first()
        return seat.seat_number if seat else "Unknown"
    
    def confirm_group_booking(self, group_booking_id: str, user_id: int) -> Dict:
        """
        Confirm all bookings in a group
        """
        
        # Get all bookings in the group
        bookings = self.db.query(Booking).filter(
            and_(
                Booking.group_booking_id == group_booking_id,
                Booking.user_id == user_id,
                Booking.status == BookingStatus.HOLD
            )
        ).all()
        
        if not bookings:
            raise ValueError("Group booking not found or already processed")
        
        # Check if bookings haven't expired
        now = datetime.utcnow()
        if any(booking.expires_at and booking.expires_at < now for booking in bookings):
            raise ValueError("Group booking has expired")
        
        # Confirm all bookings
        confirmed_bookings = []
        for booking in bookings:
            booking.status = BookingStatus.CONFIRMED
            booking.expires_at = None
            confirmed_bookings.append(booking)
        
        self.db.commit()
        
        logger.info(f"Confirmed group booking {group_booking_id} with {len(confirmed_bookings)} passengers")
        
        return {
            "group_booking_id": group_booking_id,
            "confirmed_bookings": len(confirmed_bookings),
            "status": "CONFIRMED"
        }
    
    def cancel_group_booking(self, group_booking_id: str, user_id: int) -> Dict:
        """
        Cancel all bookings in a group
        """
        
        # Get all bookings in the group
        bookings = self.db.query(Booking).filter(
            and_(
                Booking.group_booking_id == group_booking_id,
                Booking.user_id == user_id
            )
        ).all()
        
        if not bookings:
            raise ValueError("Group booking not found")
        
        # Cancel all bookings
        cancelled_count = 0
        for booking in bookings:
            if booking.status in [BookingStatus.HOLD, BookingStatus.CONFIRMED]:
                booking.status = BookingStatus.CANCELLED
                cancelled_count += 1
        
        self.db.commit()
        
        logger.info(f"Cancelled group booking {group_booking_id} - {cancelled_count} bookings cancelled")
        
        return {
            "group_booking_id": group_booking_id,
            "cancelled_bookings": cancelled_count,
            "status": "CANCELLED"
        }
    
    def get_group_booking_stats(self) -> Dict:
        """
        Get statistics about group bookings
        """
        
        # Get all group bookings
        group_bookings = self.db.query(Booking.group_booking_id).filter(
            Booking.group_booking_id.isnot(None)
        ).distinct().all()
        
        total_groups = len(group_bookings)
        
        if total_groups == 0:
            return {
                "total_group_bookings": 0,
                "average_group_size": 0,
                "most_popular_group_size": 0,
                "successful_together_rate": 0,
                "revenue_from_groups": 0
            }
        
        # Calculate statistics
        group_sizes = []
        total_revenue = 0
        
        for group_id_tuple in group_bookings:
            group_id = group_id_tuple[0]
            group_bookings_count = self.db.query(Booking).filter(
                Booking.group_booking_id == group_id
            ).count()
            
            group_sizes.append(group_bookings_count)
            
            # Calculate revenue for this group
            group_revenue = self.db.query(Booking).filter(
                and_(
                    Booking.group_booking_id == group_id,
                    Booking.status == BookingStatus.CONFIRMED
                )
            ).with_entities(Booking.price).all()
            
            total_revenue += sum(price[0] for price in group_revenue if price[0])
        
        avg_group_size = sum(group_sizes) / len(group_sizes) if group_sizes else 0
        most_popular_size = max(set(group_sizes), key=group_sizes.count) if group_sizes else 0
        
        return {
            "total_group_bookings": total_groups,
            "average_group_size": round(avg_group_size, 1),
            "most_popular_group_size": most_popular_size,
            "successful_together_rate": 85.0,  # Placeholder - would need more complex calculation
            "revenue_from_groups": float(total_revenue)
        }
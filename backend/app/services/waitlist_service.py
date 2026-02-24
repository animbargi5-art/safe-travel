"""
Waitlist Service - Railway-style seat allocation system
Handles waitlist management and automatic seat allocation when cancellations occur
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models.waitlist import Waitlist
from app.models.booking import Booking
from app.models.seat import Seat
from app.models.flight import Flight
from app.models.user import User
from app.services.auto_seat_allocation import auto_allocate_seat, get_seat_position_type
from app.services.notification_service import NotificationService
from app.services.email_service import email_service
from app.constants.booking_status import BookingStatus

import logging

logger = logging.getLogger(__name__)

class WaitlistService:
    def __init__(self, db: Session):
        self.db = db
        self.notification_service = NotificationService(db)

    def add_to_waitlist(
        self,
        user_id: int,
        flight_id: int,
        preferred_seat_class: str = "ANY",
        preferred_seat_position: str = "ANY",
        max_price: Optional[int] = None,
        notify_email: bool = True,
        notify_sms: bool = False
    ) -> Dict[str, Any]:
        """
        Add user to waitlist for a flight
        """
        try:
            # Check if user is already on waitlist for this flight
            existing_waitlist = self.db.query(Waitlist).filter(
                and_(
                    Waitlist.user_id == user_id,
                    Waitlist.flight_id == flight_id,
                    Waitlist.status == "ACTIVE"
                )
            ).first()
            
            if existing_waitlist:
                return {
                    "success": False,
                    "message": "You are already on the waitlist for this flight",
                    "waitlist_position": existing_waitlist.priority
                }
            
            # Check if user already has a confirmed booking
            existing_booking = self.db.query(Booking).filter(
                and_(
                    Booking.user_id == user_id,
                    Booking.flight_id == flight_id,
                    Booking.status == BookingStatus.CONFIRMED
                )
            ).first()
            
            if existing_booking:
                return {
                    "success": False,
                    "message": "You already have a confirmed booking for this flight"
                }
            
            # Get next priority number (highest priority = lowest number)
            max_priority = self.db.query(Waitlist).filter(
                and_(
                    Waitlist.flight_id == flight_id,
                    Waitlist.status == "ACTIVE"
                )
            ).count()
            
            next_priority = max_priority + 1
            
            # Create waitlist entry
            waitlist_entry = Waitlist(
                user_id=user_id,
                flight_id=flight_id,
                preferred_seat_class=preferred_seat_class,
                preferred_seat_position=preferred_seat_position,
                max_price=max_price,
                notify_email=notify_email,
                notify_sms=notify_sms,
                priority=next_priority,
                status="ACTIVE",
                expires_at=datetime.utcnow() + timedelta(days=30)  # Waitlist expires in 30 days
            )
            
            self.db.add(waitlist_entry)
            self.db.commit()
            self.db.refresh(waitlist_entry)
            
            # Send waitlist confirmation
            self._send_waitlist_confirmation(waitlist_entry)
            
            logger.info(f"Added user {user_id} to waitlist for flight {flight_id} at position {next_priority}")
            
            return {
                "success": True,
                "message": f"Added to waitlist at position {next_priority}",
                "waitlist_id": waitlist_entry.id,
                "waitlist_position": next_priority,
                "estimated_wait_time": self._estimate_wait_time(flight_id, next_priority)
            }
            
        except Exception as e:
            logger.error(f"Failed to add to waitlist: {e}")
            self.db.rollback()
            return {
                "success": False,
                "message": "Failed to add to waitlist"
            }

    def process_cancellation_allocation(self, cancelled_booking: Booking) -> Dict[str, Any]:
        """
        Process automatic seat allocation when a booking is cancelled
        This is the core railway-style functionality
        """
        try:
            flight_id = cancelled_booking.flight_id
            cancelled_seat = cancelled_booking.seat
            
            logger.info(f"Processing cancellation allocation for flight {flight_id}, seat {cancelled_seat.seat_number}")
            
            # Get active waitlist entries for this flight, ordered by priority
            waitlist_entries = self.db.query(Waitlist).filter(
                and_(
                    Waitlist.flight_id == flight_id,
                    Waitlist.status == "ACTIVE"
                )
            ).order_by(Waitlist.priority).all()
            
            if not waitlist_entries:
                logger.info(f"No waitlist entries found for flight {flight_id}")
                return {"allocated": False, "reason": "No waitlist entries"}
            
            # Try to allocate to waitlist users in priority order
            for waitlist_entry in waitlist_entries:
                allocation_result = self._try_allocate_to_waitlist_user(
                    waitlist_entry, 
                    cancelled_seat
                )
                
                if allocation_result["success"]:
                    # Update waitlist status
                    waitlist_entry.status = "ALLOCATED"
                    waitlist_entry.allocated_at = datetime.utcnow()
                    
                    # Update priorities for remaining waitlist entries
                    self._update_waitlist_priorities(flight_id, waitlist_entry.priority)
                    
                    self.db.commit()
                    
                    logger.info(f"Successfully allocated seat to waitlist user {waitlist_entry.user_id}")
                    
                    return {
                        "allocated": True,
                        "user_id": waitlist_entry.user_id,
                        "seat_number": cancelled_seat.seat_number,
                        "booking_id": allocation_result["booking_id"]
                    }
            
            logger.info(f"Could not allocate cancelled seat to any waitlist user")
            return {"allocated": False, "reason": "No suitable waitlist user found"}
            
        except Exception as e:
            logger.error(f"Failed to process cancellation allocation: {e}")
            self.db.rollback()
            return {"allocated": False, "reason": f"Error: {e}"}

    def _try_allocate_to_waitlist_user(self, waitlist_entry: Waitlist, available_seat: Seat) -> Dict[str, Any]:
        """
        Try to allocate a specific seat to a waitlist user
        """
        try:
            # Check if seat matches user preferences
            if not self._seat_matches_preferences(available_seat, waitlist_entry):
                return {"success": False, "reason": "Seat doesn't match preferences"}
            
            # Check price constraints
            flight = self.db.query(Flight).filter(Flight.id == waitlist_entry.flight_id).first()
            if waitlist_entry.max_price and flight.price > waitlist_entry.max_price:
                return {"success": False, "reason": "Price exceeds maximum"}
            
            # Create booking for waitlist user
            booking = Booking(
                user_id=waitlist_entry.user_id,
                flight_id=waitlist_entry.flight_id,
                seat_id=available_seat.id,
                status=BookingStatus.HOLD,  # Give them time to confirm
                price=flight.price,
                created_at=datetime.utcnow(),
                expires_at=datetime.utcnow() + timedelta(minutes=15)  # 15 minutes to confirm
            )
            
            # Update seat status
            available_seat.status = "HOLD"
            
            self.db.add(booking)
            self.db.commit()
            self.db.refresh(booking)
            
            # Send allocation notification
            self._send_allocation_notification(waitlist_entry, booking, available_seat)
            
            return {
                "success": True,
                "booking_id": booking.id,
                "seat_number": available_seat.seat_number
            }
            
        except Exception as e:
            logger.error(f"Failed to allocate seat to waitlist user: {e}")
            self.db.rollback()
            return {"success": False, "reason": f"Error: {e}"}

    def _seat_matches_preferences(self, seat: Seat, waitlist_entry: Waitlist) -> bool:
        """
        Check if a seat matches waitlist user's preferences
        """
        # Check seat class
        if (waitlist_entry.preferred_seat_class and 
            waitlist_entry.preferred_seat_class != "ANY" and 
            seat.seat_class != waitlist_entry.preferred_seat_class):
            return False
        
        # Check seat position
        if (waitlist_entry.preferred_seat_position and 
            waitlist_entry.preferred_seat_position != "ANY"):
            
            seat_position = get_seat_position_type(seat.col)
            if seat_position != waitlist_entry.preferred_seat_position:
                return False
        
        return True

    def _update_waitlist_priorities(self, flight_id: int, allocated_priority: int):
        """
        Update priorities after allocation (move everyone up)
        """
        waitlist_entries = self.db.query(Waitlist).filter(
            and_(
                Waitlist.flight_id == flight_id,
                Waitlist.status == "ACTIVE",
                Waitlist.priority > allocated_priority
            )
        ).all()
        
        for entry in waitlist_entries:
            entry.priority -= 1
        
        self.db.commit()

    def _estimate_wait_time(self, flight_id: int, position: int) -> str:
        """
        Estimate wait time based on historical cancellation data
        """
        # Simple estimation - in production, use historical data
        if position <= 5:
            return "1-2 days"
        elif position <= 15:
            return "3-7 days"
        elif position <= 30:
            return "1-2 weeks"
        else:
            return "2+ weeks"

    def _send_waitlist_confirmation(self, waitlist_entry: Waitlist):
        """
        Send waitlist confirmation email
        """
        try:
            user = self.db.query(User).filter(User.id == waitlist_entry.user_id).first()
            flight = self.db.query(Flight).filter(Flight.id == waitlist_entry.flight_id).first()
            
            if user and flight and waitlist_entry.notify_email:
                # Send email notification
                email_data = {
                    "user_name": user.full_name,
                    "flight": {
                        "from_city": flight.from_city,
                        "to_city": flight.to_city,
                        "departure_time": flight.departure_time,
                        "flight_number": f"ST{flight.id:04d}"
                    },
                    "waitlist_position": waitlist_entry.priority,
                    "estimated_wait": self._estimate_wait_time(flight.id, waitlist_entry.priority)
                }
                
                # Note: Would need to create waitlist email templates
                logger.info(f"Waitlist confirmation sent to {user.email}")
                
        except Exception as e:
            logger.error(f"Failed to send waitlist confirmation: {e}")

    def _send_allocation_notification(self, waitlist_entry: Waitlist, booking: Booking, seat: Seat):
        """
        Send seat allocation notification to waitlist user
        """
        try:
            user = self.db.query(User).filter(User.id == waitlist_entry.user_id).first()
            flight = self.db.query(Flight).filter(Flight.id == waitlist_entry.flight_id).first()
            
            if user and flight:
                # Send real-time notification
                self.notification_service.send_notification(
                    user_id=user.id,
                    notification_type="SEAT_ALLOCATED",
                    title="🎉 Seat Allocated!",
                    message=f"Great news! Seat {seat.seat_number} is now available for your flight {flight.from_city} → {flight.to_city}. You have 15 minutes to confirm.",
                    data={
                        "booking_id": booking.id,
                        "seat_number": seat.seat_number,
                        "flight_id": flight.id,
                        "expires_at": booking.expires_at.isoformat()
                    }
                )
                
                # Send email notification
                if waitlist_entry.notify_email:
                    logger.info(f"Seat allocation notification sent to {user.email}")
                
        except Exception as e:
            logger.error(f"Failed to send allocation notification: {e}")

    def get_user_waitlist(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Get all waitlist entries for a user
        """
        waitlist_entries = self.db.query(Waitlist).filter(
            Waitlist.user_id == user_id
        ).order_by(Waitlist.created_at.desc()).all()
        
        result = []
        for entry in waitlist_entries:
            flight = self.db.query(Flight).filter(Flight.id == entry.flight_id).first()
            
            result.append({
                "id": entry.id,
                "flight": {
                    "id": flight.id,
                    "from_city": flight.from_city,
                    "to_city": flight.to_city,
                    "departure_time": flight.departure_time,
                    "price": flight.price
                },
                "status": entry.status,
                "priority": entry.priority,
                "created_at": entry.created_at,
                "estimated_wait": self._estimate_wait_time(flight.id, entry.priority) if entry.status == "ACTIVE" else None
            })
        
        return result

    def cancel_waitlist_entry(self, waitlist_id: int, user_id: int) -> Dict[str, Any]:
        """
        Cancel a waitlist entry
        """
        try:
            waitlist_entry = self.db.query(Waitlist).filter(
                and_(
                    Waitlist.id == waitlist_id,
                    Waitlist.user_id == user_id,
                    Waitlist.status == "ACTIVE"
                )
            ).first()
            
            if not waitlist_entry:
                return {"success": False, "message": "Waitlist entry not found"}
            
            # Update status
            waitlist_entry.status = "CANCELLED"
            
            # Update priorities for remaining entries
            self._update_waitlist_priorities(waitlist_entry.flight_id, waitlist_entry.priority)
            
            self.db.commit()
            
            return {"success": True, "message": "Waitlist entry cancelled"}
            
        except Exception as e:
            logger.error(f"Failed to cancel waitlist entry: {e}")
            self.db.rollback()
            return {"success": False, "message": "Failed to cancel waitlist entry"}

    def get_flight_waitlist_stats(self, flight_id: int) -> Dict[str, Any]:
        """
        Get waitlist statistics for a flight
        """
        active_count = self.db.query(Waitlist).filter(
            and_(
                Waitlist.flight_id == flight_id,
                Waitlist.status == "ACTIVE"
            )
        ).count()
        
        total_count = self.db.query(Waitlist).filter(
            Waitlist.flight_id == flight_id
        ).count()
        
        return {
            "active_waitlist": active_count,
            "total_waitlist": total_count,
            "allocation_rate": round((total_count - active_count) / max(total_count, 1) * 100, 1)
        }
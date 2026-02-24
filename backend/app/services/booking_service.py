from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from app.dharma.booking_dharma import check_dharma
from app.services.email_service import email_service

from app.models.booking import Booking
from app.models.flight import Flight
from app.models.seat import Seat
from app.constants.booking_status import BookingStatus
from app.domain.booking_state_machine import can_transition

import logging

logger = logging.getLogger(__name__)

HOLD_MINUTES = 10

def confirm_booking(db: Session, booking_id: int, user_id: int, passenger_data: dict = None):
    booking = (
        db.query(Booking)
        .filter(Booking.id == booking_id)
        .first()
    )

    if not booking:
        raise Exception("Booking not found")

    if booking.user_id != user_id:
        raise Exception("Unauthorized confirmation")

    if booking.expires_at and booking.expires_at < datetime.utcnow():
        booking.status = BookingStatus.EXPIRED
        db.commit()
        raise Exception("Booking expired")

    old_status = booking.status
    new_status = BookingStatus.CONFIRMED

    check_dharma(old_status, new_status)

    booking.status = new_status
    booking.expires_at = None
    
    # Add passenger details if provided
    if passenger_data:
        booking.passenger_name = passenger_data.get('passenger_name')
        booking.passenger_email = passenger_data.get('passenger_email')
        booking.passenger_phone = passenger_data.get('passenger_phone')
    
    # Set price from flight if not already set
    if not booking.price:
        flight = db.query(Flight).filter(Flight.id == booking.flight_id).first()
        if flight:
            booking.price = flight.price

    db.commit()
    db.refresh(booking)
    
    # Send booking confirmation email
    try:
        booking_data = {
            'id': booking.id,
            'passenger_name': booking.passenger_name,
            'passenger_email': booking.passenger_email,
            'price': booking.price,
            'created_at': booking.created_at,
            'flight': {
                'from_city': booking.flight.from_city if booking.flight else '',
                'to_city': booking.flight.to_city if booking.flight else '',
                'departure_time': booking.flight.departure_time if booking.flight else None,
                'flight_number': getattr(booking.flight, 'flight_number', f'ST{booking.id}')
            },
            'seat': {
                'seat_number': booking.seat.seat_number if booking.seat else '',
                'seat_class': booking.seat.seat_class if booking.seat else ''
            }
        }
        
        if booking.passenger_email:
            email_service.send_booking_confirmation(booking_data)
            logger.info(f"Booking confirmation email sent for booking {booking.id}")
    except Exception as e:
        logger.error(f"Failed to send booking confirmation email: {e}")
        # Don't fail the booking if email fails
    
    return booking


def hold_seat(db: Session, flight_id: int, seat_id: int, user_id: int):
    booking = (
        db.query(Booking)
        .filter(
            Booking.flight_id == flight_id,
            Booking.seat_id == seat_id
        )
        .first()
    )

    now = datetime.utcnow()
    expires_at = now + timedelta(minutes=HOLD_MINUTES)

    if booking:
        # ❌ seat already held by someone else
        if booking.status == BookingStatus.HOLD and booking.user_id != user_id:
            raise Exception("Seat already held by another user")

        old_status = booking.status
        new_status = BookingStatus.HOLD

        check_dharma(old_status, new_status)

        booking.status = new_status
        booking.user_id = user_id
        booking.expires_at = expires_at

    else:
        # First time seat ever booked
        booking = Booking(
            user_id=user_id,
            flight_id=flight_id,
            seat_id=seat_id,
            status=BookingStatus.HOLD,
            created_at=now,
            expires_at=expires_at
        )
        db.add(booking)

    db.commit()
    db.refresh(booking)
    return booking


def get_user_bookings(db: Session, user_id: int):
    """Get all bookings for a user with flight and seat details"""
    bookings = (
        db.query(Booking)
        .filter(Booking.user_id == user_id)
        .order_by(Booking.created_at.desc())
        .all()
    )
    
    # Load related data
    for booking in bookings:
        booking.flight = db.query(Flight).filter(Flight.id == booking.flight_id).first()
        booking.seat = db.query(Seat).filter(Seat.id == booking.seat_id).first()
    
    return bookings


def get_booking_details(db: Session, booking_id: int, user_id: int = None):
    """Get detailed booking information"""
    query = db.query(Booking).filter(Booking.id == booking_id)
    
    if user_id:
        query = query.filter(Booking.user_id == user_id)
    
    booking = query.first()
    
    if not booking:
        return None
    
    # Load related data
    booking.flight = db.query(Flight).filter(Flight.id == booking.flight_id).first()
    booking.seat = db.query(Seat).filter(Seat.id == booking.seat_id).first()
    
    return booking

def cancel_booking(db: Session, booking_id: int, user_id: int = None, admin_cancel: bool = False):
    """
    Cancel a booking and trigger waitlist allocation
    This is the key function that enables railway-style seat allocation
    """
    try:
        # Get the booking
        query = db.query(Booking).filter(Booking.id == booking_id)
        if user_id and not admin_cancel:
            query = query.filter(Booking.user_id == user_id)
        
        booking = query.first()
        
        if not booking:
            raise Exception("Booking not found")
        
        if booking.status == BookingStatus.CANCELLED:
            raise Exception("Booking already cancelled")
        
        # Store original booking data for waitlist processing
        original_booking = {
            "id": booking.id,
            "flight_id": booking.flight_id,
            "seat_id": booking.seat_id,
            "user_id": booking.user_id,
            "seat": db.query(Seat).filter(Seat.id == booking.seat_id).first()
        }
        
        # Update booking status
        booking.status = BookingStatus.CANCELLED
        booking.expires_at = None
        
        # Free up the seat
        seat = db.query(Seat).filter(Seat.id == booking.seat_id).first()
        if seat:
            seat.status = "AVAILABLE"
        
        db.commit()
        
        logger.info(f"Booking {booking_id} cancelled successfully")
        
        # 🚀 RAILWAY-STYLE WAITLIST PROCESSING
        # This is where the magic happens - automatically allocate to waitlist
        try:
            from app.services.waitlist_service import WaitlistService
            
            waitlist_service = WaitlistService(db)
            allocation_result = waitlist_service.process_cancellation_allocation(booking)
            
            if allocation_result["allocated"]:
                logger.info(f"Seat automatically allocated to waitlist user {allocation_result['user_id']}")
                
                # Send notification about successful allocation
                return {
                    "success": True,
                    "message": "Booking cancelled and seat allocated to waitlist user",
                    "waitlist_allocation": allocation_result
                }
            else:
                logger.info(f"Seat freed but no waitlist allocation: {allocation_result.get('reason', 'Unknown')}")
                
                return {
                    "success": True,
                    "message": "Booking cancelled successfully",
                    "waitlist_allocation": None
                }
                
        except Exception as waitlist_error:
            logger.error(f"Waitlist processing failed: {waitlist_error}")
            # Don't fail the cancellation if waitlist processing fails
            return {
                "success": True,
                "message": "Booking cancelled successfully (waitlist processing failed)",
                "waitlist_allocation": None
            }
        
    except Exception as e:
        logger.error(f"Failed to cancel booking {booking_id}: {e}")
        db.rollback()
        raise Exception(f"Failed to cancel booking: {e}")


def expire_old_bookings(db: Session):
    """
    Expire old bookings and trigger waitlist allocation
    Enhanced to work with waitlist system
    """
    try:
        now = datetime.utcnow()
        
        # Find expired bookings
        expired_bookings = (
            db.query(Booking)
            .filter(
                Booking.status == BookingStatus.HOLD,
                Booking.expires_at <= now
            )
            .all()
        )
        
        for booking in expired_bookings:
            logger.info(f"Expiring booking {booking.id}")
            
            # Store booking data before expiring
            original_booking_data = {
                "id": booking.id,
                "flight_id": booking.flight_id,
                "seat_id": booking.seat_id,
                "seat": db.query(Seat).filter(Seat.id == booking.seat_id).first()
            }
            
            # Expire the booking
            booking.status = BookingStatus.EXPIRED
            
            # Free up the seat
            seat = db.query(Seat).filter(Seat.id == booking.seat_id).first()
            if seat:
                seat.status = "AVAILABLE"
            
            db.commit()
            
            # Try to allocate to waitlist
            try:
                from app.services.waitlist_service import WaitlistService
                
                waitlist_service = WaitlistService(db)
                allocation_result = waitlist_service.process_cancellation_allocation(booking)
                
                if allocation_result["allocated"]:
                    logger.info(f"Expired seat automatically allocated to waitlist user {allocation_result['user_id']}")
                
            except Exception as waitlist_error:
                logger.error(f"Waitlist processing failed for expired booking: {waitlist_error}")
        
        if expired_bookings:
            logger.info(f"Expired {len(expired_bookings)} bookings")
        
    except Exception as e:
        logger.error(f"Failed to expire bookings: {e}")
        db.rollback()
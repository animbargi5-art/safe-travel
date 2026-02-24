"""
Email notification routes for manual sending and testing
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from app.database_dep import get_db
from app.routes.auth import get_current_user
from app.services.email_service import email_service
from app.models.booking import Booking
from app.models.payment import Payment
from app.models.user import User

import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/email", tags=["Email"])

@router.post("/send-booking-confirmation/{booking_id}")
def send_booking_confirmation_manual(
    booking_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Manually send booking confirmation email"""
    
    # Get booking details
    booking = db.query(Booking).filter(
        Booking.id == booking_id,
        Booking.user_id == current_user.id
    ).first()
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    if not booking.passenger_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No email address associated with booking"
        )
    
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
        
        success = email_service.send_booking_confirmation(booking_data)
        
        if success:
            return {"message": "Booking confirmation email sent successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send email"
            )
            
    except Exception as e:
        logger.error(f"Error sending booking confirmation email: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send email"
        )

@router.post("/send-payment-receipt/{payment_id}")
def send_payment_receipt_manual(
    payment_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Manually send payment receipt email"""
    
    # Get payment details
    payment = db.query(Payment).filter(
        Payment.id == payment_id,
        Payment.user_id == current_user.id
    ).first()
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    # Get booking details
    booking = db.query(Booking).filter(Booking.id == payment.booking_id).first()
    
    if not booking or not booking.passenger_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No email address associated with booking"
        )
    
    try:
        payment_data = {
            'id': payment.id,
            'amount': payment.amount,
            'currency': payment.currency,
            'completed_at': payment.completed_at
        }
        
        booking_data = {
            'id': booking.id,
            'passenger_name': booking.passenger_name,
            'passenger_email': booking.passenger_email,
            'flight': {
                'from_city': booking.flight.from_city if booking.flight else '',
                'to_city': booking.flight.to_city if booking.flight else '',
                'flight_number': getattr(booking.flight, 'flight_number', f'ST{booking.id}')
            },
            'seat': {
                'seat_number': booking.seat.seat_number if booking.seat else '',
                'seat_class': booking.seat.seat_class if booking.seat else ''
            }
        }
        
        success = email_service.send_payment_receipt(payment_data, booking_data)
        
        if success:
            return {"message": "Payment receipt email sent successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send email"
            )
            
    except Exception as e:
        logger.error(f"Error sending payment receipt email: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send email"
        )

@router.post("/send-booking-reminder/{booking_id}")
def send_booking_reminder_manual(
    booking_id: int,
    hours_before: Optional[int] = 24,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Manually send booking reminder email"""
    
    # Get booking details
    booking = db.query(Booking).filter(
        Booking.id == booking_id,
        Booking.user_id == current_user.id
    ).first()
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    if not booking.passenger_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No email address associated with booking"
        )
    
    try:
        booking_data = {
            'id': booking.id,
            'passenger_name': booking.passenger_name,
            'passenger_email': booking.passenger_email,
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
        
        success = email_service.send_booking_reminder(booking_data, hours_before)
        
        if success:
            return {"message": f"Booking reminder email sent successfully ({hours_before}h before departure)"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send email"
            )
            
    except Exception as e:
        logger.error(f"Error sending booking reminder email: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send email"
        )

@router.post("/send-welcome")
def send_welcome_email_manual(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Manually send welcome email to current user"""
    
    try:
        user_data = {
            'email': current_user.email,
            'username': current_user.username,
            'full_name': current_user.full_name
        }
        
        success = email_service.send_welcome_email(user_data)
        
        if success:
            return {"message": "Welcome email sent successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send email"
            )
            
    except Exception as e:
        logger.error(f"Error sending welcome email: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send email"
        )

@router.post("/test-email")
def test_email_service(
    current_user = Depends(get_current_user)
):
    """Test email service with a simple test email"""
    
    try:
        success = email_service.send_email(
            to_email=current_user.email,
            subject="🧪 Safe Travel - Email Service Test",
            html_content="""
            <div style="font-family: Arial, sans-serif; padding: 20px;">
                <h2 style="color: #2563eb;">Email Service Test</h2>
                <p>Hello {name},</p>
                <p>This is a test email to verify that the Safe Travel email service is working correctly.</p>
                <p style="color: #059669;"><strong>✅ Email service is functioning properly!</strong></p>
                <p>Best regards,<br>Safe Travel Team</p>
            </div>
            """.format(name=current_user.full_name or current_user.username),
            text_content=f"""
Safe Travel - Email Service Test

Hello {current_user.full_name or current_user.username},

This is a test email to verify that the Safe Travel email service is working correctly.

✅ Email service is functioning properly!

Best regards,
Safe Travel Team
            """
        )
        
        if success:
            return {"message": "Test email sent successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send test email"
            )
            
    except Exception as e:
        logger.error(f"Error sending test email: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send test email"
        )
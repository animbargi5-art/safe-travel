"""
Payment service for handling booking payments
Integrates with Stripe for secure payment processing
Enhanced with security, analytics, and fraud detection
"""

import stripe
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Request
from datetime import datetime

from app.core.config import settings
from app.models.booking import Booking
from app.models.payment import Payment
from app.constants.booking_status import BookingStatus
from app.constants.payment_status import PaymentStatus
from app.services.booking_service import confirm_booking
from app.services.email_service import email_service
from app.services.payment_security import PaymentSecurityService
from app.services.payment_analytics import PaymentAnalytics
from app.dharma.booking_dharma import check_dharma

import logging

logger = logging.getLogger(__name__)

# Initialize Stripe
stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', 'sk_test_...')

class PaymentError(Exception):
    """Custom payment error"""
    pass

def create_payment_intent(
    db: Session,
    booking_id: int,
    user_id: int,
    return_url: str = None,
    request: Request = None
) -> Dict[str, Any]:
    """
    Create a Stripe payment intent for a booking with enhanced security
    
    Args:
        db: Database session
        booking_id: ID of the booking to pay for
        user_id: ID of the user making payment
        return_url: URL to redirect after payment
        request: FastAPI request object for security analysis
    
    Returns:
        Payment intent data including client_secret
    """
    
    # Initialize security service
    security_service = PaymentSecurityService(db)
    
    # Get booking details
    booking = db.query(Booking).filter(
        Booking.id == booking_id,
        Booking.user_id == user_id
    ).first()
    
    if not booking:
        security_service.log_security_event(
            'payment_attempt_invalid_booking',
            user_id=user_id,
            details={'booking_id': booking_id},
            severity='WARNING'
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    if booking.status != BookingStatus.HOLD:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Booking is not in a payable state"
        )
    
    # Check if booking has expired
    if booking.expires_at and booking.expires_at < datetime.utcnow():
        booking.status = BookingStatus.EXPIRED
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Booking has expired"
        )
    
    # Get price (from booking or flight)
    amount = booking.price
    if not amount:
        if booking.flight:
            amount = booking.flight.price
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Booking price not available"
            )
    
    # Enhanced security check
    ip_address = None
    user_agent = None
    if request:
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get('user-agent')
    
    risk_assessment = security_service.calculate_risk_score(
        user_id=user_id,
        amount=float(amount),
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    # Log security assessment
    security_service.log_security_event(
        'payment_risk_assessment',
        user_id=user_id,
        details={
            'booking_id': booking_id,
            'amount': float(amount),
            'risk_score': risk_assessment['risk_score'],
            'risk_level': risk_assessment['risk_level'],
            'recommendation': risk_assessment['recommendation']
        },
        severity='INFO' if risk_assessment['risk_level'] == 'LOW' else 'WARNING'
    )
    
    # Block high-risk payments
    if risk_assessment['recommendation'] == 'BLOCK':
        security_service.log_security_event(
            'payment_blocked_high_risk',
            user_id=user_id,
            details={
                'booking_id': booking_id,
                'risk_factors': risk_assessment['factors']
            },
            severity='ERROR'
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Payment blocked due to security concerns. Please contact support."
        )
    
    # Convert to cents for Stripe
    amount_cents = int(amount * 100)
    
    try:
        # Create Stripe payment intent
        intent = stripe.PaymentIntent.create(
            amount=amount_cents,
            currency='usd',  # In production, make this configurable
            metadata={
                'booking_id': booking_id,
                'user_id': user_id,
                'flight_from': booking.flight.from_city if booking.flight else '',
                'flight_to': booking.flight.to_city if booking.flight else '',
                'seat_number': booking.seat.seat_number if booking.seat else '',
                'risk_score': risk_assessment['risk_score'],
                'risk_level': risk_assessment['risk_level']
            },
            description=f"Flight booking #{booking_id}",
            return_url=return_url
        )
        
        # Create payment record
        payment = Payment(
            booking_id=booking_id,
            user_id=user_id,
            stripe_payment_intent_id=intent.id,
            amount=amount,
            currency='USD',
            status=PaymentStatus.PENDING,
            created_at=datetime.utcnow()
        )
        
        db.add(payment)
        db.commit()
        db.refresh(payment)
        
        # Log successful payment intent creation
        security_service.log_security_event(
            'payment_intent_created',
            user_id=user_id,
            payment_id=payment.id,
            details={
                'booking_id': booking_id,
                'amount': float(amount),
                'stripe_intent_id': intent.id
            }
        )
        
        logger.info(f"Created payment intent {intent.id} for booking {booking_id}")
        
        return {
            'payment_intent_id': intent.id,
            'client_secret': intent.client_secret,
            'amount': amount,
            'currency': 'USD',
            'payment_id': payment.id,
            'risk_assessment': {
                'risk_level': risk_assessment['risk_level'],
                'requires_review': risk_assessment['recommendation'] == 'REVIEW'
            }
        }
        
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error creating payment intent: {e}")
        security_service.log_security_event(
            'stripe_error',
            user_id=user_id,
            details={'error': str(e), 'booking_id': booking_id},
            severity='ERROR'
        )
        raise PaymentError(f"Payment processing error: {str(e)}")
    except Exception as e:
        logger.error(f"Error creating payment intent: {e}")
        raise PaymentError("Failed to create payment")

def confirm_payment(
    db: Session,
    payment_intent_id: str,
    passenger_data: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Confirm a payment and complete the booking with real-time notifications
    
    Args:
        db: Database session
        payment_intent_id: Stripe payment intent ID
        passenger_data: Passenger details for booking
    
    Returns:
        Confirmed booking and payment data
    """
    
    # Initialize notification service
    from app.services.notification_service import NotificationService
    notification_service = NotificationService(db)
    
    # Get payment record
    payment = db.query(Payment).filter(
        Payment.stripe_payment_intent_id == payment_intent_id
    ).first()
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    try:
        # Retrieve payment intent from Stripe
        intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        
        if intent.status == 'succeeded':
            # Update payment status
            payment.status = PaymentStatus.COMPLETED
            payment.stripe_charge_id = intent.latest_charge
            payment.completed_at = datetime.utcnow()
            
            # Confirm the booking
            booking = confirm_booking(
                db=db,
                booking_id=payment.booking_id,
                user_id=payment.user_id,
                passenger_data=passenger_data
            )
            
            db.commit()
            
            logger.info(f"Payment {payment_intent_id} confirmed for booking {payment.booking_id}")
            
            # Send real-time notifications
            try:
                import asyncio
                
                # Payment completion notification
                asyncio.create_task(notification_service.notify_payment_completed(
                    payment_id=payment.id,
                    user_id=payment.user_id
                ))
                
                # Booking confirmation notification
                asyncio.create_task(notification_service.notify_booking_confirmed(
                    booking_id=payment.booking_id,
                    user_id=payment.user_id
                ))
            except Exception as e:
                logger.error(f"Failed to send real-time notifications: {e}")
                # Don't fail the payment if notifications fail
            
            # Send payment receipt email
            try:
                # Get booking details for email
                booking = db.query(Booking).filter(Booking.id == payment.booking_id).first()
                if booking and booking.passenger_email:
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
                    
                    email_service.send_payment_receipt(payment_data, booking_data)
                    logger.info(f"Payment receipt email sent for payment {payment.id}")
            except Exception as e:
                logger.error(f"Failed to send payment receipt email: {e}")
                # Don't fail the payment if email fails
            
            return {
                'payment': {
                    'id': payment.id,
                    'status': payment.status,
                    'amount': payment.amount,
                    'currency': payment.currency
                },
                'booking': booking
            }
            
        elif intent.status == 'requires_payment_method':
            payment.status = PaymentStatus.FAILED
            db.commit()
            
            # Send payment failure notification
            try:
                import asyncio
                asyncio.create_task(notification_service.notify_payment_failed(
                    payment_id=payment.id,
                    user_id=payment.user_id,
                    reason="Invalid payment method"
                ))
            except Exception as e:
                logger.error(f"Failed to send payment failure notification: {e}")
            
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment failed - invalid payment method"
            )
        
        elif intent.status == 'canceled':
            payment.status = PaymentStatus.CANCELLED
            db.commit()
            
            # Send payment cancellation notification
            try:
                import asyncio
                asyncio.create_task(notification_service.notify_payment_failed(
                    payment_id=payment.id,
                    user_id=payment.user_id,
                    reason="Payment was cancelled"
                ))
            except Exception as e:
                logger.error(f"Failed to send payment cancellation notification: {e}")
            
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment was cancelled"
            )
        
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Payment in unexpected state: {intent.status}"
            )
            
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error confirming payment: {e}")
        payment.status = PaymentStatus.FAILED
        db.commit()
        
        # Send payment failure notification
        try:
            import asyncio
            asyncio.create_task(notification_service.notify_payment_failed(
                payment_id=payment.id,
                user_id=payment.user_id,
                reason=f"Payment processing error: {str(e)}"
            ))
        except Exception as e:
            logger.error(f"Failed to send payment failure notification: {e}")
        
        raise PaymentError(f"Payment confirmation error: {str(e)}")

def refund_payment(
    db: Session,
    payment_id: int,
    user_id: int,
    amount: Optional[float] = None,
    reason: str = "requested_by_customer"
) -> Dict[str, Any]:
    """
    Process a refund for a payment
    
    Args:
        db: Database session
        payment_id: ID of the payment to refund
        user_id: ID of the user requesting refund
        amount: Partial refund amount (None for full refund)
        reason: Reason for refund
    
    Returns:
        Refund details
    """
    
    # Get payment record
    payment = db.query(Payment).filter(
        Payment.id == payment_id,
        Payment.user_id == user_id
    ).first()
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    if payment.status != PaymentStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment cannot be refunded"
        )
    
    try:
        # Calculate refund amount
        refund_amount = amount if amount else payment.amount
        refund_amount_cents = int(refund_amount * 100)
        
        # Create Stripe refund
        refund = stripe.Refund.create(
            payment_intent=payment.stripe_payment_intent_id,
            amount=refund_amount_cents,
            reason=reason,
            metadata={
                'payment_id': payment_id,
                'user_id': user_id
            }
        )
        
        # Update payment status
        if refund_amount >= payment.amount:
            payment.status = PaymentStatus.REFUNDED
        else:
            payment.status = PaymentStatus.PARTIALLY_REFUNDED
        
        payment.refunded_amount = (payment.refunded_amount or 0) + refund_amount
        payment.refunded_at = datetime.utcnow()
        
        db.commit()
        
        logger.info(f"Refunded ${refund_amount} for payment {payment_id}")
        
        return {
            'refund_id': refund.id,
            'amount': refund_amount,
            'status': refund.status,
            'payment_status': payment.status
        }
        
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error processing refund: {e}")
        raise PaymentError(f"Refund processing error: {str(e)}")

def get_payment_status(db: Session, payment_intent_id: str) -> Dict[str, Any]:
    """Get current payment status"""
    
    payment = db.query(Payment).filter(
        Payment.stripe_payment_intent_id == payment_intent_id
    ).first()
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    try:
        # Get latest status from Stripe
        intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        
        return {
            'payment_id': payment.id,
            'booking_id': payment.booking_id,
            'amount': payment.amount,
            'currency': payment.currency,
            'status': payment.status,
            'stripe_status': intent.status,
            'created_at': payment.created_at,
            'completed_at': payment.completed_at
        }
        
    except stripe.error.StripeError as e:
        logger.error(f"Error retrieving payment status: {e}")
        raise PaymentError("Failed to retrieve payment status")

def get_payment_analytics(db: Session, days: int = 30) -> Dict[str, Any]:
    """Get comprehensive payment analytics"""
    
    analytics = PaymentAnalytics(db)
    
    return {
        'revenue_summary': analytics.get_revenue_summary(days),
        'daily_revenue': analytics.get_daily_revenue(days),
        'payment_methods': analytics.get_payment_methods_breakdown(days),
        'top_routes': analytics.get_top_routes_by_revenue(days),
        'refund_analysis': analytics.get_refund_analysis(days)
    }

def get_user_payment_analytics(db: Session, user_id: int) -> Dict[str, Any]:
    """Get payment analytics for a specific user"""
    
    analytics = PaymentAnalytics(db)
    security_service = PaymentSecurityService(db)
    
    return {
        'payment_stats': analytics.get_user_payment_stats(user_id),
        'velocity_check': security_service.get_payment_velocity_check(user_id)
    }

def detect_payment_fraud(db: Session, days: int = 7) -> List[Dict[str, Any]]:
    """Detect potential payment fraud"""
    
    analytics = PaymentAnalytics(db)
    return analytics.detect_payment_anomalies(days)

def process_webhook(db: Session, payload: bytes, signature: str) -> Dict[str, Any]:
    """Process Stripe webhook with security verification"""
    
    security_service = PaymentSecurityService(db)
    
    # Verify webhook signature
    if not security_service.verify_webhook_signature(payload, signature):
        security_service.log_security_event(
            'webhook_signature_verification_failed',
            details={'signature': signature},
            severity='ERROR'
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid webhook signature"
        )
    
    try:
        import json
        event = json.loads(payload.decode('utf-8'))
        
        # Log webhook received
        security_service.log_security_event(
            'webhook_received',
            details={
                'event_type': event.get('type'),
                'event_id': event.get('id')
            }
        )
        
        # Handle different event types
        if event['type'] == 'payment_intent.succeeded':
            return _handle_payment_succeeded(db, event['data']['object'])
        elif event['type'] == 'payment_intent.payment_failed':
            return _handle_payment_failed(db, event['data']['object'])
        elif event['type'] == 'charge.dispute.created':
            return _handle_chargeback(db, event['data']['object'])
        else:
            logger.info(f"Unhandled webhook event type: {event['type']}")
            return {'status': 'ignored', 'event_type': event['type']}
            
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        security_service.log_security_event(
            'webhook_processing_error',
            details={'error': str(e)},
            severity='ERROR'
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Webhook processing failed"
        )

def _handle_payment_succeeded(db: Session, payment_intent: Dict[str, Any]) -> Dict[str, Any]:
    """Handle successful payment webhook"""
    
    payment = db.query(Payment).filter(
        Payment.stripe_payment_intent_id == payment_intent['id']
    ).first()
    
    if payment and payment.status == PaymentStatus.PENDING:
        payment.status = PaymentStatus.COMPLETED
        payment.completed_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"Payment {payment.id} marked as completed via webhook")
        
        return {'status': 'processed', 'payment_id': payment.id}
    
    return {'status': 'no_action_needed'}

def _handle_payment_failed(db: Session, payment_intent: Dict[str, Any]) -> Dict[str, Any]:
    """Handle failed payment webhook"""
    
    payment = db.query(Payment).filter(
        Payment.stripe_payment_intent_id == payment_intent['id']
    ).first()
    
    if payment and payment.status == PaymentStatus.PENDING:
        payment.status = PaymentStatus.FAILED
        db.commit()
        
        logger.info(f"Payment {payment.id} marked as failed via webhook")
        
        return {'status': 'processed', 'payment_id': payment.id}
    
    return {'status': 'no_action_needed'}

def _handle_chargeback(db: Session, dispute: Dict[str, Any]) -> Dict[str, Any]:
    """Handle chargeback/dispute webhook"""
    
    charge_id = dispute.get('charge')
    if not charge_id:
        return {'status': 'no_charge_id'}
    
    # Find payment by charge ID
    payment = db.query(Payment).filter(
        Payment.stripe_charge_id == charge_id
    ).first()
    
    if payment:
        # Log chargeback for investigation
        security_service = PaymentSecurityService(db)
        security_service.log_security_event(
            'chargeback_received',
            user_id=payment.user_id,
            payment_id=payment.id,
            details={
                'dispute_id': dispute.get('id'),
                'reason': dispute.get('reason'),
                'amount': dispute.get('amount'),
                'charge_id': charge_id
            },
            severity='ERROR'
        )
        
        logger.warning(f"Chargeback received for payment {payment.id}")
        
        return {'status': 'logged', 'payment_id': payment.id}
    
    return {'status': 'payment_not_found'}
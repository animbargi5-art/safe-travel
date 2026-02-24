from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.database_dep import get_db
from app.routes.auth import get_current_user
from app.schemas.payment import (
    PaymentIntentCreate,
    PaymentIntentResponse,
    PaymentConfirm,
    PaymentResponse,
    RefundRequest,
    RefundResponse
)
from app.services.payment_service import (
    create_payment_intent,
    confirm_payment,
    refund_payment,
    get_payment_status,
    get_payment_analytics,
    get_user_payment_analytics,
    detect_payment_fraud,
    process_webhook,
    PaymentError
)

router = APIRouter(prefix="/payment", tags=["Payment"])

@router.post("/create-intent", response_model=PaymentIntentResponse)
def create_payment_intent_api(
    payment_data: PaymentIntentCreate,
    request: Request,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a payment intent for a booking with enhanced security"""
    try:
        intent_data = create_payment_intent(
            db=db,
            booking_id=payment_data.booking_id,
            user_id=current_user.id,
            return_url=payment_data.return_url,
            request=request
        )
        return intent_data
    except PaymentError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/confirm")
def confirm_payment_api(
    payment_data: PaymentConfirm,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Confirm a payment and complete booking"""
    try:
        passenger_data = None
        if payment_data.passenger_name:
            passenger_data = {
                'passenger_name': payment_data.passenger_name,
                'passenger_email': payment_data.passenger_email,
                'passenger_phone': payment_data.passenger_phone
            }
        
        result = confirm_payment(
            db=db,
            payment_intent_id=payment_data.payment_intent_id,
            passenger_data=passenger_data
        )
        return result
    except PaymentError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/status/{payment_intent_id}")
def get_payment_status_api(
    payment_intent_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get payment status"""
    try:
        status_data = get_payment_status(db, payment_intent_id)
        
        # Verify user owns this payment
        if status_data.get('user_id') != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        return status_data
    except PaymentError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/refund/{payment_id}", response_model=RefundResponse)
def refund_payment_api(
    payment_id: int,
    refund_data: RefundRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Process a refund for a payment"""
    try:
        refund_result = refund_payment(
            db=db,
            payment_id=payment_id,
            user_id=current_user.id,
            amount=refund_data.amount,
            reason=refund_data.reason
        )
        return refund_result
    except PaymentError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/my-payments", response_model=list[PaymentResponse])
def get_my_payments(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's payment history"""
    from app.models.payment import Payment
    
    payments = db.query(Payment).filter(
        Payment.user_id == current_user.id
    ).order_by(Payment.created_at.desc()).all()
    
    return payments

@router.get("/analytics")
def get_payment_analytics_api(
    days: int = 30,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get payment analytics (admin only for now)"""
    # In production, add proper admin role checking
    try:
        analytics = get_payment_analytics(db, days)
        return analytics
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analytics error: {str(e)}"
        )

@router.get("/my-analytics")
def get_my_payment_analytics(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's personal payment analytics"""
    try:
        analytics = get_user_payment_analytics(db, current_user.id)
        return analytics
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analytics error: {str(e)}"
        )

@router.get("/fraud-detection")
def get_fraud_detection(
    days: int = 7,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get fraud detection results (admin only)"""
    # In production, add proper admin role checking
    try:
        anomalies = detect_payment_fraud(db, days)
        return {
            'anomalies': anomalies,
            'total_anomalies': len(anomalies),
            'high_risk_count': len([a for a in anomalies if a['risk_score'] >= 80]),
            'medium_risk_count': len([a for a in anomalies if 50 <= a['risk_score'] < 80])
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Fraud detection error: {str(e)}"
        )

@router.post("/webhook")
def handle_stripe_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """Handle Stripe webhooks"""
    try:
        # Get raw body and signature
        body = request.body()
        signature = request.headers.get('stripe-signature', '')
        
        result = process_webhook(db, body, signature)
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Webhook error: {str(e)}"
        )
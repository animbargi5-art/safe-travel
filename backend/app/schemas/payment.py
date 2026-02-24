from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict, Any

class PaymentIntentCreate(BaseModel):
    booking_id: int
    return_url: Optional[str] = None

class PaymentIntentResponse(BaseModel):
    payment_intent_id: str
    client_secret: str
    amount: float
    currency: str
    payment_id: int
    risk_assessment: Optional[Dict[str, Any]] = None

class PaymentConfirm(BaseModel):
    payment_intent_id: str
    passenger_name: Optional[str] = None
    passenger_email: Optional[str] = None
    passenger_phone: Optional[str] = None

class PaymentResponse(BaseModel):
    id: int
    booking_id: int
    user_id: int
    stripe_payment_intent_id: str
    stripe_charge_id: Optional[str]
    amount: float
    currency: str
    status: str
    refunded_amount: Optional[float]
    created_at: datetime
    completed_at: Optional[datetime]
    refunded_at: Optional[datetime]

    class Config:
        from_attributes = True

class RefundRequest(BaseModel):
    amount: Optional[float] = None  # None for full refund
    reason: Optional[str] = "requested_by_customer"

class RefundResponse(BaseModel):
    refund_id: str
    amount: float
    status: str
    payment_status: str

# New schemas for enhanced features

class PaymentAnalyticsResponse(BaseModel):
    revenue_summary: Dict[str, Any]
    daily_revenue: List[Dict[str, Any]]
    payment_methods: Dict[str, Any]
    top_routes: List[Dict[str, Any]]
    refund_analysis: Dict[str, Any]

class UserPaymentAnalyticsResponse(BaseModel):
    payment_stats: Dict[str, Any]
    velocity_check: Dict[str, Any]

class FraudDetectionResponse(BaseModel):
    anomalies: List[Dict[str, Any]]
    total_anomalies: int
    high_risk_count: int
    medium_risk_count: int

class RiskAssessmentResponse(BaseModel):
    risk_score: int
    risk_level: str
    factors: List[str]
    recommendation: str
    details: Dict[str, Any]

class SecurityEventResponse(BaseModel):
    timestamp: datetime
    event_type: str
    user_id: Optional[int]
    payment_id: Optional[int]
    severity: str
    details: Dict[str, Any]

class WebhookResponse(BaseModel):
    status: str
    event_type: Optional[str] = None
    payment_id: Optional[int] = None
    message: Optional[str] = None
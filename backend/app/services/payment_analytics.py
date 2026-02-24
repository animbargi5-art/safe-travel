"""
Payment Analytics Service
Provides insights and reporting for payment data
"""

from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from datetime import datetime, timedelta
from decimal import Decimal

from app.models.payment import Payment
from app.models.booking import Booking
from app.models.flight import Flight
from app.models.user import User
from app.constants.payment_status import PaymentStatus
from app.constants.booking_status import BookingStatus

import logging

logger = logging.getLogger(__name__)

class PaymentAnalytics:
    """Payment analytics and reporting service"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_revenue_summary(self, days: int = 30) -> Dict[str, Any]:
        """Get revenue summary for the specified period"""
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Total revenue
        total_revenue = self.db.query(
            func.sum(Payment.amount)
        ).filter(
            and_(
                Payment.status == PaymentStatus.COMPLETED,
                Payment.completed_at >= start_date,
                Payment.completed_at <= end_date
            )
        ).scalar() or 0
        
        # Transaction count
        transaction_count = self.db.query(Payment).filter(
            and_(
                Payment.status == PaymentStatus.COMPLETED,
                Payment.completed_at >= start_date,
                Payment.completed_at <= end_date
            )
        ).count()
        
        # Average transaction value
        avg_transaction = float(total_revenue) / transaction_count if transaction_count > 0 else 0
        
        # Refunded amount
        refunded_amount = self.db.query(
            func.sum(Payment.refunded_amount)
        ).filter(
            and_(
                Payment.refunded_amount.isnot(None),
                Payment.refunded_at >= start_date,
                Payment.refunded_at <= end_date
            )
        ).scalar() or 0
        
        # Failed payments
        failed_count = self.db.query(Payment).filter(
            and_(
                Payment.status == PaymentStatus.FAILED,
                Payment.created_at >= start_date,
                Payment.created_at <= end_date
            )
        ).count()
        
        return {
            'period_days': days,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'total_revenue': float(total_revenue),
            'transaction_count': transaction_count,
            'average_transaction_value': round(avg_transaction, 2),
            'refunded_amount': float(refunded_amount),
            'failed_payments': failed_count,
            'success_rate': round((transaction_count / (transaction_count + failed_count)) * 100, 2) if (transaction_count + failed_count) > 0 else 0
        }
    
    def get_daily_revenue(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get daily revenue breakdown"""
        
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=days)
        
        # Query daily revenue
        daily_data = self.db.query(
            func.date(Payment.completed_at).label('date'),
            func.sum(Payment.amount).label('revenue'),
            func.count(Payment.id).label('transactions')
        ).filter(
            and_(
                Payment.status == PaymentStatus.COMPLETED,
                func.date(Payment.completed_at) >= start_date,
                func.date(Payment.completed_at) <= end_date
            )
        ).group_by(
            func.date(Payment.completed_at)
        ).order_by(
            func.date(Payment.completed_at)
        ).all()
        
        # Convert to list of dictionaries
        result = []
        for row in daily_data:
            result.append({
                'date': row.date.isoformat(),
                'revenue': float(row.revenue),
                'transactions': row.transactions
            })
        
        return result
    
    def get_payment_methods_breakdown(self, days: int = 30) -> Dict[str, Any]:
        """Get breakdown of payment methods used"""
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # For now, we only support card payments via Stripe
        # In the future, this could include other payment methods
        
        card_payments = self.db.query(Payment).filter(
            and_(
                Payment.status == PaymentStatus.COMPLETED,
                Payment.completed_at >= start_date,
                Payment.completed_at <= end_date
            )
        ).count()
        
        return {
            'card_payments': card_payments,
            'total_payments': card_payments,
            'methods': {
                'card': {
                    'count': card_payments,
                    'percentage': 100.0 if card_payments > 0 else 0.0
                }
            }
        }
    
    def get_top_routes_by_revenue(self, days: int = 30, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top flight routes by revenue"""
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        route_data = self.db.query(
            Flight.from_city,
            Flight.to_city,
            func.sum(Payment.amount).label('revenue'),
            func.count(Payment.id).label('bookings')
        ).join(
            Booking, Payment.booking_id == Booking.id
        ).join(
            Flight, Booking.flight_id == Flight.id
        ).filter(
            and_(
                Payment.status == PaymentStatus.COMPLETED,
                Payment.completed_at >= start_date,
                Payment.completed_at <= end_date
            )
        ).group_by(
            Flight.from_city,
            Flight.to_city
        ).order_by(
            func.sum(Payment.amount).desc()
        ).limit(limit).all()
        
        result = []
        for row in route_data:
            result.append({
                'route': f"{row.from_city} → {row.to_city}",
                'from_city': row.from_city,
                'to_city': row.to_city,
                'revenue': float(row.revenue),
                'bookings': row.bookings
            })
        
        return result
    
    def get_user_payment_stats(self, user_id: int) -> Dict[str, Any]:
        """Get payment statistics for a specific user"""
        
        # Total spent
        total_spent = self.db.query(
            func.sum(Payment.amount)
        ).filter(
            and_(
                Payment.user_id == user_id,
                Payment.status == PaymentStatus.COMPLETED
            )
        ).scalar() or 0
        
        # Payment count
        payment_count = self.db.query(Payment).filter(
            and_(
                Payment.user_id == user_id,
                Payment.status == PaymentStatus.COMPLETED
            )
        ).count()
        
        # Average payment
        avg_payment = float(total_spent) / payment_count if payment_count > 0 else 0
        
        # First payment date
        first_payment = self.db.query(Payment).filter(
            and_(
                Payment.user_id == user_id,
                Payment.status == PaymentStatus.COMPLETED
            )
        ).order_by(Payment.completed_at.asc()).first()
        
        # Last payment date
        last_payment = self.db.query(Payment).filter(
            and_(
                Payment.user_id == user_id,
                Payment.status == PaymentStatus.COMPLETED
            )
        ).order_by(Payment.completed_at.desc()).first()
        
        return {
            'user_id': user_id,
            'total_spent': float(total_spent),
            'payment_count': payment_count,
            'average_payment': round(avg_payment, 2),
            'first_payment_date': first_payment.completed_at.isoformat() if first_payment else None,
            'last_payment_date': last_payment.completed_at.isoformat() if last_payment else None
        }
    
    def get_refund_analysis(self, days: int = 30) -> Dict[str, Any]:
        """Get refund analysis"""
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Total refunds
        total_refunded = self.db.query(
            func.sum(Payment.refunded_amount)
        ).filter(
            and_(
                Payment.refunded_amount.isnot(None),
                Payment.refunded_at >= start_date,
                Payment.refunded_at <= end_date
            )
        ).scalar() or 0
        
        # Refund count
        refund_count = self.db.query(Payment).filter(
            and_(
                or_(
                    Payment.status == PaymentStatus.REFUNDED,
                    Payment.status == PaymentStatus.PARTIALLY_REFUNDED
                ),
                Payment.refunded_at >= start_date,
                Payment.refunded_at <= end_date
            )
        ).count()
        
        # Total completed payments in period
        total_payments = self.db.query(
            func.sum(Payment.amount)
        ).filter(
            and_(
                Payment.status == PaymentStatus.COMPLETED,
                Payment.completed_at >= start_date,
                Payment.completed_at <= end_date
            )
        ).scalar() or 0
        
        # Refund rate
        refund_rate = (float(total_refunded) / float(total_payments)) * 100 if total_payments > 0 else 0
        
        return {
            'period_days': days,
            'total_refunded': float(total_refunded),
            'refund_count': refund_count,
            'refund_rate_percentage': round(refund_rate, 2),
            'average_refund': round(float(total_refunded) / refund_count, 2) if refund_count > 0 else 0
        }
    
    def detect_payment_anomalies(self, days: int = 7) -> List[Dict[str, Any]]:
        """Detect unusual payment patterns that might indicate fraud"""
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        anomalies = []
        
        # Check for users with unusually high payment frequency
        high_frequency_users = self.db.query(
            Payment.user_id,
            func.count(Payment.id).label('payment_count'),
            func.sum(Payment.amount).label('total_amount')
        ).filter(
            and_(
                Payment.created_at >= start_date,
                Payment.created_at <= end_date
            )
        ).group_by(
            Payment.user_id
        ).having(
            func.count(Payment.id) > 10  # More than 10 payments in the period
        ).all()
        
        for user_data in high_frequency_users:
            user = self.db.query(User).filter(User.id == user_data.user_id).first()
            anomalies.append({
                'type': 'high_frequency',
                'user_id': user_data.user_id,
                'user_email': user.email if user else 'Unknown',
                'payment_count': user_data.payment_count,
                'total_amount': float(user_data.total_amount),
                'risk_score': min(user_data.payment_count * 10, 100),  # Simple risk scoring
                'description': f'User made {user_data.payment_count} payments in {days} days'
            })
        
        # Check for unusually large payments
        avg_payment = self.db.query(
            func.avg(Payment.amount)
        ).filter(
            Payment.status == PaymentStatus.COMPLETED
        ).scalar() or 0
        
        large_payments = self.db.query(Payment).filter(
            and_(
                Payment.amount > avg_payment * 5,  # 5x average
                Payment.created_at >= start_date,
                Payment.created_at <= end_date
            )
        ).all()
        
        for payment in large_payments:
            user = self.db.query(User).filter(User.id == payment.user_id).first()
            anomalies.append({
                'type': 'large_payment',
                'user_id': payment.user_id,
                'user_email': user.email if user else 'Unknown',
                'payment_id': payment.id,
                'amount': float(payment.amount),
                'average_amount': float(avg_payment),
                'risk_score': min(int((payment.amount / avg_payment) * 20), 100),
                'description': f'Payment of ${payment.amount} is {payment.amount / avg_payment:.1f}x the average'
            })
        
        return sorted(anomalies, key=lambda x: x['risk_score'], reverse=True)
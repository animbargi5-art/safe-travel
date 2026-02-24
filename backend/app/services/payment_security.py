"""
Payment Security Service
Enhanced security features for payment processing
"""

import hashlib
import hmac
import time
from typing import Dict, List, Any, Optional, Tuple
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from decimal import Decimal
import ipaddress
import re

from app.models.payment import Payment
from app.models.user import User
from app.core.config import settings

import logging

logger = logging.getLogger(__name__)

class PaymentSecurityService:
    """Enhanced payment security and fraud detection"""
    
    def __init__(self, db: Session):
        self.db = db
        
        # Risk thresholds
        self.HIGH_RISK_THRESHOLD = 80
        self.MEDIUM_RISK_THRESHOLD = 50
        
        # Rate limiting
        self.MAX_PAYMENTS_PER_HOUR = 5
        self.MAX_PAYMENTS_PER_DAY = 20
        
        # Suspicious patterns
        self.SUSPICIOUS_EMAIL_PATTERNS = [
            r'.*\+.*@.*',  # Plus addressing
            r'.*\.{2,}.*@.*',  # Multiple dots
            r'.*[0-9]{5,}.*@.*',  # Long number sequences
        ]
    
    def calculate_risk_score(
        self,
        user_id: int,
        amount: float,
        ip_address: str = None,
        user_agent: str = None
    ) -> Dict[str, Any]:
        """Calculate comprehensive risk score for a payment"""
        
        risk_factors = []
        total_score = 0
        
        # Get user information
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return {
                'risk_score': 100,
                'risk_level': 'HIGH',
                'factors': ['User not found'],
                'recommendation': 'BLOCK'
            }
        
        # 1. User account age
        account_age_days = (datetime.utcnow() - user.created_at).days if hasattr(user, 'created_at') else 0
        if account_age_days < 1:
            risk_factors.append('New account (less than 1 day old)')
            total_score += 30
        elif account_age_days < 7:
            risk_factors.append('Recent account (less than 1 week old)')
            total_score += 15
        
        # 2. Payment history
        payment_history = self._analyze_payment_history(user_id)
        if payment_history['total_payments'] == 0:
            risk_factors.append('No payment history')
            total_score += 20
        elif payment_history['failed_rate'] > 0.3:
            risk_factors.append(f'High failure rate ({payment_history["failed_rate"]:.1%})')
            total_score += 25
        
        # 3. Payment amount analysis
        amount_risk = self._analyze_payment_amount(user_id, amount)
        if amount_risk['is_unusual']:
            risk_factors.append(amount_risk['reason'])
            total_score += amount_risk['score']
        
        # 4. Rate limiting check
        rate_limit_risk = self._check_rate_limits(user_id)
        if rate_limit_risk['exceeded']:
            risk_factors.append(rate_limit_risk['reason'])
            total_score += rate_limit_risk['score']
        
        # 5. Email pattern analysis
        email_risk = self._analyze_email_pattern(user.email)
        if email_risk['is_suspicious']:
            risk_factors.append(email_risk['reason'])
            total_score += email_risk['score']
        
        # 6. IP address analysis (if provided)
        if ip_address:
            ip_risk = self._analyze_ip_address(ip_address)
            if ip_risk['is_suspicious']:
                risk_factors.append(ip_risk['reason'])
                total_score += ip_risk['score']
        
        # Determine risk level and recommendation
        if total_score >= self.HIGH_RISK_THRESHOLD:
            risk_level = 'HIGH'
            recommendation = 'BLOCK'
        elif total_score >= self.MEDIUM_RISK_THRESHOLD:
            risk_level = 'MEDIUM'
            recommendation = 'REVIEW'
        else:
            risk_level = 'LOW'
            recommendation = 'APPROVE'
        
        return {
            'risk_score': min(total_score, 100),
            'risk_level': risk_level,
            'factors': risk_factors,
            'recommendation': recommendation,
            'details': {
                'account_age_days': account_age_days,
                'payment_history': payment_history,
                'amount_analysis': amount_risk,
                'rate_limits': rate_limit_risk,
                'email_analysis': email_risk
            }
        }
    
    def _analyze_payment_history(self, user_id: int) -> Dict[str, Any]:
        """Analyze user's payment history for risk factors"""
        
        # Get all payments for user
        payments = self.db.query(Payment).filter(Payment.user_id == user_id).all()
        
        total_payments = len(payments)
        if total_payments == 0:
            return {
                'total_payments': 0,
                'successful_payments': 0,
                'failed_payments': 0,
                'failed_rate': 0,
                'average_amount': 0,
                'total_amount': 0
            }
        
        successful = sum(1 for p in payments if p.status == 'COMPLETED')
        failed = sum(1 for p in payments if p.status == 'FAILED')
        total_amount = sum(float(p.amount) for p in payments if p.status == 'COMPLETED')
        
        return {
            'total_payments': total_payments,
            'successful_payments': successful,
            'failed_payments': failed,
            'failed_rate': failed / total_payments if total_payments > 0 else 0,
            'average_amount': total_amount / successful if successful > 0 else 0,
            'total_amount': total_amount
        }
    
    def _analyze_payment_amount(self, user_id: int, amount: float) -> Dict[str, Any]:
        """Analyze if payment amount is unusual for this user"""
        
        # Get user's payment history
        recent_payments = self.db.query(Payment).filter(
            Payment.user_id == user_id,
            Payment.status == 'COMPLETED',
            Payment.completed_at >= datetime.utcnow() - timedelta(days=90)
        ).all()
        
        if len(recent_payments) < 3:
            # Not enough history, check against global average
            global_avg = self._get_global_average_payment()
            if amount > global_avg * 3:
                return {
                    'is_unusual': True,
                    'reason': f'Amount ${amount:.2f} is unusually high (3x global average)',
                    'score': 25
                }
        else:
            # Check against user's history
            amounts = [float(p.amount) for p in recent_payments]
            user_avg = sum(amounts) / len(amounts)
            user_max = max(amounts)
            
            if amount > user_avg * 5:
                return {
                    'is_unusual': True,
                    'reason': f'Amount ${amount:.2f} is 5x user average (${user_avg:.2f})',
                    'score': 30
                }
            elif amount > user_max * 2:
                return {
                    'is_unusual': True,
                    'reason': f'Amount ${amount:.2f} is 2x user maximum (${user_max:.2f})',
                    'score': 20
                }
        
        return {
            'is_unusual': False,
            'reason': 'Amount within normal range',
            'score': 0
        }
    
    def _check_rate_limits(self, user_id: int) -> Dict[str, Any]:
        """Check if user is exceeding rate limits"""
        
        now = datetime.utcnow()
        
        # Check hourly limit
        hour_ago = now - timedelta(hours=1)
        hourly_payments = self.db.query(Payment).filter(
            Payment.user_id == user_id,
            Payment.created_at >= hour_ago
        ).count()
        
        if hourly_payments >= self.MAX_PAYMENTS_PER_HOUR:
            return {
                'exceeded': True,
                'reason': f'Exceeded hourly limit ({hourly_payments}/{self.MAX_PAYMENTS_PER_HOUR})',
                'score': 40
            }
        
        # Check daily limit
        day_ago = now - timedelta(days=1)
        daily_payments = self.db.query(Payment).filter(
            Payment.user_id == user_id,
            Payment.created_at >= day_ago
        ).count()
        
        if daily_payments >= self.MAX_PAYMENTS_PER_DAY:
            return {
                'exceeded': True,
                'reason': f'Exceeded daily limit ({daily_payments}/{self.MAX_PAYMENTS_PER_DAY})',
                'score': 30
            }
        
        return {
            'exceeded': False,
            'reason': 'Within rate limits',
            'score': 0
        }
    
    def _analyze_email_pattern(self, email: str) -> Dict[str, Any]:
        """Analyze email for suspicious patterns"""
        
        for pattern in self.SUSPICIOUS_EMAIL_PATTERNS:
            if re.match(pattern, email):
                return {
                    'is_suspicious': True,
                    'reason': 'Suspicious email pattern detected',
                    'score': 15
                }
        
        # Check for disposable email domains (simplified list)
        disposable_domains = [
            '10minutemail.com', 'tempmail.org', 'guerrillamail.com',
            'mailinator.com', 'throwaway.email'
        ]
        
        domain = email.split('@')[1].lower() if '@' in email else ''
        if domain in disposable_domains:
            return {
                'is_suspicious': True,
                'reason': 'Disposable email domain detected',
                'score': 25
            }
        
        return {
            'is_suspicious': False,
            'reason': 'Email pattern looks normal',
            'score': 0
        }
    
    def _analyze_ip_address(self, ip_address: str) -> Dict[str, Any]:
        """Analyze IP address for risk factors"""
        
        try:
            ip = ipaddress.ip_address(ip_address)
            
            # Check if it's a private/local IP
            if ip.is_private or ip.is_loopback:
                return {
                    'is_suspicious': True,
                    'reason': 'Private/local IP address',
                    'score': 20
                }
            
            # In a real implementation, you would check against:
            # - Known VPN/proxy IP ranges
            # - Geolocation databases
            # - Threat intelligence feeds
            # - Previous fraud patterns
            
            return {
                'is_suspicious': False,
                'reason': 'IP address appears normal',
                'score': 0
            }
            
        except ValueError:
            return {
                'is_suspicious': True,
                'reason': 'Invalid IP address format',
                'score': 10
            }
    
    def _get_global_average_payment(self) -> float:
        """Get global average payment amount"""
        
        from sqlalchemy import func
        
        avg_amount = self.db.query(
            func.avg(Payment.amount)
        ).filter(
            Payment.status == 'COMPLETED'
        ).scalar()
        
        return float(avg_amount) if avg_amount else 100.0  # Default fallback
    
    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """Verify Stripe webhook signature"""
        
        webhook_secret = getattr(settings, 'STRIPE_WEBHOOK_SECRET', '')
        if not webhook_secret:
            logger.warning("Stripe webhook secret not configured")
            return False
        
        try:
            # Extract timestamp and signature from header
            elements = signature.split(',')
            timestamp = None
            signatures = []
            
            for element in elements:
                key, value = element.split('=')
                if key == 't':
                    timestamp = int(value)
                elif key.startswith('v'):
                    signatures.append(value)
            
            if not timestamp or not signatures:
                return False
            
            # Check timestamp (prevent replay attacks)
            current_time = int(time.time())
            if abs(current_time - timestamp) > 300:  # 5 minutes tolerance
                logger.warning("Webhook timestamp too old")
                return False
            
            # Verify signature
            payload_to_sign = f"{timestamp}.{payload.decode('utf-8')}"
            expected_signature = hmac.new(
                webhook_secret.encode('utf-8'),
                payload_to_sign.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            return any(
                hmac.compare_digest(expected_signature, sig)
                for sig in signatures
            )
            
        except Exception as e:
            logger.error(f"Error verifying webhook signature: {e}")
            return False
    
    def log_security_event(
        self,
        event_type: str,
        user_id: int = None,
        payment_id: int = None,
        details: Dict[str, Any] = None,
        severity: str = 'INFO'
    ):
        """Log security events for monitoring and analysis"""
        
        event_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': event_type,
            'user_id': user_id,
            'payment_id': payment_id,
            'severity': severity,
            'details': details or {}
        }
        
        # In a production system, this would be sent to a security monitoring system
        # For now, we'll just log it
        logger.info(f"Security Event: {event_data}")
        
        # Could also store in database for analysis
        # security_log = SecurityLog(**event_data)
        # self.db.add(security_log)
        # self.db.commit()
    
    def get_payment_velocity_check(self, user_id: int) -> Dict[str, Any]:
        """Check payment velocity for a user"""
        
        now = datetime.utcnow()
        
        # Check different time windows
        windows = {
            '1_hour': timedelta(hours=1),
            '24_hours': timedelta(hours=24),
            '7_days': timedelta(days=7),
            '30_days': timedelta(days=30)
        }
        
        velocity_data = {}
        
        for window_name, window_delta in windows.items():
            start_time = now - window_delta
            
            payments = self.db.query(Payment).filter(
                Payment.user_id == user_id,
                Payment.created_at >= start_time
            ).all()
            
            total_amount = sum(float(p.amount) for p in payments)
            
            velocity_data[window_name] = {
                'payment_count': len(payments),
                'total_amount': total_amount,
                'average_amount': total_amount / len(payments) if payments else 0
            }
        
        return velocity_data
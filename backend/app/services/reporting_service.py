"""
Advanced Reporting & Business Intelligence Service
Provides comprehensive analytics, insights, and reporting for business operations
"""

from typing import Dict, List, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, text, case, extract
from datetime import datetime, timedelta, date
from decimal import Decimal
import json

from app.models.user import User
from app.models.booking import Booking
from app.models.payment import Payment
from app.models.flight import Flight
from app.models.seat import Seat
from app.models.aircraft import Aircraft
from app.constants.booking_status import BookingStatus
from app.constants.payment_status import PaymentStatus

import logging

logger = logging.getLogger(__name__)

class BusinessIntelligenceService:
    """Advanced business intelligence and reporting service"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_executive_dashboard(self, days: int = 30) -> Dict[str, Any]:
        """Get executive-level dashboard with key business metrics"""
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Key Performance Indicators
        kpis = self._calculate_kpis(start_date, end_date)
        
        # Revenue trends
        revenue_trends = self._get_revenue_trends(start_date, end_date)
        
        # Customer metrics
        customer_metrics = self._get_customer_metrics(start_date, end_date)
        
        # Operational metrics
        operational_metrics = self._get_operational_metrics(start_date, end_date)
        
        # Market insights
        market_insights = self._get_market_insights(start_date, end_date)
        
        return {
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'days': days
            },
            'kpis': kpis,
            'revenue_trends': revenue_trends,
            'customer_metrics': customer_metrics,
            'operational_metrics': operational_metrics,
            'market_insights': market_insights,
            'generated_at': datetime.utcnow().isoformat()
        }
    
    def _calculate_kpis(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Calculate key performance indicators"""
        
        # Total Revenue
        total_revenue = self.db.query(
            func.sum(Payment.amount)
        ).filter(
            and_(
                Payment.status == PaymentStatus.COMPLETED,
                Payment.completed_at >= start_date,
                Payment.completed_at <= end_date
            )
        ).scalar() or 0
        
        # Total Bookings
        total_bookings = self.db.query(Booking).filter(
            and_(
                Booking.created_at >= start_date,
                Booking.created_at <= end_date
            )
        ).count()
        
        # Confirmed Bookings
        confirmed_bookings = self.db.query(Booking).filter(
            and_(
                Booking.status == BookingStatus.CONFIRMED,
                Booking.created_at >= start_date,
                Booking.created_at <= end_date
            )
        ).count()
        
        # New Customers
        new_customers = self.db.query(User).filter(
            and_(
                User.created_at >= start_date,
                User.created_at <= end_date
            )
        ).count()
        
        # Average Booking Value
        avg_booking_value = float(total_revenue) / confirmed_bookings if confirmed_bookings > 0 else 0
        
        # Conversion Rate
        conversion_rate = (confirmed_bookings / total_bookings * 100) if total_bookings > 0 else 0
        
        # Calculate previous period for comparison
        prev_start = start_date - timedelta(days=(end_date - start_date).days)
        prev_end = start_date
        
        prev_revenue = self.db.query(
            func.sum(Payment.amount)
        ).filter(
            and_(
                Payment.status == PaymentStatus.COMPLETED,
                Payment.completed_at >= prev_start,
                Payment.completed_at <= prev_end
            )
        ).scalar() or 0
        
        prev_bookings = self.db.query(Booking).filter(
            and_(
                Booking.status == BookingStatus.CONFIRMED,
                Booking.created_at >= prev_start,
                Booking.created_at <= prev_end
            )
        ).count()
        
        # Growth calculations
        revenue_growth = ((float(total_revenue) - float(prev_revenue)) / float(prev_revenue) * 100) if prev_revenue > 0 else 0
        booking_growth = ((confirmed_bookings - prev_bookings) / prev_bookings * 100) if prev_bookings > 0 else 0
        
        return {
            'total_revenue': {
                'value': float(total_revenue),
                'growth': round(revenue_growth, 2),
                'formatted': f"${total_revenue:,.2f}"
            },
            'total_bookings': {
                'value': confirmed_bookings,
                'growth': round(booking_growth, 2),
                'total_attempts': total_bookings
            },
            'average_booking_value': {
                'value': round(avg_booking_value, 2),
                'formatted': f"${avg_booking_value:.2f}"
            },
            'conversion_rate': {
                'value': round(conversion_rate, 2),
                'formatted': f"{conversion_rate:.1f}%"
            },
            'new_customers': {
                'value': new_customers
            }
        }
    
    def _get_revenue_trends(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get detailed revenue trend analysis"""
        
        # Daily revenue
        daily_revenue = self.db.query(
            func.date(Payment.completed_at).label('date'),
            func.sum(Payment.amount).label('revenue'),
            func.count(Payment.id).label('transactions')
        ).filter(
            and_(
                Payment.status == PaymentStatus.COMPLETED,
                Payment.completed_at >= start_date,
                Payment.completed_at <= end_date
            )
        ).group_by(
            func.date(Payment.completed_at)
        ).order_by(
            func.date(Payment.completed_at)
        ).all()
        
        # Revenue by hour of day
        hourly_revenue = self.db.query(
            extract('hour', Payment.completed_at).label('hour'),
            func.sum(Payment.amount).label('revenue'),
            func.count(Payment.id).label('transactions')
        ).filter(
            and_(
                Payment.status == PaymentStatus.COMPLETED,
                Payment.completed_at >= start_date,
                Payment.completed_at <= end_date
            )
        ).group_by(
            extract('hour', Payment.completed_at)
        ).order_by(
            extract('hour', Payment.completed_at)
        ).all()
        
        # Revenue by day of week
        weekly_revenue = self.db.query(
            extract('dow', Payment.completed_at).label('day_of_week'),
            func.sum(Payment.amount).label('revenue'),
            func.count(Payment.id).label('transactions')
        ).filter(
            and_(
                Payment.status == PaymentStatus.COMPLETED,
                Payment.completed_at >= start_date,
                Payment.completed_at <= end_date
            )
        ).group_by(
            extract('dow', Payment.completed_at)
        ).order_by(
            extract('dow', Payment.completed_at)
        ).all()
        
        return {
            'daily': [
                {
                    'date': row.date.isoformat(),
                    'revenue': float(row.revenue),
                    'transactions': row.transactions
                } for row in daily_revenue
            ],
            'hourly': [
                {
                    'hour': int(row.hour),
                    'revenue': float(row.revenue),
                    'transactions': row.transactions
                } for row in hourly_revenue
            ],
            'weekly': [
                {
                    'day_of_week': int(row.day_of_week),
                    'day_name': ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'][int(row.day_of_week)],
                    'revenue': float(row.revenue),
                    'transactions': row.transactions
                } for row in weekly_revenue
            ]
        }
    
    def _get_customer_metrics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get comprehensive customer analytics"""
        
        # Customer acquisition
        new_customers = self.db.query(User).filter(
            and_(
                User.created_at >= start_date,
                User.created_at <= end_date
            )
        ).count()
        
        # Customer lifetime value
        customer_ltv = self.db.query(
            Payment.user_id,
            func.sum(Payment.amount).label('total_spent'),
            func.count(Payment.id).label('total_bookings')
        ).filter(
            Payment.status == PaymentStatus.COMPLETED
        ).group_by(Payment.user_id).subquery()
        
        avg_ltv = self.db.query(
            func.avg(customer_ltv.c.total_spent)
        ).scalar() or 0
        
        # Repeat customers
        repeat_customers = self.db.query(
            Payment.user_id
        ).filter(
            Payment.status == PaymentStatus.COMPLETED
        ).group_by(
            Payment.user_id
        ).having(
            func.count(Payment.id) > 1
        ).count()
        
        total_customers = self.db.query(User).count()
        repeat_rate = (repeat_customers / total_customers * 100) if total_customers > 0 else 0
        
        # Customer segments by spending
        customer_segments = self.db.query(
            case(
                (customer_ltv.c.total_spent >= 1000, 'High Value'),
                (customer_ltv.c.total_spent >= 500, 'Medium Value'),
                else_='Low Value'
            ).label('segment'),
            func.count(customer_ltv.c.user_id).label('count'),
            func.avg(customer_ltv.c.total_spent).label('avg_spent')
        ).group_by(
            case(
                (customer_ltv.c.total_spent >= 1000, 'High Value'),
                (customer_ltv.c.total_spent >= 500, 'Medium Value'),
                else_='Low Value'
            )
        ).all()
        
        return {
            'new_customers': new_customers,
            'average_lifetime_value': round(float(avg_ltv), 2),
            'repeat_customer_rate': round(repeat_rate, 2),
            'customer_segments': [
                {
                    'segment': row.segment,
                    'count': row.count,
                    'average_spent': round(float(row.avg_spent), 2)
                } for row in customer_segments
            ]
        }
    
    def _get_operational_metrics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get operational performance metrics"""
        
        # Seat utilization
        total_seats = self.db.query(func.count(Seat.id)).scalar() or 0
        
        booked_seats = self.db.query(
            func.count(Booking.id)
        ).filter(
            and_(
                Booking.status == BookingStatus.CONFIRMED,
                Booking.created_at >= start_date,
                Booking.created_at <= end_date
            )
        ).scalar() or 0
        
        utilization_rate = (booked_seats / total_seats * 100) if total_seats > 0 else 0
        
        # Flight performance
        flight_performance = self.db.query(
            Flight.from_city,
            Flight.to_city,
            func.count(Booking.id).label('bookings'),
            func.sum(Payment.amount).label('revenue')
        ).join(
            Booking, Flight.id == Booking.flight_id
        ).join(
            Payment, Booking.id == Payment.booking_id
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
        ).limit(10).all()
        
        # Booking funnel analysis
        total_attempts = self.db.query(Booking).filter(
            and_(
                Booking.created_at >= start_date,
                Booking.created_at <= end_date
            )
        ).count()
        
        held_bookings = self.db.query(Booking).filter(
            and_(
                Booking.status == BookingStatus.HOLD,
                Booking.created_at >= start_date,
                Booking.created_at <= end_date
            )
        ).count()
        
        confirmed_bookings = self.db.query(Booking).filter(
            and_(
                Booking.status == BookingStatus.CONFIRMED,
                Booking.created_at >= start_date,
                Booking.created_at <= end_date
            )
        ).count()
        
        expired_bookings = self.db.query(Booking).filter(
            and_(
                Booking.status == BookingStatus.EXPIRED,
                Booking.created_at >= start_date,
                Booking.created_at <= end_date
            )
        ).count()
        
        return {
            'seat_utilization': {
                'rate': round(utilization_rate, 2),
                'booked_seats': booked_seats,
                'total_seats': total_seats
            },
            'top_routes': [
                {
                    'route': f"{row.from_city} → {row.to_city}",
                    'bookings': row.bookings,
                    'revenue': float(row.revenue)
                } for row in flight_performance
            ],
            'booking_funnel': {
                'total_attempts': total_attempts,
                'held': held_bookings,
                'confirmed': confirmed_bookings,
                'expired': expired_bookings,
                'conversion_rate': round((confirmed_bookings / total_attempts * 100) if total_attempts > 0 else 0, 2)
            }
        }
    
    def _get_market_insights(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get market analysis and insights"""
        
        # Popular destinations
        destinations = self.db.query(
            Flight.to_city,
            func.count(Booking.id).label('bookings'),
            func.avg(Payment.amount).label('avg_price')
        ).join(
            Booking, Flight.id == Booking.flight_id
        ).join(
            Payment, Booking.id == Payment.booking_id
        ).filter(
            and_(
                Payment.status == PaymentStatus.COMPLETED,
                Payment.completed_at >= start_date,
                Payment.completed_at <= end_date
            )
        ).group_by(
            Flight.to_city
        ).order_by(
            func.count(Booking.id).desc()
        ).limit(10).all()
        
        # Seasonal trends (if we have enough data)
        seasonal_data = self.db.query(
            extract('month', Payment.completed_at).label('month'),
            func.sum(Payment.amount).label('revenue'),
            func.count(Payment.id).label('bookings')
        ).filter(
            Payment.status == PaymentStatus.COMPLETED
        ).group_by(
            extract('month', Payment.completed_at)
        ).order_by(
            extract('month', Payment.completed_at)
        ).all()
        
        # Price analysis
        price_analysis = self.db.query(
            func.min(Payment.amount).label('min_price'),
            func.max(Payment.amount).label('max_price'),
            func.avg(Payment.amount).label('avg_price'),
            func.percentile_cont(0.5).within_group(Payment.amount).label('median_price')
        ).filter(
            and_(
                Payment.status == PaymentStatus.COMPLETED,
                Payment.completed_at >= start_date,
                Payment.completed_at <= end_date
            )
        ).first()
        
        return {
            'popular_destinations': [
                {
                    'city': row.to_city,
                    'bookings': row.bookings,
                    'average_price': round(float(row.avg_price), 2)
                } for row in destinations
            ],
            'seasonal_trends': [
                {
                    'month': int(row.month),
                    'month_name': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                                  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][int(row.month) - 1],
                    'revenue': float(row.revenue),
                    'bookings': row.bookings
                } for row in seasonal_data
            ],
            'price_analysis': {
                'min_price': float(price_analysis.min_price) if price_analysis.min_price else 0,
                'max_price': float(price_analysis.max_price) if price_analysis.max_price else 0,
                'average_price': round(float(price_analysis.avg_price), 2) if price_analysis.avg_price else 0,
                'median_price': round(float(price_analysis.median_price), 2) if price_analysis.median_price else 0
            }
        }
    
    def get_financial_report(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Generate comprehensive financial report"""
        
        # Revenue breakdown
        revenue_by_class = self.db.query(
            Seat.seat_class,
            func.sum(Payment.amount).label('revenue'),
            func.count(Payment.id).label('bookings')
        ).join(
            Booking, Seat.id == Booking.seat_id
        ).join(
            Payment, Booking.id == Payment.booking_id
        ).filter(
            and_(
                Payment.status == PaymentStatus.COMPLETED,
                Payment.completed_at >= start_date,
                Payment.completed_at <= end_date
            )
        ).group_by(
            Seat.seat_class
        ).all()
        
        # Refund analysis
        refunds = self.db.query(
            func.sum(Payment.refunded_amount).label('total_refunded'),
            func.count(Payment.id).label('refund_count')
        ).filter(
            and_(
                Payment.refunded_amount.isnot(None),
                Payment.refunded_at >= start_date,
                Payment.refunded_at <= end_date
            )
        ).first()
        
        # Payment method analysis
        payment_methods = self.db.query(
            Payment.currency,
            func.sum(Payment.amount).label('revenue'),
            func.count(Payment.id).label('transactions')
        ).filter(
            and_(
                Payment.status == PaymentStatus.COMPLETED,
                Payment.completed_at >= start_date,
                Payment.completed_at <= end_date
            )
        ).group_by(
            Payment.currency
        ).all()
        
        return {
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            },
            'revenue_by_class': [
                {
                    'seat_class': row.seat_class,
                    'revenue': float(row.revenue),
                    'bookings': row.bookings
                } for row in revenue_by_class
            ],
            'refunds': {
                'total_refunded': float(refunds.total_refunded) if refunds.total_refunded else 0,
                'refund_count': refunds.refund_count or 0
            },
            'payment_methods': [
                {
                    'currency': row.currency,
                    'revenue': float(row.revenue),
                    'transactions': row.transactions
                } for row in payment_methods
            ]
        }
    
    def get_predictive_insights(self) -> Dict[str, Any]:
        """Generate predictive insights and forecasts"""
        
        # Get historical data for trend analysis
        historical_data = self.db.query(
            func.date(Payment.completed_at).label('date'),
            func.sum(Payment.amount).label('revenue')
        ).filter(
            Payment.status == PaymentStatus.COMPLETED
        ).group_by(
            func.date(Payment.completed_at)
        ).order_by(
            func.date(Payment.completed_at)
        ).all()
        
        if len(historical_data) < 7:
            return {
                'message': 'Insufficient data for predictions',
                'data_points': len(historical_data)
            }
        
        # Simple trend analysis (in production, use proper ML models)
        recent_data = historical_data[-7:]  # Last 7 days
        older_data = historical_data[-14:-7] if len(historical_data) >= 14 else []
        
        recent_avg = sum(float(row.revenue) for row in recent_data) / len(recent_data)
        older_avg = sum(float(row.revenue) for row in older_data) / len(older_data) if older_data else recent_avg
        
        trend = ((recent_avg - older_avg) / older_avg * 100) if older_avg > 0 else 0
        
        # Forecast next 7 days (simple linear projection)
        forecast = []
        for i in range(1, 8):
            projected_revenue = recent_avg * (1 + (trend / 100))
            forecast.append({
                'day': i,
                'projected_revenue': round(projected_revenue, 2),
                'confidence': max(50, 90 - (i * 5))  # Decreasing confidence
            })
        
        return {
            'trend_analysis': {
                'recent_average': round(recent_avg, 2),
                'trend_percentage': round(trend, 2),
                'trend_direction': 'up' if trend > 0 else 'down' if trend < 0 else 'stable'
            },
            'forecast': forecast,
            'recommendations': self._generate_recommendations(trend, recent_avg)
        }
    
    def _generate_recommendations(self, trend: float, recent_avg: float) -> List[str]:
        """Generate business recommendations based on data"""
        
        recommendations = []
        
        if trend > 10:
            recommendations.append("Strong upward trend detected. Consider increasing flight capacity or prices.")
        elif trend < -10:
            recommendations.append("Declining trend observed. Review pricing strategy and marketing campaigns.")
        
        if recent_avg < 1000:
            recommendations.append("Revenue below target. Focus on customer acquisition and retention.")
        elif recent_avg > 5000:
            recommendations.append("Excellent performance. Consider expanding to new routes.")
        
        # Add more intelligent recommendations based on other metrics
        recommendations.append("Monitor customer satisfaction scores to maintain service quality.")
        recommendations.append("Analyze competitor pricing for market positioning opportunities.")
        
        return recommendations
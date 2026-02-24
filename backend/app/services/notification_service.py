"""
Real-time Notification Service
Handles WebSocket connections, real-time updates, and push notifications
"""

import json
import asyncio
from typing import Dict, List, Any, Optional, Set
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import WebSocket, WebSocketDisconnect
from enum import Enum

from app.models.user import User
from app.models.booking import Booking
from app.models.payment import Payment
from app.models.flight import Flight
from app.constants.booking_status import BookingStatus
from app.constants.payment_status import PaymentStatus

import logging

logger = logging.getLogger(__name__)

class NotificationType(str, Enum):
    """Types of notifications"""
    BOOKING_CONFIRMED = "booking_confirmed"
    BOOKING_CANCELLED = "booking_cancelled"
    BOOKING_EXPIRED = "booking_expired"
    PAYMENT_COMPLETED = "payment_completed"
    PAYMENT_FAILED = "payment_failed"
    FLIGHT_DELAYED = "flight_delayed"
    FLIGHT_CANCELLED = "flight_cancelled"
    SEAT_RELEASED = "seat_released"
    PRICE_ALERT = "price_alert"
    SYSTEM_MAINTENANCE = "system_maintenance"
    SECURITY_ALERT = "security_alert"

class NotificationPriority(str, Enum):
    """Notification priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class ConnectionManager:
    """Manages WebSocket connections for real-time notifications"""
    
    def __init__(self):
        # Active connections: user_id -> set of websockets
        self.active_connections: Dict[int, Set[WebSocket]] = {}
        # Connection metadata
        self.connection_metadata: Dict[WebSocket, Dict[str, Any]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: int, metadata: Dict[str, Any] = None):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        
        self.active_connections[user_id].add(websocket)
        self.connection_metadata[websocket] = {
            'user_id': user_id,
            'connected_at': datetime.utcnow(),
            'last_ping': datetime.utcnow(),
            **(metadata or {})
        }
        
        logger.info(f"WebSocket connected for user {user_id}")
        
        # Send welcome message
        await self.send_personal_message({
            'type': 'connection_established',
            'message': 'Connected to Safe Travel notifications',
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_id
        }, user_id)
    
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        if websocket in self.connection_metadata:
            user_id = self.connection_metadata[websocket]['user_id']
            
            # Remove from active connections
            if user_id in self.active_connections:
                self.active_connections[user_id].discard(websocket)
                if not self.active_connections[user_id]:
                    del self.active_connections[user_id]
            
            # Remove metadata
            del self.connection_metadata[websocket]
            
            logger.info(f"WebSocket disconnected for user {user_id}")
    
    async def send_personal_message(self, message: Dict[str, Any], user_id: int):
        """Send message to a specific user"""
        if user_id in self.active_connections:
            disconnected_sockets = set()
            
            for websocket in self.active_connections[user_id].copy():
                try:
                    await websocket.send_text(json.dumps(message))
                except Exception as e:
                    logger.error(f"Error sending message to user {user_id}: {e}")
                    disconnected_sockets.add(websocket)
            
            # Clean up disconnected sockets
            for websocket in disconnected_sockets:
                self.disconnect(websocket)
    
    async def broadcast_message(self, message: Dict[str, Any], exclude_user: int = None):
        """Broadcast message to all connected users"""
        for user_id, websockets in self.active_connections.items():
            if exclude_user and user_id == exclude_user:
                continue
            
            await self.send_personal_message(message, user_id)
    
    async def send_to_multiple_users(self, message: Dict[str, Any], user_ids: List[int]):
        """Send message to multiple specific users"""
        for user_id in user_ids:
            await self.send_personal_message(message, user_id)
    
    def get_connected_users(self) -> List[int]:
        """Get list of currently connected user IDs"""
        return list(self.active_connections.keys())
    
    def get_connection_count(self) -> int:
        """Get total number of active connections"""
        return sum(len(sockets) for sockets in self.active_connections.values())
    
    async def ping_all_connections(self):
        """Send ping to all connections to keep them alive"""
        ping_message = {
            'type': 'ping',
            'timestamp': datetime.utcnow().isoformat()
        }
        
        for user_id in list(self.active_connections.keys()):
            await self.send_personal_message(ping_message, user_id)

# Global connection manager instance
connection_manager = ConnectionManager()

class NotificationService:
    """Service for creating and managing notifications"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def create_notification(
        self,
        user_id: int,
        notification_type: NotificationType,
        title: str,
        message: str,
        priority: NotificationPriority = NotificationPriority.MEDIUM,
        data: Dict[str, Any] = None,
        send_realtime: bool = True
    ) -> Dict[str, Any]:
        """Create and optionally send a real-time notification"""
        
        notification = {
            'id': f"notif_{int(datetime.utcnow().timestamp() * 1000)}",
            'user_id': user_id,
            'type': notification_type.value,
            'title': title,
            'message': message,
            'priority': priority.value,
            'data': data or {},
            'timestamp': datetime.utcnow().isoformat(),
            'read': False
        }
        
        # Store notification (in production, save to database)
        logger.info(f"Created notification for user {user_id}: {title}")
        
        # Send real-time notification if requested
        if send_realtime:
            await connection_manager.send_personal_message({
                'type': 'notification',
                **notification
            }, user_id)
        
        return notification
    
    async def notify_booking_confirmed(self, booking_id: int, user_id: int):
        """Send booking confirmation notification"""
        booking = self.db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            return
        
        flight_info = ""
        if booking.flight:
            flight_info = f"{booking.flight.from_city} → {booking.flight.to_city}"
        
        await self.create_notification(
            user_id=user_id,
            notification_type=NotificationType.BOOKING_CONFIRMED,
            title="Booking Confirmed! ✈️",
            message=f"Your flight booking #{booking_id} has been confirmed. {flight_info}",
            priority=NotificationPriority.HIGH,
            data={
                'booking_id': booking_id,
                'flight_info': flight_info,
                'seat_number': booking.seat.seat_number if booking.seat else None
            }
        )
    
    async def notify_payment_completed(self, payment_id: int, user_id: int):
        """Send payment completion notification"""
        payment = self.db.query(Payment).filter(Payment.id == payment_id).first()
        if not payment:
            return
        
        await self.create_notification(
            user_id=user_id,
            notification_type=NotificationType.PAYMENT_COMPLETED,
            title="Payment Successful 💳",
            message=f"Payment of ${payment.amount} has been processed successfully.",
            priority=NotificationPriority.HIGH,
            data={
                'payment_id': payment_id,
                'amount': float(payment.amount),
                'booking_id': payment.booking_id
            }
        )
    
    async def notify_payment_failed(self, payment_id: int, user_id: int, reason: str = None):
        """Send payment failure notification"""
        await self.create_notification(
            user_id=user_id,
            notification_type=NotificationType.PAYMENT_FAILED,
            title="Payment Failed ❌",
            message=f"Your payment could not be processed. {reason or 'Please try again.'}",
            priority=NotificationPriority.HIGH,
            data={
                'payment_id': payment_id,
                'reason': reason
            }
        )
    
    async def notify_booking_expired(self, booking_id: int, user_id: int):
        """Send booking expiration notification"""
        await self.create_notification(
            user_id=user_id,
            notification_type=NotificationType.BOOKING_EXPIRED,
            title="Booking Expired ⏰",
            message=f"Your booking #{booking_id} has expired. The seat has been released.",
            priority=NotificationPriority.MEDIUM,
            data={'booking_id': booking_id}
        )
    
    async def notify_flight_delay(self, flight_id: int, delay_minutes: int, new_time: datetime):
        """Send flight delay notification to all passengers"""
        flight = self.db.query(Flight).filter(Flight.id == flight_id).first()
        if not flight:
            return
        
        # Get all confirmed bookings for this flight
        bookings = self.db.query(Booking).filter(
            Booking.flight_id == flight_id,
            Booking.status == BookingStatus.CONFIRMED
        ).all()
        
        user_ids = [booking.user_id for booking in bookings]
        
        message = {
            'type': 'notification',
            'notification_type': NotificationType.FLIGHT_DELAYED.value,
            'title': f"Flight Delayed ⏰",
            'message': f"Flight {flight.from_city} → {flight.to_city} is delayed by {delay_minutes} minutes.",
            'priority': NotificationPriority.HIGH.value,
            'data': {
                'flight_id': flight_id,
                'delay_minutes': delay_minutes,
                'new_departure_time': new_time.isoformat(),
                'route': f"{flight.from_city} → {flight.to_city}"
            },
            'timestamp': datetime.utcnow().isoformat()
        }
        
        await connection_manager.send_to_multiple_users(message, user_ids)
        logger.info(f"Sent flight delay notification to {len(user_ids)} passengers")
    
    async def notify_security_alert(self, user_id: int, alert_type: str, details: Dict[str, Any]):
        """Send security alert notification"""
        await self.create_notification(
            user_id=user_id,
            notification_type=NotificationType.SECURITY_ALERT,
            title="Security Alert 🔒",
            message=f"Security alert: {alert_type}. Please review your account activity.",
            priority=NotificationPriority.URGENT,
            data={
                'alert_type': alert_type,
                'details': details
            }
        )
    
    async def notify_price_alert(self, user_id: int, route: str, old_price: float, new_price: float):
        """Send price change alert"""
        price_change = new_price - old_price
        direction = "increased" if price_change > 0 else "decreased"
        
        await self.create_notification(
            user_id=user_id,
            notification_type=NotificationType.PRICE_ALERT,
            title=f"Price Alert 💰",
            message=f"Price for {route} has {direction} by ${abs(price_change):.2f}",
            priority=NotificationPriority.MEDIUM,
            data={
                'route': route,
                'old_price': old_price,
                'new_price': new_price,
                'price_change': price_change
            }
        )
    
    async def broadcast_system_maintenance(self, message: str, start_time: datetime, duration_minutes: int):
        """Broadcast system maintenance notification"""
        maintenance_message = {
            'type': 'notification',
            'notification_type': NotificationType.SYSTEM_MAINTENANCE.value,
            'title': "System Maintenance 🔧",
            'message': message,
            'priority': NotificationPriority.MEDIUM.value,
            'data': {
                'start_time': start_time.isoformat(),
                'duration_minutes': duration_minutes,
                'end_time': (start_time + timedelta(minutes=duration_minutes)).isoformat()
            },
            'timestamp': datetime.utcnow().isoformat()
        }
        
        await connection_manager.broadcast_message(maintenance_message)
        logger.info("Broadcasted system maintenance notification")

# Background task for connection health monitoring
async def connection_health_monitor():
    """Background task to monitor connection health"""
    while True:
        try:
            await connection_manager.ping_all_connections()
            await asyncio.sleep(30)  # Ping every 30 seconds
        except Exception as e:
            logger.error(f"Error in connection health monitor: {e}")
            await asyncio.sleep(60)  # Wait longer on error

# Background task for booking expiration monitoring
async def booking_expiration_monitor(db: Session):
    """Background task to monitor and notify about booking expirations"""
    while True:
        try:
            # Find bookings that will expire in the next 5 minutes
            warning_time = datetime.utcnow() + timedelta(minutes=5)
            expiring_bookings = db.query(Booking).filter(
                Booking.status == BookingStatus.HOLD,
                Booking.expires_at <= warning_time,
                Booking.expires_at > datetime.utcnow()
            ).all()
            
            notification_service = NotificationService(db)
            
            for booking in expiring_bookings:
                await notification_service.create_notification(
                    user_id=booking.user_id,
                    notification_type=NotificationType.BOOKING_EXPIRED,
                    title="Booking Expiring Soon ⏰",
                    message=f"Your booking #{booking.id} will expire in 5 minutes. Complete payment to secure your seat.",
                    priority=NotificationPriority.HIGH,
                    data={
                        'booking_id': booking.id,
                        'expires_at': booking.expires_at.isoformat()
                    }
                )
            
            await asyncio.sleep(300)  # Check every 5 minutes
            
        except Exception as e:
            logger.error(f"Error in booking expiration monitor: {e}")
            await asyncio.sleep(300)
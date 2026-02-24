"""
Live Monitoring API Routes
Real-time dashboard for admin and user activity monitoring
"""

import time
from datetime import datetime
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.routes.auth import get_current_user
from app.database_dep import get_db
from app.services.live_monitoring import get_monitoring_service
from app.services.nanosecond_booking import get_nanosecond_engine

import logging
import json
import asyncio

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/live-monitoring", tags=["Live Monitoring"])

# Get monitoring service
monitoring_service = get_monitoring_service()

@router.get("/dashboard")
async def get_live_dashboard(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    🔍 Get live dashboard data based on user role
    Admin gets full system monitoring, users get limited view
    """
    try:
        # Check if user is admin (you can customize this logic)
        is_admin = getattr(current_user, 'email', '') == 'test@safetravelapp.com'  # Admin user
        
        # Track user activity
        monitoring_service.track_user_session(current_user.id, 'ACTIVITY')
        
        # Get dashboard data
        dashboard_data = monitoring_service.get_live_dashboard_data(
            user_id=current_user.id,
            is_admin=is_admin
        )
        
        # Add nanosecond engine stats
        nano_engine = get_nanosecond_engine("flight_booking.db")
        engine_stats = nano_engine.get_performance_stats()
        
        dashboard_data['nanosecond_engine'] = {
            'status': 'ACTIVE',
            'total_seats': engine_stats['total_seats'],
            'available_seats': engine_stats['available_seats'],
            'booked_seats': engine_stats['booked_seats'],
            'booking_counter': engine_stats['booking_counter']
        }
        
        return dashboard_data
        
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        raise HTTPException(status_code=500, detail=f"Dashboard error: {e}")

@router.get("/activity-stream")
async def get_activity_stream(
    current_user = Depends(get_current_user)
):
    """
    📊 Get live activity stream
    """
    try:
        is_admin = getattr(current_user, 'email', '') == 'test@safetravelapp.com'
        
        activity_stream = monitoring_service.get_live_activity_stream(
            user_id=current_user.id,
            is_admin=is_admin
        )
        
        return {
            'activities': activity_stream,
            'timestamp': datetime.utcnow().isoformat(),
            'user_role': 'admin' if is_admin else 'user'
        }
        
    except Exception as e:
        logger.error(f"Activity stream error: {e}")
        raise HTTPException(status_code=500, detail=f"Activity stream error: {e}")

@router.post("/log-activity")
async def log_custom_activity(
    activity_data: dict,
    current_user = Depends(get_current_user)
):
    """
    📝 Log custom activity (for testing or manual events)
    """
    try:
        monitoring_service.log_activity(
            activity_type=activity_data.get('type', 'CUSTOM'),
            user_id=current_user.id,
            details=activity_data.get('details', {})
        )
        
        return {
            'success': True,
            'message': 'Activity logged successfully'
        }
        
    except Exception as e:
        logger.error(f"Log activity error: {e}")
        raise HTTPException(status_code=500, detail=f"Log activity error: {e}")

@router.get("/performance-test")
async def run_live_performance_test(
    iterations: int = 10,
    current_user = Depends(get_current_user)
):
    """
    🚀 Run live performance test and log results
    """
    try:
        is_admin = getattr(current_user, 'email', '') == 'test@safetravelapp.com'
        
        if not is_admin:
            raise HTTPException(status_code=403, detail="Admin access required")
        
        nano_engine = get_nanosecond_engine("flight_booking.db")
        
        # Run performance tests
        test_results = {
            'iterations': iterations,
            'booking_times': [],
            'lookup_times': [],
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Test booking performance
        for i in range(min(iterations, 10)):  # Limit to prevent conflicts
            start_ns = time.perf_counter_ns()
            
            # Get available seats first
            seats_result = nano_engine.get_available_seats_instant(2)
            if seats_result['seats']:
                # Try booking first available seat
                seat = seats_result['seats'][0]
                booking_result = nano_engine.nanosecond_book_seat(
                    user_id=current_user.id,
                    flight_id=2,
                    seat_id=seat['id']
                )
                
                end_ns = time.perf_counter_ns()
                booking_time = end_ns - start_ns
                
                test_results['booking_times'].append(booking_time)
                
                # Log the activity
                monitoring_service.log_activity(
                    'PERFORMANCE_TEST_BOOKING',
                    current_user.id,
                    {
                        'booking_time_ns': booking_time,
                        'booking_time_microseconds': booking_time / 1000,
                        'seat_number': seat['seat_number'],
                        'success': booking_result['success']
                    }
                )
                
                # Log performance sample
                monitoring_service.log_performance_sample(
                    'NANOSECOND_BOOKING',
                    booking_time,
                    booking_result['success']
                )
        
        # Test lookup performance
        for i in range(iterations):
            start_ns = time.perf_counter_ns()
            nano_engine.get_available_seats_instant(2)
            end_ns = time.perf_counter_ns()
            
            lookup_time = end_ns - start_ns
            test_results['lookup_times'].append(lookup_time)
            
            monitoring_service.log_performance_sample(
                'SEAT_LOOKUP',
                lookup_time,
                True
            )
        
        # Calculate averages
        if test_results['booking_times']:
            avg_booking = sum(test_results['booking_times']) / len(test_results['booking_times'])
            test_results['avg_booking_time_ns'] = avg_booking
            test_results['avg_booking_time_microseconds'] = avg_booking / 1000
            test_results['bookings_per_second'] = 1_000_000_000 / avg_booking
        
        if test_results['lookup_times']:
            avg_lookup = sum(test_results['lookup_times']) / len(test_results['lookup_times'])
            test_results['avg_lookup_time_ns'] = avg_lookup
            test_results['avg_lookup_time_microseconds'] = avg_lookup / 1000
            test_results['lookups_per_second'] = 1_000_000_000 / avg_lookup
        
        # Log test completion
        monitoring_service.log_activity(
            'PERFORMANCE_TEST_COMPLETED',
            current_user.id,
            {
                'iterations': iterations,
                'avg_booking_microseconds': test_results.get('avg_booking_time_microseconds', 0),
                'avg_lookup_microseconds': test_results.get('avg_lookup_time_microseconds', 0),
                'bookings_per_second': test_results.get('bookings_per_second', 0)
            }
        )
        
        return test_results
        
    except Exception as e:
        logger.error(f"Performance test error: {e}")
        raise HTTPException(status_code=500, detail=f"Performance test error: {e}")

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        
        # Track user login
        monitoring_service.track_user_session(user_id, 'LOGIN')
        
        logger.info(f"User {user_id} connected to live monitoring")
    
    def disconnect(self, user_id: int):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
            
        # Track user logout
        monitoring_service.track_user_session(user_id, 'LOGOUT')
        
        logger.info(f"User {user_id} disconnected from live monitoring")
    
    async def send_personal_message(self, message: str, user_id: int):
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_text(message)
            except:
                self.disconnect(user_id)
    
    async def broadcast_to_admins(self, message: str):
        # Broadcast to admin users (you can customize this logic)
        admin_users = [user_id for user_id in self.active_connections.keys()]  # Simplified
        
        for user_id in admin_users:
            await self.send_personal_message(message, user_id)

manager = ConnectionManager()

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    """
    🔄 WebSocket endpoint for real-time monitoring updates
    """
    await manager.connect(websocket, user_id)
    
    try:
        # Send initial dashboard data
        is_admin = True  # You can add proper admin check here
        
        initial_data = monitoring_service.get_live_dashboard_data(user_id, is_admin)
        await websocket.send_text(json.dumps({
            'type': 'INITIAL_DATA',
            'data': initial_data
        }))
        
        # Keep connection alive and send periodic updates
        while True:
            try:
                # Wait for client message or timeout
                await asyncio.wait_for(websocket.receive_text(), timeout=5.0)
            except asyncio.TimeoutError:
                # Send periodic update
                dashboard_data = monitoring_service.get_live_dashboard_data(user_id, is_admin)
                
                await websocket.send_text(json.dumps({
                    'type': 'DASHBOARD_UPDATE',
                    'data': dashboard_data,
                    'timestamp': datetime.utcnow().isoformat()
                }))
            
    except WebSocketDisconnect:
        manager.disconnect(user_id)
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {e}")
        manager.disconnect(user_id)

# Hook into booking operations to log activities
def log_booking_activity(activity_type: str, user_id: int, details: Dict[str, Any]):
    """Helper function to log booking activities from other services"""
    try:
        monitoring_service.log_activity(activity_type, user_id, details)
    except Exception as e:
        logger.error(f"Failed to log booking activity: {e}")

# Export the logging function for use in other services
__all__ = ['router', 'log_booking_activity', 'monitoring_service']
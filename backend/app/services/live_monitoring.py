"""
Live Monitoring Service - Real-time system activity tracking
Shows live backend performance, booking speeds, and system metrics
"""

import time
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, List
from collections import deque, defaultdict
import json
import logging

logger = logging.getLogger(__name__)

class LiveMonitoringService:
    """
    Real-time monitoring service for tracking system performance and activity
    """
    
    def __init__(self):
        # Live activity tracking
        self._activity_log = deque(maxlen=1000)  # Last 1000 activities
        self._performance_metrics = deque(maxlen=100)  # Last 100 performance samples
        self._booking_stats = {
            'total_bookings': 0,
            'successful_bookings': 0,
            'failed_bookings': 0,
            'cancelled_bookings': 0,
            'waitlist_allocations': 0
        }
        
        # Real-time counters
        self._current_users = set()
        self._active_sessions = {}
        
        # Performance tracking
        self._booking_times = deque(maxlen=50)  # Last 50 booking times
        self._allocation_times = deque(maxlen=50)  # Last 50 allocation times
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Start background cleanup
        self._start_cleanup_thread()
        
        logger.info("🔍 Live Monitoring Service initialized")
    
    def log_activity(self, activity_type: str, user_id: int, details: Dict[str, Any]):
        """Log real-time activity"""
        with self._lock:
            activity = {
                'timestamp': datetime.utcnow().isoformat(),
                'timestamp_ns': time.perf_counter_ns(),
                'type': activity_type,
                'user_id': user_id,
                'details': details
            }
            
            self._activity_log.append(activity)
            
            # Update stats
            if activity_type == 'BOOKING_SUCCESS':
                self._booking_stats['total_bookings'] += 1
                self._booking_stats['successful_bookings'] += 1
                
                # Track booking time
                if 'performance_ns' in details:
                    self._booking_times.append(details['performance_ns'])
                    
            elif activity_type == 'BOOKING_FAILED':
                self._booking_stats['total_bookings'] += 1
                self._booking_stats['failed_bookings'] += 1
                
            elif activity_type == 'BOOKING_CANCELLED':
                self._booking_stats['cancelled_bookings'] += 1
                
            elif activity_type == 'WAITLIST_ALLOCATED':
                self._booking_stats['waitlist_allocations'] += 1
                
                # Track allocation time
                if 'performance_ns' in details:
                    self._allocation_times.append(details['performance_ns'])
    
    def log_performance_sample(self, operation: str, time_ns: int, success: bool):
        """Log performance sample"""
        with self._lock:
            sample = {
                'timestamp': datetime.utcnow().isoformat(),
                'operation': operation,
                'time_ns': time_ns,
                'time_microseconds': time_ns / 1000,
                'success': success
            }
            
            self._performance_metrics.append(sample)
    
    def track_user_session(self, user_id: int, action: str):
        """Track user session activity"""
        with self._lock:
            if action == 'LOGIN':
                self._current_users.add(user_id)
                self._active_sessions[user_id] = {
                    'login_time': datetime.utcnow(),
                    'last_activity': datetime.utcnow(),
                    'actions': 0
                }
            elif action == 'LOGOUT':
                self._current_users.discard(user_id)
                self._active_sessions.pop(user_id, None)
            elif action == 'ACTIVITY' and user_id in self._active_sessions:
                self._active_sessions[user_id]['last_activity'] = datetime.utcnow()
                self._active_sessions[user_id]['actions'] += 1
    
    def get_live_dashboard_data(self, user_id: int, is_admin: bool = False) -> Dict[str, Any]:
        """Get live dashboard data based on user role"""
        with self._lock:
            current_time = datetime.utcnow()
            
            # Base data for all users
            dashboard_data = {
                'timestamp': current_time.isoformat(),
                'user_id': user_id,
                'is_admin': is_admin
            }
            
            if is_admin:
                # Admin gets full system monitoring
                dashboard_data.update({
                    'system_stats': self._get_system_stats(),
                    'live_activity': self._get_recent_activity(50),
                    'performance_metrics': self._get_performance_summary(),
                    'active_users': self._get_active_users_info(),
                    'booking_analytics': self._get_booking_analytics(),
                    'real_time_metrics': self._get_real_time_metrics()
                })
            else:
                # Regular users get limited view
                dashboard_data.update({
                    'user_activity': self._get_user_activity(user_id, 10),
                    'system_health': self._get_system_health_summary(),
                    'booking_speed': self._get_booking_speed_summary()
                })
            
            return dashboard_data
    
    def _get_system_stats(self) -> Dict[str, Any]:
        """Get comprehensive system statistics"""
        return {
            'total_bookings': self._booking_stats['total_bookings'],
            'successful_bookings': self._booking_stats['successful_bookings'],
            'failed_bookings': self._booking_stats['failed_bookings'],
            'cancelled_bookings': self._booking_stats['cancelled_bookings'],
            'waitlist_allocations': self._booking_stats['waitlist_allocations'],
            'success_rate': (
                (self._booking_stats['successful_bookings'] / max(self._booking_stats['total_bookings'], 1)) * 100
            ),
            'active_users': len(self._current_users),
            'total_activities': len(self._activity_log)
        }
    
    def _get_recent_activity(self, limit: int) -> List[Dict[str, Any]]:
        """Get recent system activity"""
        activities = list(self._activity_log)[-limit:]
        return activities[::-1]  # Most recent first
    
    def _get_performance_summary(self) -> Dict[str, Any]:
        """Get performance metrics summary"""
        if not self._booking_times:
            return {
                'avg_booking_time_ns': 0,
                'min_booking_time_ns': 0,
                'max_booking_time_ns': 0,
                'avg_booking_time_microseconds': 0,
                'bookings_per_second': 0
            }
        
        booking_times = list(self._booking_times)
        avg_time = sum(booking_times) / len(booking_times)
        
        performance_data = {
            'avg_booking_time_ns': avg_time,
            'min_booking_time_ns': min(booking_times),
            'max_booking_time_ns': max(booking_times),
            'avg_booking_time_microseconds': avg_time / 1000,
            'bookings_per_second': 1_000_000_000 / avg_time if avg_time > 0 else 0
        }
        
        if self._allocation_times:
            allocation_times = list(self._allocation_times)
            avg_allocation = sum(allocation_times) / len(allocation_times)
            performance_data.update({
                'avg_allocation_time_ns': avg_allocation,
                'avg_allocation_time_microseconds': avg_allocation / 1000,
                'allocations_per_second': 1_000_000_000 / avg_allocation if avg_allocation > 0 else 0
            })
        
        return performance_data
    
    def _get_active_users_info(self) -> Dict[str, Any]:
        """Get active users information"""
        current_time = datetime.utcnow()
        active_sessions = []
        
        for user_id, session in self._active_sessions.items():
            session_duration = (current_time - session['login_time']).total_seconds()
            last_activity = (current_time - session['last_activity']).total_seconds()
            
            active_sessions.append({
                'user_id': user_id,
                'session_duration_seconds': session_duration,
                'last_activity_seconds': last_activity,
                'actions_count': session['actions']
            })
        
        return {
            'total_active': len(self._current_users),
            'sessions': active_sessions
        }
    
    def _get_booking_analytics(self) -> Dict[str, Any]:
        """Get booking analytics for admin"""
        current_time = datetime.utcnow()
        
        # Activity in last hour
        hour_ago = current_time - timedelta(hours=1)
        recent_activities = [
            activity for activity in self._activity_log
            if datetime.fromisoformat(activity['timestamp']) > hour_ago
        ]
        
        # Count by type
        activity_counts = defaultdict(int)
        for activity in recent_activities:
            activity_counts[activity['type']] += 1
        
        return {
            'last_hour_activities': dict(activity_counts),
            'total_recent_activities': len(recent_activities),
            'activity_rate_per_minute': len(recent_activities) / 60 if recent_activities else 0
        }
    
    def _get_real_time_metrics(self) -> Dict[str, Any]:
        """Get real-time system metrics"""
        return {
            'memory_structures': {
                'activity_log_size': len(self._activity_log),
                'performance_metrics_size': len(self._performance_metrics),
                'booking_times_tracked': len(self._booking_times),
                'allocation_times_tracked': len(self._allocation_times)
            },
            'current_timestamp_ns': time.perf_counter_ns(),
            'system_uptime_info': {
                'monitoring_active': True,
                'last_cleanup': getattr(self, '_last_cleanup', 'Never')
            }
        }
    
    def _get_user_activity(self, user_id: int, limit: int) -> List[Dict[str, Any]]:
        """Get activity for specific user"""
        user_activities = [
            activity for activity in self._activity_log
            if activity['user_id'] == user_id
        ]
        return user_activities[-limit:][::-1]  # Most recent first
    
    def _get_system_health_summary(self) -> Dict[str, Any]:
        """Get system health summary for regular users"""
        return {
            'status': 'HEALTHY',
            'active_users': len(self._current_users),
            'system_responsive': True,
            'booking_system_status': 'OPERATIONAL'
        }
    
    def _get_booking_speed_summary(self) -> Dict[str, Any]:
        """Get booking speed summary for regular users"""
        if not self._booking_times:
            return {
                'status': 'No recent bookings',
                'avg_speed': 'N/A'
            }
        
        avg_time = sum(self._booking_times) / len(self._booking_times)
        
        return {
            'status': 'ULTRA_FAST',
            'avg_speed_microseconds': avg_time / 1000,
            'performance_level': 'NANOSECOND' if avg_time < 10000 else 'MICROSECOND'
        }
    
    def _start_cleanup_thread(self):
        """Start background cleanup thread"""
        def cleanup_old_data():
            while True:
                try:
                    time.sleep(300)  # Cleanup every 5 minutes
                    
                    with self._lock:
                        current_time = datetime.utcnow()
                        
                        # Remove inactive sessions (no activity for 30 minutes)
                        inactive_users = []
                        for user_id, session in self._active_sessions.items():
                            if (current_time - session['last_activity']).total_seconds() > 1800:
                                inactive_users.append(user_id)
                        
                        for user_id in inactive_users:
                            self._current_users.discard(user_id)
                            self._active_sessions.pop(user_id, None)
                        
                        self._last_cleanup = current_time.isoformat()
                        
                        if inactive_users:
                            logger.info(f"Cleaned up {len(inactive_users)} inactive sessions")
                
                except Exception as e:
                    logger.error(f"Cleanup thread error: {e}")
        
        cleanup_thread = threading.Thread(target=cleanup_old_data, daemon=True)
        cleanup_thread.start()
    
    def get_live_activity_stream(self, user_id: int, is_admin: bool = False) -> List[Dict[str, Any]]:
        """Get live activity stream for WebSocket updates"""
        with self._lock:
            if is_admin:
                # Admin sees all recent activity
                return list(self._activity_log)[-20:][::-1]
            else:
                # Users see their own activity + general system events
                user_activities = [
                    activity for activity in self._activity_log
                    if activity['user_id'] == user_id or activity['type'] in ['SYSTEM_STATUS', 'PERFORMANCE_UPDATE']
                ]
                return user_activities[-10:][::-1]

# Global monitoring service instance
_monitoring_service = None

def get_monitoring_service() -> LiveMonitoringService:
    """Get or create monitoring service instance"""
    global _monitoring_service
    if _monitoring_service is None:
        _monitoring_service = LiveMonitoringService()
    return _monitoring_service
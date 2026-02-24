"""
Ultra-Fast Booking Service - Nanosecond Performance Optimization
High-performance seat booking and waitlist allocation system
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Tuple
from concurrent.futures import ThreadPoolExecutor
from sqlalchemy.orm import Session
from sqlalchemy import text, and_, or_, select, update, delete
from sqlalchemy.exc import IntegrityError
from contextlib import contextmanager
import threading
import queue
import logging

from app.models.booking import Booking
from app.models.seat import Seat
from app.models.flight import Flight
from app.models.user import User
from app.models.waitlist import Waitlist
from app.constants.booking_status import BookingStatus
from app.services.notification_service import NotificationService

logger = logging.getLogger(__name__)

class UltraFastBookingService:
    """
    Ultra-high performance booking service with nanosecond optimizations
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.notification_service = NotificationService(db)
        
        # Performance optimizations
        self._seat_cache = {}
        self._flight_cache = {}
        self._booking_locks = {}
        self._allocation_queue = queue.Queue()
        self._executor = ThreadPoolExecutor(max_workers=10)
        
        # Start background allocation processor
        self._start_allocation_processor()
    
    def _start_allocation_processor(self):
        """Start background thread for processing allocations"""
        def process_allocations():
            while True:
                try:
                    allocation_task = self._allocation_queue.get(timeout=1)
                    if allocation_task:
                        self._process_allocation_task(allocation_task)
                except queue.Empty:
                    continue
                except Exception as e:
                    logger.error(f"Allocation processor error: {e}")
        
        thread = threading.Thread(target=process_allocations, daemon=True)
        thread.start()
    
    @contextmanager
    def _seat_lock(self, seat_id: int):
        """Thread-safe seat locking mechanism"""
        if seat_id not in self._booking_locks:
            self._booking_locks[seat_id] = threading.Lock()
        
        lock = self._booking_locks[seat_id]
        lock.acquire()
        try:
            yield
        finally:
            lock.release()
    
    def ultra_fast_book_seat(
        self, 
        user_id: int, 
        flight_id: int, 
        seat_id: int,
        auto_confirm: bool = False
    ) -> Dict[str, Any]:
        """
        Ultra-fast seat booking with nanosecond optimization
        """
        start_time = time.perf_counter_ns()
        
        try:
            with self._seat_lock(seat_id):
                # Step 1: Atomic seat availability check (optimized query)
                availability_check = self._atomic_seat_check(flight_id, seat_id)
                if not availability_check["available"]:
                    return {
                        "success": False,
                        "message": availability_check["reason"],
                        "processing_time_ns": time.perf_counter_ns() - start_time
                    }
                
                # Step 2: Lightning-fast booking creation
                booking_result = self._lightning_create_booking(
                    user_id, flight_id, seat_id, auto_confirm
                )
                
                if booking_result["success"]:
                    # Step 3: Instant cache updates
                    self._update_caches(flight_id, seat_id, "BOOKED")
                    
                    # Step 4: Async notification (non-blocking)
                    self._async_notify_booking(booking_result["booking"])
                    
                    processing_time = time.perf_counter_ns() - start_time
                    
                    logger.info(f"Ultra-fast booking completed in {processing_time} nanoseconds")
                    
                    return {
                        "success": True,
                        "booking_id": booking_result["booking_id"],
                        "seat_number": availability_check["seat_number"],
                        "processing_time_ns": processing_time,
                        "message": "Seat booked at light speed! ⚡"
                    }
                else:
                    return {
                        "success": False,
                        "message": booking_result["error"],
                        "processing_time_ns": time.perf_counter_ns() - start_time
                    }
        
        except Exception as e:
            logger.error(f"Ultra-fast booking failed: {e}")
            return {
                "success": False,
                "message": f"Booking failed: {e}",
                "processing_time_ns": time.perf_counter_ns() - start_time
            }
    
    def _atomic_seat_check(self, flight_id: int, seat_id: int) -> Dict[str, Any]:
        """
        Atomic seat availability check with single optimized query
        """
        try:
            # Single query to check seat availability and get details
            result = self.db.execute(text("""
                SELECT 
                    s.id as seat_id,
                    s.seat_number,
                    s.seat_class,
                    s.status as seat_status,
                    CASE 
                        WHEN b.id IS NOT NULL AND b.status IN ('HOLD', 'CONFIRMED') 
                        THEN 1 ELSE 0 
                    END as is_booked
                FROM SEATS s
                LEFT JOIN BOOKINGS b ON s.id = b.seat_id 
                    AND b.flight_id = :flight_id 
                    AND b.status IN ('HOLD', 'CONFIRMED')
                WHERE s.id = :seat_id 
                    AND s.aircraft_id = (
                        SELECT aircraft_id FROM FLIGHTS WHERE id = :flight_id
                    )
            """), {
                "flight_id": flight_id,
                "seat_id": seat_id
            }).fetchone()
            
            if not result:
                return {"available": False, "reason": "Seat not found for this flight"}
            
            if result.is_booked:
                return {"available": False, "reason": "Seat already booked"}
            
            return {
                "available": True,
                "seat_number": result.seat_number,
                "seat_class": result.seat_class
            }
            
        except Exception as e:
            logger.error(f"Atomic seat check failed: {e}")
            return {"available": False, "reason": f"Check failed: {e}"}
    
    def _lightning_create_booking(
        self, 
        user_id: int, 
        flight_id: int, 
        seat_id: int,
        auto_confirm: bool = False
    ) -> Dict[str, Any]:
        """
        Lightning-fast booking creation with minimal database operations
        """
        try:
            now = datetime.utcnow()
            status = BookingStatus.CONFIRMED if auto_confirm else BookingStatus.HOLD
            expires_at = None if auto_confirm else now + timedelta(minutes=10)
            
            # Get flight price in single query
            flight_price = self.db.execute(text("""
                SELECT price FROM FLIGHTS WHERE id = :flight_id
            """), {"flight_id": flight_id}).scalar()
            
            # Single INSERT operation
            booking_id = self.db.execute(text("""
                INSERT INTO BOOKINGS (
                    user_id, flight_id, seat_id, status, price, 
                    created_at, expires_at
                ) VALUES (
                    :user_id, :flight_id, :seat_id, :status, :price,
                    :created_at, :expires_at
                ) RETURNING id
            """), {
                "user_id": user_id,
                "flight_id": flight_id,
                "seat_id": seat_id,
                "status": status,
                "price": flight_price,
                "created_at": now,
                "expires_at": expires_at
            }).scalar()
            
            # Update seat status atomically
            self.db.execute(text("""
                UPDATE SEATS SET status = 'BOOKED' WHERE id = :seat_id
            """), {"seat_id": seat_id})
            
            self.db.commit()
            
            return {
                "success": True,
                "booking_id": booking_id,
                "booking": {
                    "id": booking_id,
                    "user_id": user_id,
                    "flight_id": flight_id,
                    "seat_id": seat_id,
                    "status": status,
                    "price": flight_price
                }
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Lightning booking creation failed: {e}")
            return {"success": False, "error": str(e)}
    
    def instant_waitlist_allocation(self, cancelled_booking_id: int) -> Dict[str, Any]:
        """
        Instant waitlist allocation when seat becomes available
        """
        start_time = time.perf_counter_ns()
        
        try:
            # Get cancelled booking details
            booking_data = self.db.execute(text("""
                SELECT flight_id, seat_id FROM BOOKINGS WHERE id = :booking_id
            """), {"booking_id": cancelled_booking_id}).fetchone()
            
            if not booking_data:
                return {"success": False, "message": "Booking not found"}
            
            flight_id = booking_data.flight_id
            seat_id = booking_data.seat_id
            
            # Get next waitlist user with single optimized query
            waitlist_user = self.db.execute(text("""
                SELECT 
                    w.id as waitlist_id,
                    w.user_id,
                    w.preferred_seat_class,
                    w.preferred_seat_position,
                    w.max_price,
                    s.seat_number,
                    s.seat_class,
                    s.col,
                    f.price as flight_price
                FROM WAITLIST w
                JOIN SEATS s ON s.id = :seat_id
                JOIN FLIGHTS f ON f.id = w.flight_id
                WHERE w.flight_id = :flight_id 
                    AND w.status = 'ACTIVE'
                    AND (w.preferred_seat_class = 'ANY' OR w.preferred_seat_class = s.seat_class)
                    AND (w.max_price IS NULL OR w.max_price >= f.price)
                ORDER BY w.priority ASC
                LIMIT 1
            """), {
                "flight_id": flight_id,
                "seat_id": seat_id
            }).fetchone()
            
            if not waitlist_user:
                # No suitable waitlist user, free the seat
                self.db.execute(text("""
                    UPDATE SEATS SET status = 'AVAILABLE' WHERE id = :seat_id
                """), {"seat_id": seat_id})
                self.db.commit()
                
                return {
                    "success": False,
                    "message": "No suitable waitlist user found",
                    "processing_time_ns": time.perf_counter_ns() - start_time
                }
            
            # Instant allocation - create booking for waitlist user
            allocation_result = self._instant_allocate_to_user(
                waitlist_user, flight_id, seat_id
            )
            
            if allocation_result["success"]:
                # Update waitlist status and priorities atomically
                self.db.execute(text("""
                    UPDATE WAITLIST 
                    SET status = 'ALLOCATED', allocated_at = :now 
                    WHERE id = :waitlist_id
                """), {
                    "waitlist_id": waitlist_user.waitlist_id,
                    "now": datetime.utcnow()
                })
                
                # Update priorities for remaining waitlist entries
                self.db.execute(text("""
                    UPDATE WAITLIST 
                    SET priority = priority - 1 
                    WHERE flight_id = :flight_id 
                        AND status = 'ACTIVE' 
                        AND priority > :old_priority
                """), {
                    "flight_id": flight_id,
                    "old_priority": waitlist_user.priority if hasattr(waitlist_user, 'priority') else 1
                })
                
                self.db.commit()
                
                # Async notification (non-blocking)
                self._async_notify_allocation(allocation_result)
                
                processing_time = time.perf_counter_ns() - start_time
                
                logger.info(f"Instant waitlist allocation completed in {processing_time} nanoseconds")
                
                return {
                    "success": True,
                    "allocated_user_id": waitlist_user.user_id,
                    "seat_number": waitlist_user.seat_number,
                    "booking_id": allocation_result["booking_id"],
                    "processing_time_ns": processing_time,
                    "message": "Seat allocated instantly! ⚡"
                }
            else:
                return {
                    "success": False,
                    "message": allocation_result["error"],
                    "processing_time_ns": time.perf_counter_ns() - start_time
                }
        
        except Exception as e:
            self.db.rollback()
            logger.error(f"Instant waitlist allocation failed: {e}")
            return {
                "success": False,
                "message": f"Allocation failed: {e}",
                "processing_time_ns": time.perf_counter_ns() - start_time
            }
    
    def _instant_allocate_to_user(
        self, 
        waitlist_user, 
        flight_id: int, 
        seat_id: int
    ) -> Dict[str, Any]:
        """
        Instantly allocate seat to waitlist user
        """
        try:
            now = datetime.utcnow()
            expires_at = now + timedelta(minutes=15)  # 15 minutes to confirm
            
            # Create booking atomically
            booking_id = self.db.execute(text("""
                INSERT INTO BOOKINGS (
                    user_id, flight_id, seat_id, status, price,
                    created_at, expires_at
                ) VALUES (
                    :user_id, :flight_id, :seat_id, 'HOLD', :price,
                    :created_at, :expires_at
                ) RETURNING id
            """), {
                "user_id": waitlist_user.user_id,
                "flight_id": flight_id,
                "seat_id": seat_id,
                "price": waitlist_user.flight_price,
                "created_at": now,
                "expires_at": expires_at
            }).scalar()
            
            # Update seat status
            self.db.execute(text("""
                UPDATE SEATS SET status = 'HOLD' WHERE id = :seat_id
            """), {"seat_id": seat_id})
            
            return {
                "success": True,
                "booking_id": booking_id,
                "user_id": waitlist_user.user_id,
                "seat_number": waitlist_user.seat_number,
                "expires_at": expires_at
            }
            
        except Exception as e:
            logger.error(f"Instant allocation to user failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _update_caches(self, flight_id: int, seat_id: int, status: str):
        """Update in-memory caches for ultra-fast lookups"""
        try:
            # Update seat cache
            if seat_id in self._seat_cache:
                self._seat_cache[seat_id]["status"] = status
            
            # Update flight cache
            if flight_id in self._flight_cache:
                if "available_seats" in self._flight_cache[flight_id]:
                    if status == "BOOKED" and seat_id in self._flight_cache[flight_id]["available_seats"]:
                        self._flight_cache[flight_id]["available_seats"].remove(seat_id)
                    elif status == "AVAILABLE" and seat_id not in self._flight_cache[flight_id]["available_seats"]:
                        self._flight_cache[flight_id]["available_seats"].append(seat_id)
        
        except Exception as e:
            logger.error(f"Cache update failed: {e}")
    
    def _async_notify_booking(self, booking_data: Dict[str, Any]):
        """Async notification for booking (non-blocking)"""
        def notify():
            try:
                self.notification_service.send_notification(
                    user_id=booking_data["user_id"],
                    notification_type="BOOKING_CONFIRMED",
                    title="🎉 Seat Booked!",
                    message=f"Your seat has been booked successfully!",
                    data=booking_data
                )
            except Exception as e:
                logger.error(f"Async booking notification failed: {e}")
        
        self._executor.submit(notify)
    
    def _async_notify_allocation(self, allocation_data: Dict[str, Any]):
        """Async notification for waitlist allocation (non-blocking)"""
        def notify():
            try:
                self.notification_service.send_notification(
                    user_id=allocation_data["user_id"],
                    notification_type="SEAT_ALLOCATED",
                    title="🚀 Seat Allocated from Waitlist!",
                    message=f"Great news! Seat {allocation_data['seat_number']} is now yours! Confirm within 15 minutes.",
                    data=allocation_data
                )
            except Exception as e:
                logger.error(f"Async allocation notification failed: {e}")
        
        self._executor.submit(notify)
    
    def _process_allocation_task(self, task: Dict[str, Any]):
        """Process allocation task from queue"""
        try:
            if task["type"] == "cancellation":
                self.instant_waitlist_allocation(task["booking_id"])
            elif task["type"] == "expiration":
                self.instant_waitlist_allocation(task["booking_id"])
        except Exception as e:
            logger.error(f"Allocation task processing failed: {e}")
    
    def queue_allocation_task(self, task_type: str, booking_id: int):
        """Queue allocation task for background processing"""
        task = {
            "type": task_type,
            "booking_id": booking_id,
            "timestamp": time.perf_counter_ns()
        }
        self._allocation_queue.put(task)
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        return {
            "cache_size": {
                "seats": len(self._seat_cache),
                "flights": len(self._flight_cache)
            },
            "active_locks": len(self._booking_locks),
            "queue_size": self._allocation_queue.qsize(),
            "executor_threads": self._executor._threads if hasattr(self._executor, '_threads') else 0
        }

# Global instance for ultra-fast access
_ultra_fast_service = None

def get_ultra_fast_service(db: Session) -> UltraFastBookingService:
    """Get or create ultra-fast booking service instance"""
    global _ultra_fast_service
    if _ultra_fast_service is None:
        _ultra_fast_service = UltraFastBookingService(db)
    return _ultra_fast_service
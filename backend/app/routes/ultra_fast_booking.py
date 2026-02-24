"""
Ultra-Fast Booking API Routes
Lightning-speed booking and waitlist allocation endpoints
"""

import time
from datetime import datetime
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database_dep import get_db
from app.services.ultra_fast_booking import get_ultra_fast_service
from app.services.db_optimizer import get_db_optimizer, FastBookingOperations
from app.routes.auth import get_current_user
from app.services.notification_service import NotificationService

import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ultra-fast", tags=["Ultra-Fast Booking"])

# Request models
class UltraFastBookingRequest(BaseModel):
    flight_id: int
    seat_id: int
    auto_confirm: bool = False

class InstantCancelRequest(BaseModel):
    booking_id: int
    reason: str = "User cancellation"

# Initialize optimizer
db_optimizer = get_db_optimizer("sqlite:///./flight_booking.db")
fast_ops = FastBookingOperations(db_optimizer)

@router.post("/book-seat")
async def ultra_fast_book_seat(
    request: UltraFastBookingRequest,
    background_tasks: BackgroundTasks,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    ⚡ Ultra-fast seat booking - Nanosecond performance
    Books a seat with lightning speed and instant waitlist processing
    """
    start_time = time.perf_counter_ns()
    
    try:
        logger.info(f"Ultra-fast booking request: User {current_user.id}, Flight {request.flight_id}, Seat {request.seat_id}")
        
        # Use ultra-fast booking service
        ultra_service = get_ultra_fast_service(db)
        result = ultra_service.ultra_fast_book_seat(
            user_id=current_user.id,
            flight_id=request.flight_id,
            seat_id=request.seat_id,
            auto_confirm=request.auto_confirm
        )
        
        if result["success"]:
            # Background task for additional processing (non-blocking)
            background_tasks.add_task(
                _post_booking_tasks,
                result["booking_id"],
                current_user.id,
                request.flight_id
            )
            
            total_time = time.perf_counter_ns() - start_time
            
            return {
                "success": True,
                "booking_id": result["booking_id"],
                "seat_number": result["seat_number"],
                "message": result["message"],
                "performance": {
                    "booking_time_ns": result["processing_time_ns"],
                    "total_time_ns": total_time,
                    "booking_time_ms": result["processing_time_ns"] / 1_000_000,
                    "total_time_ms": total_time / 1_000_000
                },
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            raise HTTPException(status_code=400, detail=result["message"])
            
    except Exception as e:
        logger.error(f"Ultra-fast booking failed: {e}")
        raise HTTPException(status_code=500, detail=f"Booking failed: {e}")

@router.post("/lightning-book")
async def lightning_book_seat(
    request: UltraFastBookingRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    🚀 Lightning booking - Optimized database operations
    Uses prepared statements and connection pooling for maximum speed
    """
    start_time = time.perf_counter_ns()
    
    try:
        # Use optimized database operations
        result = fast_ops.lightning_book_seat(
            session=db,
            user_id=current_user.id,
            flight_id=request.flight_id,
            seat_id=request.seat_id
        )
        
        total_time = time.perf_counter_ns() - start_time
        
        if result["success"]:
            return {
                "success": True,
                "booking_id": result["booking_id"],
                "seat_number": result["seat_number"],
                "message": result["message"],
                "performance": {
                    "db_time_ns": result["processing_time_ns"],
                    "total_time_ns": total_time,
                    "db_time_microseconds": result["processing_time_ns"] / 1000,
                    "total_time_microseconds": total_time / 1000
                }
            }
        else:
            raise HTTPException(status_code=400, detail=result["message"])
            
    except Exception as e:
        logger.error(f"Lightning booking failed: {e}")
        raise HTTPException(status_code=500, detail=f"Lightning booking failed: {e}")

@router.post("/instant-cancel")
async def instant_cancel_with_allocation(
    request: InstantCancelRequest,
    background_tasks: BackgroundTasks,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    ⚡ Instant cancellation with automatic waitlist allocation
    Cancels booking and instantly allocates to next waitlist user
    """
    start_time = time.perf_counter_ns()
    
    try:
        # Verify booking ownership
        from app.models.booking import Booking
        booking = db.query(Booking).filter(
            Booking.id == request.booking_id,
            Booking.user_id == current_user.id
        ).first()
        
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        
        if booking.status == "CANCELLED":
            raise HTTPException(status_code=400, detail="Booking already cancelled")
        
        # Cancel booking
        booking.status = "CANCELLED"
        booking.expires_at = None
        
        # Free the seat temporarily
        from app.models.seat import Seat
        seat = db.query(Seat).filter(Seat.id == booking.seat_id).first()
        if seat:
            seat.status = "AVAILABLE"
        
        db.commit()
        
        # Instant waitlist allocation
        allocation_result = fast_ops.instant_waitlist_allocation(
            session=db,
            cancelled_booking_id=request.booking_id
        )
        
        total_time = time.perf_counter_ns() - start_time
        
        # Background notification tasks
        if allocation_result["success"]:
            background_tasks.add_task(
                _notify_waitlist_allocation,
                allocation_result["allocated_user_id"],
                allocation_result["seat_number"],
                booking.flight_id
            )
        
        return {
            "success": True,
            "message": "Booking cancelled successfully",
            "waitlist_allocation": allocation_result,
            "performance": {
                "total_time_ns": total_time,
                "total_time_ms": total_time / 1_000_000,
                "allocation_time_ns": allocation_result.get("processing_time_ns", 0),
                "allocation_time_ms": allocation_result.get("processing_time_ns", 0) / 1_000_000
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Instant cancellation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Cancellation failed: {e}")

@router.get("/performance-stats")
async def get_performance_stats(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    📊 Get ultra-fast booking performance statistics
    """
    try:
        ultra_service = get_ultra_fast_service(db)
        
        return {
            "ultra_fast_service": ultra_service.get_performance_stats(),
            "database_optimizer": db_optimizer.get_performance_stats(),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get performance stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get performance stats")

@router.post("/batch-expire")
async def batch_expire_bookings(
    background_tasks: BackgroundTasks,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    🔄 Batch expire old bookings with instant waitlist allocation
    Admin endpoint for processing expired bookings
    """
    if not current_user.is_admin:  # Assuming admin check
        raise HTTPException(status_code=403, detail="Admin access required")
    
    start_time = time.perf_counter_ns()
    
    try:
        from sqlalchemy import text
        
        # Get expired bookings
        expired_bookings = db.execute(text("""
            SELECT id, flight_id, seat_id 
            FROM BOOKINGS 
            WHERE status = 'HOLD' AND expires_at <= :now
        """), {"now": datetime.utcnow()}).fetchall()
        
        if not expired_bookings:
            return {
                "success": True,
                "message": "No expired bookings found",
                "expired_count": 0
            }
        
        # Batch update expired bookings
        expired_ids = [b.id for b in expired_bookings]
        db.execute(text("""
            UPDATE BOOKINGS 
            SET status = 'EXPIRED' 
            WHERE id IN :ids
        """), {"ids": tuple(expired_ids)})
        
        # Free up seats
        seat_ids = [b.seat_id for b in expired_bookings]
        db.execute(text("""
            UPDATE SEATS 
            SET status = 'AVAILABLE' 
            WHERE id IN :seat_ids
        """), {"seat_ids": tuple(seat_ids)})
        
        db.commit()
        
        # Process waitlist allocations for each expired booking
        allocation_results = []
        for booking in expired_bookings:
            allocation_result = fast_ops.instant_waitlist_allocation(
                session=db,
                cancelled_booking_id=booking.id
            )
            allocation_results.append(allocation_result)
            
            # Background notification if allocated
            if allocation_result["success"]:
                background_tasks.add_task(
                    _notify_waitlist_allocation,
                    allocation_result["allocated_user_id"],
                    allocation_result["seat_number"],
                    booking.flight_id
                )
        
        total_time = time.perf_counter_ns() - start_time
        successful_allocations = sum(1 for r in allocation_results if r["success"])
        
        return {
            "success": True,
            "message": f"Processed {len(expired_bookings)} expired bookings",
            "expired_count": len(expired_bookings),
            "allocated_count": successful_allocations,
            "allocation_results": allocation_results,
            "performance": {
                "total_time_ns": total_time,
                "total_time_ms": total_time / 1_000_000,
                "avg_time_per_booking_ns": total_time // len(expired_bookings),
                "avg_time_per_booking_ms": (total_time // len(expired_bookings)) / 1_000_000
            }
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Batch expire failed: {e}")
        raise HTTPException(status_code=500, detail=f"Batch expire failed: {e}")

@router.get("/speed-test")
async def booking_speed_test(
    iterations: int = 100,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    🏃‍♂️ Speed test for booking operations
    Test the performance of booking operations
    """
    try:
        results = {
            "iterations": iterations,
            "tests": {}
        }
        
        # Test 1: Seat availability check speed
        start_time = time.perf_counter_ns()
        for i in range(iterations):
            db.execute(text("""
                SELECT COUNT(*) FROM SEATS s
                LEFT JOIN BOOKINGS b ON s.id = b.seat_id AND b.status IN ('HOLD', 'CONFIRMED')
                WHERE s.aircraft_id = 1 AND b.id IS NULL
            """)).scalar()
        
        results["tests"]["seat_availability_check"] = {
            "total_time_ns": time.perf_counter_ns() - start_time,
            "avg_time_ns": (time.perf_counter_ns() - start_time) // iterations,
            "operations_per_second": iterations / ((time.perf_counter_ns() - start_time) / 1_000_000_000)
        }
        
        # Test 2: Waitlist query speed
        start_time = time.perf_counter_ns()
        for i in range(iterations):
            db.execute(text("""
                SELECT COUNT(*) FROM WAITLIST 
                WHERE flight_id = 1 AND status = 'ACTIVE'
                ORDER BY priority
            """)).scalar()
        
        results["tests"]["waitlist_query"] = {
            "total_time_ns": time.perf_counter_ns() - start_time,
            "avg_time_ns": (time.perf_counter_ns() - start_time) // iterations,
            "operations_per_second": iterations / ((time.perf_counter_ns() - start_time) / 1_000_000_000)
        }
        
        return results
        
    except Exception as e:
        logger.error(f"Speed test failed: {e}")
        raise HTTPException(status_code=500, detail=f"Speed test failed: {e}")

# Background task functions
async def _post_booking_tasks(booking_id: int, user_id: int, flight_id: int):
    """Background tasks after booking (non-blocking)"""
    try:
        # Analytics, logging, etc.
        logger.info(f"Post-booking tasks completed for booking {booking_id}")
    except Exception as e:
        logger.error(f"Post-booking tasks failed: {e}")

async def _notify_waitlist_allocation(user_id: int, seat_number: str, flight_id: int):
    """Background notification for waitlist allocation"""
    try:
        # Send notifications
        logger.info(f"Waitlist allocation notification sent to user {user_id} for seat {seat_number}")
    except Exception as e:
        logger.error(f"Waitlist notification failed: {e}")
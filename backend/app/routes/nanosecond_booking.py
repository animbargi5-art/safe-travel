"""
Nanosecond Booking API Routes - True Nanosecond Performance
Hyper-optimized endpoints operating at nanosecond level
"""

import time
from datetime import datetime
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel

from app.routes.auth import get_current_user
from app.services.nanosecond_booking import get_nanosecond_engine
from app.services.live_monitoring import get_monitoring_service

import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/nanosecond", tags=["Nanosecond Booking"])

# Request models
class NanosecondBookingRequest(BaseModel):
    flight_id: int
    seat_id: int

class NanosecondCancelRequest(BaseModel):
    booking_id: int

# Initialize nanosecond engine and monitoring
nano_engine = get_nanosecond_engine("flight_booking.db")
monitoring_service = get_monitoring_service()

@router.post("/book")
async def nanosecond_book_seat(
    request: NanosecondBookingRequest,
    current_user = Depends(get_current_user)
):
    """
    ⚡ TRUE NANOSECOND BOOKING - Pure in-memory operations
    Books a seat in actual nanoseconds using hyper-optimized algorithms
    """
    # Measure total API time including serialization
    api_start = time.perf_counter_ns()
    
    try:
        # Core booking operation (nanoseconds)
        result = nano_engine.nanosecond_book_seat(
            user_id=current_user.id,
            flight_id=request.flight_id,
            seat_id=request.seat_id
        )
        
        api_end = time.perf_counter_ns()
        total_api_time = api_end - api_start
        
        if result["success"]:
            # Log successful booking activity
            monitoring_service.log_activity(
                'BOOKING_SUCCESS',
                current_user.id,
                {
                    'booking_id': result["booking_id"],
                    'seat_number': result["seat_number"],
                    'seat_class': result["seat_class"],
                    'flight_id': request.flight_id,
                    'performance_ns': result["processing_time_ns"],
                    'performance_microseconds': result["processing_time_microseconds"]
                }
            )
            
            # Log performance sample
            monitoring_service.log_performance_sample(
                'NANOSECOND_BOOKING',
                result["processing_time_ns"],
                True
            )
            
            return {
                "success": True,
                "booking_id": result["booking_id"],
                "seat_number": result["seat_number"],
                "seat_class": result["seat_class"],
                "message": result["message"],
                "performance": {
                    "core_booking_ns": result["processing_time_ns"],
                    "total_api_ns": total_api_time,
                    "core_booking_microseconds": result["processing_time_microseconds"],
                    "total_api_microseconds": total_api_time / 1000,
                    "serialization_overhead_ns": total_api_time - result["processing_time_ns"],
                    "operations_per_second": 1_000_000_000 / result["processing_time_ns"]
                },
                "timestamp_ns": api_end
            }
        else:
            # Log failed booking activity
            monitoring_service.log_activity(
                'BOOKING_FAILED',
                current_user.id,
                {
                    'flight_id': request.flight_id,
                    'seat_id': request.seat_id,
                    'error': result["message"],
                    'performance_ns': result["processing_time_ns"]
                }
            )
            
            raise HTTPException(status_code=400, detail=result["message"])
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Nanosecond booking failed: {e}")
        raise HTTPException(status_code=500, detail=f"Nanosecond booking failed: {e}")

@router.post("/cancel")
async def nanosecond_cancel_with_allocation(
    request: NanosecondCancelRequest,
    current_user = Depends(get_current_user)
):
    """
    🚀 NANOSECOND CANCELLATION + INSTANT WAITLIST ALLOCATION
    Cancels and allocates to waitlist in nanoseconds
    """
    api_start = time.perf_counter_ns()
    
    try:
        result = nano_engine.nanosecond_cancel_with_allocation(
            booking_id=request.booking_id,
            user_id=current_user.id
        )
        
        api_end = time.perf_counter_ns()
        total_api_time = api_end - api_start
        
        if result["success"]:
            return {
                "success": True,
                "message": result["message"],
                "waitlist_allocation": result["waitlist_allocation"],
                "performance": {
                    "core_operation_ns": result["processing_time_ns"],
                    "total_api_ns": total_api_time,
                    "core_operation_microseconds": result["processing_time_microseconds"],
                    "total_api_microseconds": total_api_time / 1000,
                    "operations_per_second": 1_000_000_000 / result["processing_time_ns"]
                }
            }
        else:
            raise HTTPException(status_code=400, detail=result["message"])
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Nanosecond cancel failed: {e}")
        raise HTTPException(status_code=500, detail=f"Nanosecond cancel failed: {e}")

@router.get("/seats/{flight_id}")
async def get_seats_nanosecond(
    flight_id: int,
    current_user = Depends(get_current_user)
):
    """
    ⚡ INSTANT SEAT AVAILABILITY - Pure memory lookup
    Gets seat availability in nanoseconds from in-memory cache
    """
    api_start = time.perf_counter_ns()
    
    try:
        result = nano_engine.get_available_seats_instant(flight_id)
        
        api_end = time.perf_counter_ns()
        total_api_time = api_end - api_start
        
        return {
            "seats": result["seats"],
            "count": result["count"],
            "flight_id": flight_id,
            "performance": {
                "core_lookup_ns": result["processing_time_ns"],
                "total_api_ns": total_api_time,
                "core_lookup_microseconds": result["processing_time_microseconds"],
                "total_api_microseconds": total_api_time / 1000,
                "lookups_per_second": 1_000_000_000 / result["processing_time_ns"]
            }
        }
        
    except Exception as e:
        logger.error(f"Nanosecond seat lookup failed: {e}")
        raise HTTPException(status_code=500, detail=f"Seat lookup failed: {e}")

@router.get("/stats")
async def get_nanosecond_stats(current_user = Depends(get_current_user)):
    """
    📊 NANOSECOND ENGINE STATISTICS
    Real-time performance and memory statistics
    """
    try:
        stats = nano_engine.get_performance_stats()
        
        return {
            "engine_stats": stats,
            "timestamp": datetime.utcnow().isoformat(),
            "performance_level": "NANOSECOND",
            "optimization_level": "MAXIMUM"
        }
        
    except Exception as e:
        logger.error(f"Failed to get nanosecond stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get stats")

@router.post("/benchmark")
async def nanosecond_benchmark(
    iterations: int = 1000,
    current_user = Depends(get_current_user)
):
    """
    🏃‍♂️ NANOSECOND PERFORMANCE BENCHMARK
    Benchmark pure nanosecond operations
    """
    if iterations > 10000:
        raise HTTPException(status_code=400, detail="Max 10,000 iterations")
    
    try:
        benchmark_results = {
            "iterations": iterations,
            "tests": {}
        }
        
        # Test 1: Pure booking speed (in-memory only)
        booking_times = []
        successful_bookings = 0
        
        for i in range(min(iterations, 100)):  # Limit to avoid conflicts
            start_ns = time.perf_counter_ns()
            
            # Use different seats to avoid conflicts
            seat_id = (i % 180) + 1
            
            result = nano_engine.nanosecond_book_seat(
                user_id=current_user.id,
                flight_id=2,
                seat_id=seat_id
            )
            
            end_ns = time.perf_counter_ns()
            booking_time = end_ns - start_ns
            booking_times.append(booking_time)
            
            if result["success"]:
                successful_bookings += 1
        
        if booking_times:
            avg_booking_time = sum(booking_times) / len(booking_times)
            min_booking_time = min(booking_times)
            max_booking_time = max(booking_times)
            
            benchmark_results["tests"]["nanosecond_booking"] = {
                "avg_time_ns": avg_booking_time,
                "min_time_ns": min_booking_time,
                "max_time_ns": max_booking_time,
                "avg_time_microseconds": avg_booking_time / 1000,
                "min_time_microseconds": min_booking_time / 1000,
                "max_time_microseconds": max_booking_time / 1000,
                "successful_bookings": successful_bookings,
                "success_rate": (successful_bookings / len(booking_times)) * 100,
                "bookings_per_second": 1_000_000_000 / avg_booking_time
            }
        
        # Test 2: Seat lookup speed
        lookup_times = []
        
        for i in range(min(iterations, 1000)):
            start_ns = time.perf_counter_ns()
            nano_engine.get_available_seats_instant(2)
            end_ns = time.perf_counter_ns()
            lookup_times.append(end_ns - start_ns)
        
        if lookup_times:
            avg_lookup_time = sum(lookup_times) / len(lookup_times)
            
            benchmark_results["tests"]["seat_lookup"] = {
                "avg_time_ns": avg_lookup_time,
                "min_time_ns": min(lookup_times),
                "max_time_ns": max(lookup_times),
                "avg_time_microseconds": avg_lookup_time / 1000,
                "lookups_per_second": 1_000_000_000 / avg_lookup_time
            }
        
        # Test 3: Memory operation speed
        memory_times = []
        
        for i in range(iterations):
            start_ns = time.perf_counter_ns()
            # Simulate memory operations
            stats = nano_engine.get_performance_stats()
            end_ns = time.perf_counter_ns()
            memory_times.append(end_ns - start_ns)
        
        if memory_times:
            avg_memory_time = sum(memory_times) / len(memory_times)
            
            benchmark_results["tests"]["memory_operations"] = {
                "avg_time_ns": avg_memory_time,
                "min_time_ns": min(memory_times),
                "max_time_ns": max(memory_times),
                "avg_time_microseconds": avg_memory_time / 1000,
                "operations_per_second": 1_000_000_000 / avg_memory_time
            }
        
        return benchmark_results
        
    except Exception as e:
        logger.error(f"Nanosecond benchmark failed: {e}")
        raise HTTPException(status_code=500, detail=f"Benchmark failed: {e}")

@router.get("/health")
async def nanosecond_health_check():
    """
    ⚡ NANOSECOND HEALTH CHECK
    Ultra-fast health check in nanoseconds
    """
    start_ns = time.perf_counter_ns()
    
    try:
        # Quick engine check
        stats = nano_engine.get_performance_stats()
        
        end_ns = time.perf_counter_ns()
        check_time = end_ns - start_ns
        
        return {
            "status": "HEALTHY",
            "engine": "Nanosecond Booking Engine",
            "total_seats": stats["total_seats"],
            "available_seats": stats["available_seats"],
            "health_check_time_ns": check_time,
            "health_check_time_microseconds": check_time / 1000,
            "timestamp_ns": end_ns
        }
        
    except Exception as e:
        return {
            "status": "UNHEALTHY",
            "error": str(e),
            "timestamp_ns": time.perf_counter_ns()
        }

@router.post("/stress-test")
async def nanosecond_stress_test(
    concurrent_operations: int = 1000,
    current_user = Depends(get_current_user)
):
    """
    💪 NANOSECOND STRESS TEST
    Test system under extreme load with nanosecond precision
    """
    if concurrent_operations > 5000:
        raise HTTPException(status_code=400, detail="Max 5,000 concurrent operations")
    
    try:
        import threading
        import queue
        
        results_queue = queue.Queue()
        
        def stress_operation(operation_id: int):
            start_ns = time.perf_counter_ns()
            
            try:
                # Alternate between booking and lookup operations
                if operation_id % 2 == 0:
                    # Booking operation
                    seat_id = (operation_id % 180) + 1
                    result = nano_engine.nanosecond_book_seat(
                        user_id=current_user.id,
                        flight_id=2,
                        seat_id=seat_id
                    )
                    operation_type = "booking"
                else:
                    # Lookup operation
                    result = nano_engine.get_available_seats_instant(2)
                    operation_type = "lookup"
                
                end_ns = time.perf_counter_ns()
                
                results_queue.put({
                    "operation_id": operation_id,
                    "operation_type": operation_type,
                    "success": result.get("success", True),
                    "time_ns": end_ns - start_ns,
                    "time_microseconds": (end_ns - start_ns) / 1000
                })
                
            except Exception as e:
                end_ns = time.perf_counter_ns()
                results_queue.put({
                    "operation_id": operation_id,
                    "operation_type": "error",
                    "success": False,
                    "time_ns": end_ns - start_ns,
                    "error": str(e)
                })
        
        # Launch concurrent operations
        stress_start = time.perf_counter_ns()
        threads = []
        
        for i in range(concurrent_operations):
            thread = threading.Thread(target=stress_operation, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all operations to complete
        for thread in threads:
            thread.join()
        
        stress_end = time.perf_counter_ns()
        total_stress_time = stress_end - stress_start
        
        # Collect results
        results = []
        while not results_queue.empty():
            results.append(results_queue.get())
        
        # Analyze results
        successful_ops = [r for r in results if r["success"]]
        failed_ops = [r for r in results if not r["success"]]
        
        if successful_ops:
            times = [r["time_ns"] for r in successful_ops]
            avg_time = sum(times) / len(times)
            min_time = min(times)
            max_time = max(times)
            
            return {
                "stress_test_results": {
                    "total_operations": concurrent_operations,
                    "successful_operations": len(successful_ops),
                    "failed_operations": len(failed_ops),
                    "success_rate": (len(successful_ops) / concurrent_operations) * 100,
                    "total_time_ns": total_stress_time,
                    "total_time_ms": total_stress_time / 1_000_000,
                    "avg_operation_time_ns": avg_time,
                    "min_operation_time_ns": min_time,
                    "max_operation_time_ns": max_time,
                    "avg_operation_time_microseconds": avg_time / 1000,
                    "min_operation_time_microseconds": min_time / 1000,
                    "max_operation_time_microseconds": max_time / 1000,
                    "operations_per_second": concurrent_operations / (total_stress_time / 1_000_000_000),
                    "throughput": len(successful_ops) / (total_stress_time / 1_000_000_000)
                }
            }
        else:
            return {
                "stress_test_results": {
                    "total_operations": concurrent_operations,
                    "successful_operations": 0,
                    "failed_operations": len(failed_ops),
                    "success_rate": 0,
                    "error": "All operations failed"
                }
            }
        
    except Exception as e:
        logger.error(f"Stress test failed: {e}")
        raise HTTPException(status_code=500, detail=f"Stress test failed: {e}")
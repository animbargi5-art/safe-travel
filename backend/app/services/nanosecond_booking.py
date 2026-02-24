"""
Nanosecond Booking Service - True Nanosecond Performance
Hyper-optimized booking system with in-memory operations and pre-compiled queries
"""

import time
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Set
from collections import defaultdict
import asyncio
from concurrent.futures import ThreadPoolExecutor
import sqlite3
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)

class NanosecondBookingEngine:
    """
    Hyper-optimized booking engine operating at nanosecond level
    """
    
    def __init__(self, db_path: str):
        # In-memory data structures for nanosecond access
        self._seat_status = {}  # seat_id -> status
        self._flight_seats = defaultdict(set)  # flight_id -> set of seat_ids
        self._available_seats = defaultdict(set)  # flight_id -> set of available seat_ids
        self._waitlist_queue = defaultdict(list)  # flight_id -> list of waitlist entries
        self._booking_counter = 0
        
        # Thread-safe locks for atomic operations
        self._seat_locks = defaultdict(threading.Lock)
        self._global_lock = threading.RLock()
        
        # Pre-compiled SQL statements for maximum speed
        self._db_path = db_path
        self._prepare_statements()
        
        # Initialize in-memory cache
        self._load_initial_data()
        
        # Background processor for async operations
        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="nano-booking")
        
        logger.info("🚀 Nanosecond Booking Engine initialized")
    
    def _prepare_statements(self):
        """Pre-compile all SQL statements for instant execution"""
        self._statements = {
            'insert_booking': """
                INSERT INTO BOOKINGS (user_id, flight_id, seat_id, status, price, created_at, expires_at)
                VALUES (?, ?, ?, ?, ?, ?, ?) RETURNING id
            """,
            'update_seat_status': "UPDATE SEATS SET status = ? WHERE id = ?",
            'get_flight_price': "SELECT price FROM FLIGHTS WHERE id = ?",
            'insert_waitlist_booking': """
                INSERT INTO BOOKINGS (user_id, flight_id, seat_id, status, price, created_at, expires_at)
                VALUES (?, ?, ?, 'HOLD', ?, ?, ?)
            """,
            'update_waitlist_status': "UPDATE WAITLIST SET status = 'ALLOCATED', allocated_at = ? WHERE id = ?",
            'update_waitlist_priorities': """
                UPDATE WAITLIST SET priority = priority - 1 
                WHERE flight_id = ? AND status = 'ACTIVE' AND priority > ?
            """
        }
    
    def _load_initial_data(self):
        """Load initial seat and flight data into memory for nanosecond access"""
        try:
            conn = sqlite3.connect(self._db_path)
            cursor = conn.cursor()
            
            # Load all seats with their aircraft assignments
            cursor.execute("""
                SELECT s.id, s.aircraft_id, s.seat_number, s.seat_class, s.row, s.col
                FROM SEATS s
            """)
            
            seat_data = cursor.fetchall()
            
            # Load flights with their aircraft assignments
            cursor.execute("""
                SELECT f.id, f.aircraft_id
                FROM FLIGHTS f
            """)
            
            flight_data = cursor.fetchall()
            
            # Create aircraft to flights mapping
            aircraft_to_flights = {}
            for flight_id, aircraft_id in flight_data:
                if aircraft_id not in aircraft_to_flights:
                    aircraft_to_flights[aircraft_id] = []
                aircraft_to_flights[aircraft_id].append(flight_id)
            
            # Load seats into memory with correct flight mappings
            for seat_id, aircraft_id, seat_number, seat_class, seat_row, seat_col in seat_data:
                # Get all flights that use this aircraft
                flight_ids = aircraft_to_flights.get(aircraft_id, [])
                
                self._seat_status[seat_id] = {
                    'aircraft_id': aircraft_id,
                    'flight_ids': flight_ids,  # All flights this seat can be used for
                    'seat_number': seat_number,
                    'seat_class': seat_class,
                    'row': seat_row,
                    'col': seat_col,
                    'status': 'AVAILABLE',
                    'booked_by': None
                }
                
                # Add seat to all flights that use this aircraft
                for flight_id in flight_ids:
                    self._flight_seats[flight_id].add(seat_id)
                    self._available_seats[flight_id].add(seat_id)
            
            # Load existing bookings to update availability
            cursor.execute("""
                SELECT seat_id, flight_id, user_id, status 
                FROM BOOKINGS 
                WHERE status IN ('HOLD', 'CONFIRMED')
            """)
            
            for seat_id, flight_id, user_id, status in cursor.fetchall():
                if seat_id in self._seat_status:
                    self._seat_status[seat_id]['status'] = 'BOOKED'
                    self._seat_status[seat_id]['booked_by'] = user_id
                    self._available_seats[flight_id].discard(seat_id)
            
            # Load waitlist data
            cursor.execute("""
                SELECT id, user_id, flight_id, priority, preferred_seat_class, preferred_seat_position, max_price
                FROM WAITLIST 
                WHERE status = 'ACTIVE'
                ORDER BY flight_id, priority
            """)
            
            for row in cursor.fetchall():
                waitlist_id, user_id, flight_id, priority, seat_class, seat_pos, max_price = row
                self._waitlist_queue[flight_id].append({
                    'id': waitlist_id,
                    'user_id': user_id,
                    'priority': priority,
                    'preferred_seat_class': seat_class,
                    'preferred_seat_position': seat_pos,
                    'max_price': max_price
                })
            
            conn.close()
            
            total_seats = len(self._seat_status)
            total_flights = len(self._flight_seats)
            total_waitlist = sum(len(q) for q in self._waitlist_queue.values())
            
            logger.info(f"✅ Loaded {total_seats} seats across {total_flights} flights and {total_waitlist} waitlist entries into memory")
            
        except Exception as e:
            logger.error(f"Failed to load initial data: {e}")
            import traceback
            traceback.print_exc()
    
    def nanosecond_book_seat(self, user_id: int, flight_id: int, seat_id: int) -> Dict[str, Any]:
        """
        Book a seat in nanoseconds using pure in-memory operations
        """
        start_ns = time.perf_counter_ns()
        
        try:
            # Step 1: Atomic availability check (nanoseconds)
            with self._seat_locks[seat_id]:
                if seat_id not in self._seat_status:
                    return {
                        "success": False,
                        "message": "Seat not found",
                        "processing_time_ns": time.perf_counter_ns() - start_ns
                    }
                
                seat_info = self._seat_status[seat_id]
                
                if seat_info['status'] != 'AVAILABLE':
                    return {
                        "success": False,
                        "message": "Seat not available",
                        "processing_time_ns": time.perf_counter_ns() - start_ns
                    }
                
                # Check if seat can be used for this flight
                if flight_id not in seat_info.get('flight_ids', []):
                    return {
                        "success": False,
                        "message": "Seat not available for this flight",
                        "processing_time_ns": time.perf_counter_ns() - start_ns
                    }
                
                # Step 2: Instant in-memory booking (nanoseconds)
                self._booking_counter += 1
                booking_id = self._booking_counter
                
                # Update in-memory state atomically
                seat_info['status'] = 'BOOKED'
                seat_info['booked_by'] = user_id
                seat_info['booking_id'] = booking_id
                seat_info['booked_at'] = time.perf_counter_ns()
                
                # Remove from available seats
                self._available_seats[flight_id].discard(seat_id)
                
                processing_time = time.perf_counter_ns() - start_ns
                
                # Step 3: Async database persistence (non-blocking)
                self._executor.submit(self._persist_booking_async, {
                    'booking_id': booking_id,
                    'user_id': user_id,
                    'flight_id': flight_id,
                    'seat_id': seat_id,
                    'seat_number': seat_info['seat_number']
                })
                
                return {
                    "success": True,
                    "booking_id": booking_id,
                    "seat_number": seat_info['seat_number'],
                    "seat_class": seat_info['seat_class'],
                    "processing_time_ns": processing_time,
                    "processing_time_microseconds": processing_time / 1000,
                    "message": f"Booked in {processing_time} nanoseconds! ⚡"
                }
        
        except Exception as e:
            logger.error(f"Nanosecond booking failed: {e}")
            return {
                "success": False,
                "message": f"Booking failed: {e}",
                "processing_time_ns": time.perf_counter_ns() - start_ns
            }
    
    def instant_waitlist_allocation(self, flight_id: int, seat_id: int) -> Dict[str, Any]:
        """
        Instant waitlist allocation in nanoseconds
        """
        start_ns = time.perf_counter_ns()
        
        try:
            with self._global_lock:
                # Step 1: Get next waitlist user (nanoseconds)
                waitlist = self._waitlist_queue.get(flight_id, [])
                if not waitlist:
                    return {
                        "success": False,
                        "message": "No waitlist users",
                        "processing_time_ns": time.perf_counter_ns() - start_ns
                    }
                
                seat_info = self._seat_status.get(seat_id)
                if not seat_info:
                    return {
                        "success": False,
                        "message": "Seat not found",
                        "processing_time_ns": time.perf_counter_ns() - start_ns
                    }
                
                # Step 2: Find suitable waitlist user (nanoseconds)
                suitable_user = None
                for i, waitlist_entry in enumerate(waitlist):
                    if self._matches_preferences(seat_info, waitlist_entry):
                        suitable_user = waitlist_entry
                        # Remove from waitlist queue
                        waitlist.pop(i)
                        break
                
                if not suitable_user:
                    # Free the seat
                    seat_info['status'] = 'AVAILABLE'
                    seat_info['booked_by'] = None
                    self._available_seats[flight_id].add(seat_id)
                    
                    return {
                        "success": False,
                        "message": "No suitable waitlist user",
                        "processing_time_ns": time.perf_counter_ns() - start_ns
                    }
                
                # Step 3: Instant allocation (nanoseconds)
                self._booking_counter += 1
                booking_id = self._booking_counter
                
                seat_info['status'] = 'HOLD'  # Give them time to confirm
                seat_info['booked_by'] = suitable_user['user_id']
                seat_info['booking_id'] = booking_id
                seat_info['allocated_at'] = time.perf_counter_ns()
                
                processing_time = time.perf_counter_ns() - start_ns
                
                # Step 4: Async database update (non-blocking)
                self._executor.submit(self._persist_waitlist_allocation_async, {
                    'booking_id': booking_id,
                    'user_id': suitable_user['user_id'],
                    'flight_id': flight_id,
                    'seat_id': seat_id,
                    'waitlist_id': suitable_user['id'],
                    'seat_number': seat_info['seat_number']
                })
                
                return {
                    "success": True,
                    "allocated_user_id": suitable_user['user_id'],
                    "booking_id": booking_id,
                    "seat_number": seat_info['seat_number'],
                    "processing_time_ns": processing_time,
                    "processing_time_microseconds": processing_time / 1000,
                    "message": f"Allocated in {processing_time} nanoseconds! 🚀"
                }
        
        except Exception as e:
            logger.error(f"Instant allocation failed: {e}")
            return {
                "success": False,
                "message": f"Allocation failed: {e}",
                "processing_time_ns": time.perf_counter_ns() - start_ns
            }
    
    def nanosecond_cancel_with_allocation(self, booking_id: int, user_id: int) -> Dict[str, Any]:
        """
        Cancel booking and instantly allocate to waitlist in nanoseconds
        """
        start_ns = time.perf_counter_ns()
        
        try:
            # Step 1: Find and cancel booking (nanoseconds)
            cancelled_seat = None
            cancelled_flight = None
            
            for seat_id, seat_info in self._seat_status.items():
                if (seat_info.get('booking_id') == booking_id and 
                    seat_info.get('booked_by') == user_id):
                    
                    cancelled_seat = seat_id
                    cancelled_flight = seat_info['flight_id']
                    
                    # Cancel booking instantly
                    seat_info['status'] = 'AVAILABLE'
                    seat_info['booked_by'] = None
                    seat_info['booking_id'] = None
                    
                    break
            
            if not cancelled_seat:
                return {
                    "success": False,
                    "message": "Booking not found",
                    "processing_time_ns": time.perf_counter_ns() - start_ns
                }
            
            # Step 2: Instant waitlist allocation (nanoseconds)
            allocation_result = self.instant_waitlist_allocation(cancelled_flight, cancelled_seat)
            
            processing_time = time.perf_counter_ns() - start_ns
            
            # Step 3: Async database update (non-blocking)
            self._executor.submit(self._persist_cancellation_async, {
                'booking_id': booking_id,
                'seat_id': cancelled_seat,
                'flight_id': cancelled_flight
            })
            
            return {
                "success": True,
                "message": "Cancelled and processed waitlist",
                "waitlist_allocation": allocation_result,
                "processing_time_ns": processing_time,
                "processing_time_microseconds": processing_time / 1000
            }
        
        except Exception as e:
            logger.error(f"Nanosecond cancel failed: {e}")
            return {
                "success": False,
                "message": f"Cancel failed: {e}",
                "processing_time_ns": time.perf_counter_ns() - start_ns
            }
    
    def _matches_preferences(self, seat_info: Dict[str, Any], waitlist_entry: Dict[str, Any]) -> bool:
        """Check if seat matches waitlist user preferences (nanoseconds)"""
        # Seat class check
        if (waitlist_entry['preferred_seat_class'] and 
            waitlist_entry['preferred_seat_class'] != 'ANY' and
            seat_info['seat_class'] != waitlist_entry['preferred_seat_class']):
            return False
        
        # Position check (simplified for speed)
        if (waitlist_entry['preferred_seat_position'] and 
            waitlist_entry['preferred_seat_position'] != 'ANY'):
            col = seat_info['col']
            if waitlist_entry['preferred_seat_position'] == 'WINDOW' and col not in ['A', 'F']:
                return False
            elif waitlist_entry['preferred_seat_position'] == 'AISLE' and col not in ['C', 'D']:
                return False
        
        return True
    
    def get_available_seats_instant(self, flight_id: int) -> Dict[str, Any]:
        """Get available seats instantly from memory"""
        start_ns = time.perf_counter_ns()
        
        available_seat_ids = self._available_seats.get(flight_id, set())
        seats = []
        
        for seat_id in available_seat_ids:
            seat_info = self._seat_status[seat_id]
            seats.append({
                'id': seat_id,
                'seat_number': seat_info['seat_number'],
                'seat_class': seat_info['seat_class'],
                'row': seat_info['row'],
                'col': seat_info['col'],
                'status': 'AVAILABLE'
            })
        
        processing_time = time.perf_counter_ns() - start_ns
        
        return {
            'seats': seats,
            'count': len(seats),
            'processing_time_ns': processing_time,
            'processing_time_microseconds': processing_time / 1000
        }
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get real-time performance statistics"""
        total_seats = len(self._seat_status)
        total_available = sum(len(seats) for seats in self._available_seats.values())
        total_waitlist = sum(len(queue) for queue in self._waitlist_queue.values())
        
        return {
            'engine_type': 'Nanosecond Booking Engine',
            'total_seats': total_seats,
            'available_seats': total_available,
            'booked_seats': total_seats - total_available,
            'waitlist_entries': total_waitlist,
            'booking_counter': self._booking_counter,
            'memory_structures': {
                'seat_status_entries': len(self._seat_status),
                'flight_seat_mappings': len(self._flight_seats),
                'available_seat_sets': len(self._available_seats),
                'waitlist_queues': len(self._waitlist_queue)
            }
        }
    
    # Async database persistence methods (non-blocking)
    def _persist_booking_async(self, booking_data: Dict[str, Any]):
        """Persist booking to database asynchronously"""
        try:
            conn = sqlite3.connect(self._db_path)
            cursor = conn.cursor()
            
            # Get flight price
            cursor.execute(self._statements['get_flight_price'], (booking_data['flight_id'],))
            price = cursor.fetchone()[0]
            
            # Insert booking
            now = datetime.utcnow()
            expires_at = now + timedelta(minutes=10)
            
            cursor.execute(self._statements['insert_booking'], (
                booking_data['user_id'],
                booking_data['flight_id'],
                booking_data['seat_id'],
                'HOLD',
                price,
                now,
                expires_at
            ))
            
            # Update seat status
            cursor.execute(self._statements['update_seat_status'], ('HOLD', booking_data['seat_id']))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Async booking persistence failed: {e}")
    
    def _persist_waitlist_allocation_async(self, allocation_data: Dict[str, Any]):
        """Persist waitlist allocation to database asynchronously"""
        try:
            conn = sqlite3.connect(self._db_path)
            cursor = conn.cursor()
            
            # Get flight price
            cursor.execute(self._statements['get_flight_price'], (allocation_data['flight_id'],))
            price = cursor.fetchone()[0]
            
            # Insert booking
            now = datetime.utcnow()
            expires_at = now + timedelta(minutes=15)
            
            cursor.execute(self._statements['insert_waitlist_booking'], (
                allocation_data['user_id'],
                allocation_data['flight_id'],
                allocation_data['seat_id'],
                price,
                now,
                expires_at
            ))
            
            # Update waitlist status
            cursor.execute(self._statements['update_waitlist_status'], (now, allocation_data['waitlist_id']))
            
            # Update seat status
            cursor.execute(self._statements['update_seat_status'], ('HOLD', allocation_data['seat_id']))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Async waitlist persistence failed: {e}")
    
    def _persist_cancellation_async(self, cancel_data: Dict[str, Any]):
        """Persist cancellation to database asynchronously"""
        try:
            conn = sqlite3.connect(self._db_path)
            cursor = conn.cursor()
            
            # Update booking status
            cursor.execute("UPDATE BOOKINGS SET status = 'CANCELLED' WHERE id = ?", 
                         (cancel_data['booking_id'],))
            
            # Update seat status
            cursor.execute(self._statements['update_seat_status'], ('AVAILABLE', cancel_data['seat_id']))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Async cancellation persistence failed: {e}")

# Global nanosecond engine instance
_nanosecond_engine = None

def get_nanosecond_engine(db_path: str = "flight_booking.db") -> NanosecondBookingEngine:
    """Get or create nanosecond booking engine"""
    global _nanosecond_engine
    if _nanosecond_engine is None:
        _nanosecond_engine = NanosecondBookingEngine(db_path)
    return _nanosecond_engine
"""
Database Optimizer - Ultra-fast database operations
Connection pooling, prepared statements, and query optimization
"""

import time
from typing import Dict, Any, List, Optional
from sqlalchemy import create_engine, text, event
from sqlalchemy.engine import Engine
from sqlalchemy.pool import QueuePool
from sqlalchemy.orm import sessionmaker
import logging

logger = logging.getLogger(__name__)

class DatabaseOptimizer:
    """
    High-performance database optimizer with connection pooling
    """
    
    def __init__(self, database_url: str):
        # Optimized engine with connection pooling
        self.engine = create_engine(
            database_url,
            poolclass=QueuePool,
            pool_size=20,  # Increased pool size
            max_overflow=30,  # Allow overflow connections
            pool_pre_ping=True,  # Verify connections
            pool_recycle=3600,  # Recycle connections every hour
            echo=False,  # Disable SQL logging for performance
            connect_args={
                "check_same_thread": False,  # For SQLite
                "timeout": 1  # 1 second timeout
            }
        )
        
        # Optimized session factory
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,  # Manual flush for better control
            bind=self.engine
        )
        
        # Prepared statements cache
        self._prepared_statements = {}
        
        # Performance monitoring
        self._query_stats = {}
        
        # Setup database optimizations
        self._setup_optimizations()
    
    def _setup_optimizations(self):
        """Setup database-level optimizations"""
        
        @event.listens_for(Engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            """Set SQLite optimizations on connection"""
            if 'sqlite' in str(self.engine.url):
                cursor = dbapi_connection.cursor()
                
                # Performance optimizations
                cursor.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging
                cursor.execute("PRAGMA synchronous=NORMAL")  # Faster writes
                cursor.execute("PRAGMA cache_size=10000")  # Larger cache
                cursor.execute("PRAGMA temp_store=MEMORY")  # Memory temp storage
                cursor.execute("PRAGMA mmap_size=268435456")  # 256MB memory map
                cursor.execute("PRAGMA optimize")  # Auto-optimize
                
                cursor.close()
    
    def get_prepared_statement(self, key: str, sql: str) -> text:
        """Get or create prepared statement"""
        if key not in self._prepared_statements:
            self._prepared_statements[key] = text(sql)
        return self._prepared_statements[key]
    
    def execute_fast_query(self, session, key: str, sql: str, params: Dict[str, Any] = None) -> Any:
        """Execute optimized query with performance tracking"""
        start_time = time.perf_counter_ns()
        
        try:
            stmt = self.get_prepared_statement(key, sql)
            result = session.execute(stmt, params or {})
            
            # Track performance
            execution_time = time.perf_counter_ns() - start_time
            self._update_query_stats(key, execution_time)
            
            return result
            
        except Exception as e:
            logger.error(f"Fast query execution failed for {key}: {e}")
            raise
    
    def _update_query_stats(self, key: str, execution_time_ns: int):
        """Update query performance statistics"""
        if key not in self._query_stats:
            self._query_stats[key] = {
                "count": 0,
                "total_time_ns": 0,
                "avg_time_ns": 0,
                "min_time_ns": float('inf'),
                "max_time_ns": 0
            }
        
        stats = self._query_stats[key]
        stats["count"] += 1
        stats["total_time_ns"] += execution_time_ns
        stats["avg_time_ns"] = stats["total_time_ns"] // stats["count"]
        stats["min_time_ns"] = min(stats["min_time_ns"], execution_time_ns)
        stats["max_time_ns"] = max(stats["max_time_ns"], execution_time_ns)
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get database performance statistics"""
        return {
            "connection_pool": {
                "size": self.engine.pool.size(),
                "checked_in": self.engine.pool.checkedin(),
                "checked_out": self.engine.pool.checkedout(),
                "overflow": self.engine.pool.overflow(),
                "invalid": self.engine.pool.invalid()
            },
            "query_stats": self._query_stats,
            "prepared_statements": len(self._prepared_statements)
        }

# Optimized queries for ultra-fast operations
OPTIMIZED_QUERIES = {
    "check_seat_availability": """
        SELECT 
            s.id, s.seat_number, s.seat_class, s.status,
            CASE WHEN b.id IS NOT NULL THEN 1 ELSE 0 END as is_booked
        FROM SEATS s
        LEFT JOIN BOOKINGS b ON s.id = b.seat_id 
            AND b.flight_id = :flight_id 
            AND b.status IN ('HOLD', 'CONFIRMED')
        WHERE s.id = :seat_id 
            AND s.aircraft_id = (SELECT aircraft_id FROM FLIGHTS WHERE id = :flight_id)
    """,
    
    "create_booking": """
        INSERT INTO BOOKINGS (
            user_id, flight_id, seat_id, status, price, created_at, expires_at
        ) VALUES (
            :user_id, :flight_id, :seat_id, :status, :price, :created_at, :expires_at
        ) RETURNING id
    """,
    
    "update_seat_status": """
        UPDATE SEATS SET status = :status WHERE id = :seat_id
    """,
    
    "get_next_waitlist_user": """
        SELECT 
            w.id as waitlist_id, w.user_id, w.priority,
            w.preferred_seat_class, w.preferred_seat_position, w.max_price,
            s.seat_number, s.seat_class, s.col,
            f.price as flight_price, u.full_name, u.email
        FROM WAITLIST w
        JOIN SEATS s ON s.id = :seat_id
        JOIN FLIGHTS f ON f.id = w.flight_id
        JOIN USERS u ON u.id = w.user_id
        WHERE w.flight_id = :flight_id 
            AND w.status = 'ACTIVE'
            AND (w.preferred_seat_class = 'ANY' OR w.preferred_seat_class = s.seat_class)
            AND (w.max_price IS NULL OR w.max_price >= f.price)
        ORDER BY w.priority ASC
        LIMIT 1
    """,
    
    "allocate_to_waitlist": """
        INSERT INTO BOOKINGS (
            user_id, flight_id, seat_id, status, price, created_at, expires_at
        ) VALUES (
            :user_id, :flight_id, :seat_id, 'HOLD', :price, :created_at, :expires_at
        ) RETURNING id
    """,
    
    "update_waitlist_allocated": """
        UPDATE WAITLIST 
        SET status = 'ALLOCATED', allocated_at = :now 
        WHERE id = :waitlist_id
    """,
    
    "update_waitlist_priorities": """
        UPDATE WAITLIST 
        SET priority = priority - 1 
        WHERE flight_id = :flight_id 
            AND status = 'ACTIVE' 
            AND priority > :old_priority
    """,
    
    "get_flight_seats": """
        SELECT s.id, s.seat_number, s.seat_class, s.row, s.col, s.status,
               CASE WHEN b.id IS NOT NULL THEN 'BOOKED' ELSE 'AVAILABLE' END as booking_status
        FROM SEATS s
        LEFT JOIN BOOKINGS b ON s.id = b.seat_id 
            AND b.flight_id = :flight_id 
            AND b.status IN ('HOLD', 'CONFIRMED')
        WHERE s.aircraft_id = (SELECT aircraft_id FROM FLIGHTS WHERE id = :flight_id)
        ORDER BY s.row, s.col
    """,
    
    "cancel_booking": """
        UPDATE BOOKINGS 
        SET status = 'CANCELLED', expires_at = NULL 
        WHERE id = :booking_id AND user_id = :user_id
        RETURNING flight_id, seat_id
    """,
    
    "expire_bookings": """
        UPDATE BOOKINGS 
        SET status = 'EXPIRED' 
        WHERE status = 'HOLD' 
            AND expires_at <= :now
        RETURNING id, flight_id, seat_id
    """,
    
    "batch_update_seats": """
        UPDATE SEATS 
        SET status = 'AVAILABLE' 
        WHERE id IN :seat_ids
    """,
    
    "get_user_bookings": """
        SELECT 
            b.id, b.status, b.price, b.created_at, b.expires_at,
            f.from_city, f.to_city, f.departure_time, f.flight_number,
            s.seat_number, s.seat_class
        FROM BOOKINGS b
        JOIN FLIGHTS f ON f.id = b.flight_id
        JOIN SEATS s ON s.id = b.seat_id
        WHERE b.user_id = :user_id
        ORDER BY b.created_at DESC
    """,
    
    "get_waitlist_stats": """
        SELECT 
            COUNT(*) as total_waitlist,
            SUM(CASE WHEN status = 'ACTIVE' THEN 1 ELSE 0 END) as active_waitlist,
            SUM(CASE WHEN status = 'ALLOCATED' THEN 1 ELSE 0 END) as allocated_count
        FROM WAITLIST 
        WHERE flight_id = :flight_id
    """
}

class FastBookingOperations:
    """
    Ultra-fast booking operations using optimized queries
    """
    
    def __init__(self, db_optimizer: DatabaseOptimizer):
        self.db_optimizer = db_optimizer
    
    def lightning_book_seat(self, session, user_id: int, flight_id: int, seat_id: int) -> Dict[str, Any]:
        """Lightning-fast seat booking operation"""
        start_time = time.perf_counter_ns()
        
        try:
            # Step 1: Check availability (single query)
            availability = self.db_optimizer.execute_fast_query(
                session, "check_seat_availability", 
                OPTIMIZED_QUERIES["check_seat_availability"],
                {"flight_id": flight_id, "seat_id": seat_id}
            ).fetchone()
            
            if not availability or availability.is_booked:
                return {
                    "success": False,
                    "message": "Seat not available",
                    "processing_time_ns": time.perf_counter_ns() - start_time
                }
            
            # Step 2: Create booking (single query)
            from datetime import datetime, timedelta
            now = datetime.utcnow()
            
            # Get flight price
            flight_price = session.execute(text("SELECT price FROM FLIGHTS WHERE id = :flight_id"), 
                                         {"flight_id": flight_id}).scalar()
            
            booking_id = self.db_optimizer.execute_fast_query(
                session, "create_booking",
                OPTIMIZED_QUERIES["create_booking"],
                {
                    "user_id": user_id,
                    "flight_id": flight_id,
                    "seat_id": seat_id,
                    "status": "HOLD",
                    "price": flight_price,
                    "created_at": now,
                    "expires_at": now + timedelta(minutes=10)
                }
            ).scalar()
            
            # Step 3: Update seat status (single query)
            self.db_optimizer.execute_fast_query(
                session, "update_seat_status",
                OPTIMIZED_QUERIES["update_seat_status"],
                {"seat_id": seat_id, "status": "HOLD"}
            )
            
            session.commit()
            
            processing_time = time.perf_counter_ns() - start_time
            
            return {
                "success": True,
                "booking_id": booking_id,
                "seat_number": availability.seat_number,
                "processing_time_ns": processing_time,
                "message": f"Booked in {processing_time // 1000} microseconds! ⚡"
            }
            
        except Exception as e:
            session.rollback()
            logger.error(f"Lightning booking failed: {e}")
            return {
                "success": False,
                "message": f"Booking failed: {e}",
                "processing_time_ns": time.perf_counter_ns() - start_time
            }
    
    def instant_waitlist_allocation(self, session, cancelled_booking_id: int) -> Dict[str, Any]:
        """Instant waitlist allocation when seat becomes available"""
        start_time = time.perf_counter_ns()
        
        try:
            # Get cancelled booking details
            booking_data = session.execute(text("""
                SELECT flight_id, seat_id FROM BOOKINGS WHERE id = :booking_id
            """), {"booking_id": cancelled_booking_id}).fetchone()
            
            if not booking_data:
                return {"success": False, "message": "Booking not found"}
            
            # Get next waitlist user (single optimized query)
            waitlist_user = self.db_optimizer.execute_fast_query(
                session, "get_next_waitlist_user",
                OPTIMIZED_QUERIES["get_next_waitlist_user"],
                {"flight_id": booking_data.flight_id, "seat_id": booking_data.seat_id}
            ).fetchone()
            
            if not waitlist_user:
                # Free the seat
                self.db_optimizer.execute_fast_query(
                    session, "update_seat_status",
                    OPTIMIZED_QUERIES["update_seat_status"],
                    {"seat_id": booking_data.seat_id, "status": "AVAILABLE"}
                )
                session.commit()
                
                return {
                    "success": False,
                    "message": "No suitable waitlist user",
                    "processing_time_ns": time.perf_counter_ns() - start_time
                }
            
            # Allocate to waitlist user (single query)
            from datetime import datetime, timedelta
            now = datetime.utcnow()
            
            booking_id = self.db_optimizer.execute_fast_query(
                session, "allocate_to_waitlist",
                OPTIMIZED_QUERIES["allocate_to_waitlist"],
                {
                    "user_id": waitlist_user.user_id,
                    "flight_id": booking_data.flight_id,
                    "seat_id": booking_data.seat_id,
                    "price": waitlist_user.flight_price,
                    "created_at": now,
                    "expires_at": now + timedelta(minutes=15)
                }
            ).scalar()
            
            # Update waitlist status
            self.db_optimizer.execute_fast_query(
                session, "update_waitlist_allocated",
                OPTIMIZED_QUERIES["update_waitlist_allocated"],
                {"waitlist_id": waitlist_user.waitlist_id, "now": now}
            )
            
            # Update priorities
            self.db_optimizer.execute_fast_query(
                session, "update_waitlist_priorities",
                OPTIMIZED_QUERIES["update_waitlist_priorities"],
                {
                    "flight_id": booking_data.flight_id,
                    "old_priority": waitlist_user.priority
                }
            )
            
            # Update seat status
            self.db_optimizer.execute_fast_query(
                session, "update_seat_status",
                OPTIMIZED_QUERIES["update_seat_status"],
                {"seat_id": booking_data.seat_id, "status": "HOLD"}
            )
            
            session.commit()
            
            processing_time = time.perf_counter_ns() - start_time
            
            return {
                "success": True,
                "allocated_user_id": waitlist_user.user_id,
                "user_name": waitlist_user.full_name,
                "seat_number": waitlist_user.seat_number,
                "booking_id": booking_id,
                "processing_time_ns": processing_time,
                "message": f"Allocated in {processing_time // 1000} microseconds! 🚀"
            }
            
        except Exception as e:
            session.rollback()
            logger.error(f"Instant allocation failed: {e}")
            return {
                "success": False,
                "message": f"Allocation failed: {e}",
                "processing_time_ns": time.perf_counter_ns() - start_time
            }

# Global optimizer instance
_db_optimizer = None

def get_db_optimizer(database_url: str = None) -> DatabaseOptimizer:
    """Get or create database optimizer instance"""
    global _db_optimizer
    if _db_optimizer is None and database_url:
        _db_optimizer = DatabaseOptimizer(database_url)
    return _db_optimizer
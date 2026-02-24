"""
Migration script to add new flight search fields
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.flight import Flight
from app.database import Base
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_flight_fields():
    """Add new fields to flights table for enhanced search"""
    
    # Create engine and session
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        logger.info("Starting flight fields migration...")
        
        # Add new columns to flights table
        migration_queries = [
            "ALTER TABLE FLIGHTS ADD COLUMN IF NOT EXISTS from_airport_code VARCHAR(10)",
            "ALTER TABLE FLIGHTS ADD COLUMN IF NOT EXISTS to_airport_code VARCHAR(10)",
            "ALTER TABLE FLIGHTS ADD COLUMN IF NOT EXISTS duration INTEGER",
            "ALTER TABLE FLIGHTS ADD COLUMN IF NOT EXISTS airline VARCHAR(100)",
            "ALTER TABLE FLIGHTS ADD COLUMN IF NOT EXISTS flight_number VARCHAR(20)",
            "ALTER TABLE FLIGHTS ADD COLUMN IF NOT EXISTS aircraft_type VARCHAR(50)"
        ]
        
        for query in migration_queries:
            try:
                db.execute(text(query))
                logger.info(f"Executed: {query}")
            except Exception as e:
                logger.warning(f"Query may have already been executed: {query} - {e}")
        
        db.commit()
        logger.info("Migration queries committed successfully")
        
        # Update existing flights with sample data
        flights = db.query(Flight).all()
        
        # Airport codes mapping
        airport_codes = {
            "Mumbai": "BOM",
            "Delhi": "DEL", 
            "Bangalore": "BLR",
            "Chennai": "MAA",
            "Kolkata": "CCU",
            "Hyderabad": "HYD",
            "Pune": "PNQ",
            "Ahmedabad": "AMD",
            "Kochi": "COK",
            "Goa": "GOI",
            "Jaipur": "JAI",
            "Lucknow": "LKO",
            "New York": "JFK",
            "Los Angeles": "LAX",
            "London": "LHR",
            "Paris": "CDG",
            "Tokyo": "NRT",
            "Singapore": "SIN"
        }
        
        airlines = [
            "Safe Travel Airways",
            "Dharma Airlines", 
            "Mindful Air",
            "Conscious Travel",
            "Peaceful Journeys"
        ]
        
        aircraft_types = [
            "Airbus A320",
            "Boeing 737",
            "Airbus A321",
            "Boeing 777",
            "Airbus A330"
        ]
        
        for i, flight in enumerate(flights):
            # Calculate duration if not set
            if flight.arrival_time and flight.departure_time:
                duration_delta = flight.arrival_time - flight.departure_time
                flight.duration = int(duration_delta.total_seconds() / 60)  # Convert to minutes
            
            # Set airport codes
            flight.from_airport_code = airport_codes.get(flight.from_city, "UNK")
            flight.to_airport_code = airport_codes.get(flight.to_city, "UNK")
            
            # Set airline and flight number
            flight.airline = airlines[i % len(airlines)]
            flight.flight_number = f"ST{1000 + flight.id}"
            
            # Set aircraft type
            flight.aircraft_type = aircraft_types[i % len(aircraft_types)]
        
        db.commit()
        logger.info(f"Updated {len(flights)} flights with new field data")
        
        logger.info("Flight fields migration completed successfully!")
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    migrate_flight_fields()
"""
Service to seed flight data for enhanced search functionality
"""

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.flight import Flight
from app.models.aircraft import Aircraft
import random
import logging

logger = logging.getLogger(__name__)

def seed_flight_data(db: Session):
    """Seed comprehensive flight data for search testing"""
    
    # Check if we already have enough flights
    existing_flights = db.query(Flight).count()
    if existing_flights >= 50:
        logger.info(f"Already have {existing_flights} flights, skipping seed")
        return
    
    # Get available aircraft
    aircraft = db.query(Aircraft).first()
    if not aircraft:
        logger.error("No aircraft found. Please seed aircraft data first.")
        return
    
    # Indian cities with airport codes
    indian_cities = [
        {"city": "Mumbai", "code": "BOM"},
        {"city": "Delhi", "code": "DEL"},
        {"city": "Bangalore", "code": "BLR"},
        {"city": "Chennai", "code": "MAA"},
        {"city": "Kolkata", "code": "CCU"},
        {"city": "Hyderabad", "code": "HYD"},
        {"city": "Pune", "code": "PNQ"},
        {"city": "Ahmedabad", "code": "AMD"},
        {"city": "Kochi", "code": "COK"},
        {"city": "Goa", "code": "GOI"},
        {"city": "Jaipur", "code": "JAI"},
        {"city": "Lucknow", "code": "LKO"},
        {"city": "Indore", "code": "IDR"},
        {"city": "Bhubaneswar", "code": "BBI"},
        {"city": "Coimbatore", "code": "CJB"}
    ]
    
    # International cities
    international_cities = [
        {"city": "New York", "code": "JFK"},
        {"city": "Los Angeles", "code": "LAX"},
        {"city": "London", "code": "LHR"},
        {"city": "Paris", "code": "CDG"},
        {"city": "Tokyo", "code": "NRT"},
        {"city": "Singapore", "code": "SIN"},
        {"city": "Dubai", "code": "DXB"},
        {"city": "Bangkok", "code": "BKK"}
    ]
    
    all_cities = indian_cities + international_cities
    
    airlines = [
        "Safe Travel Airways",
        "Dharma Airlines", 
        "Mindful Air",
        "Conscious Travel",
        "Peaceful Journeys",
        "Karma Airlines",
        "Zen Airways",
        "Enlightened Travel"
    ]
    
    aircraft_types = [
        "Airbus A320",
        "Boeing 737-800",
        "Airbus A321",
        "Boeing 777-300ER",
        "Airbus A330-300",
        "Boeing 787-9",
        "Airbus A350-900"
    ]
    
    # Generate flights for the next 30 days
    base_date = datetime.now().replace(hour=6, minute=0, second=0, microsecond=0)
    
    flights_to_create = []
    
    for day_offset in range(30):  # Next 30 days
        current_date = base_date + timedelta(days=day_offset)
        
        # Create 8-12 flights per day
        daily_flights = random.randint(8, 12)
        
        for _ in range(daily_flights):
            # Select random cities (ensure different from/to)
            from_city_data = random.choice(all_cities)
            to_city_data = random.choice([c for c in all_cities if c != from_city_data])
            
            # Random departure time during the day
            departure_hour = random.randint(6, 22)
            departure_minute = random.choice([0, 15, 30, 45])
            departure_time = current_date.replace(hour=departure_hour, minute=departure_minute)
            
            # Calculate flight duration based on route type
            is_international = (from_city_data in international_cities or 
                              to_city_data in international_cities)
            
            if is_international:
                # International flights: 3-15 hours
                duration_minutes = random.randint(180, 900)
                base_price = random.randint(25000, 80000)
            else:
                # Domestic flights: 1-4 hours
                duration_minutes = random.randint(60, 240)
                base_price = random.randint(3000, 15000)
            
            arrival_time = departure_time + timedelta(minutes=duration_minutes)
            
            # Add some price variation
            price_variation = random.uniform(0.8, 1.3)
            final_price = int(base_price * price_variation)
            
            # Select airline and aircraft
            airline = random.choice(airlines)
            aircraft_type = random.choice(aircraft_types)
            
            # Generate flight number
            airline_code = "ST" if "Safe Travel" in airline else airline[:2].upper()
            flight_number = f"{airline_code}{random.randint(100, 999)}"
            
            flight = Flight(
                from_city=from_city_data["city"],
                to_city=to_city_data["city"],
                from_airport_code=from_city_data["code"],
                to_airport_code=to_city_data["code"],
                departure_time=departure_time,
                arrival_time=arrival_time,
                duration=duration_minutes,
                price=final_price,
                airline=airline,
                flight_number=flight_number,
                aircraft_type=aircraft_type,
                aircraft_id=aircraft.id
            )
            
            flights_to_create.append(flight)
    
    # Batch insert flights
    try:
        db.add_all(flights_to_create)
        db.commit()
        logger.info(f"Successfully seeded {len(flights_to_create)} flights")
        
        # Log some statistics
        total_flights = db.query(Flight).count()
        unique_routes = db.query(Flight.from_city, Flight.to_city).distinct().count()
        from sqlalchemy import func
        price_range = db.query(
            func.min(Flight.price),
            func.max(Flight.price),
            func.avg(Flight.price)
        ).first()
        
        logger.info(f"Flight database statistics:")
        logger.info(f"  Total flights: {total_flights}")
        logger.info(f"  Unique routes: {unique_routes}")
        logger.info(f"  Price range: ₹{price_range[0]:.0f} - ₹{price_range[1]:.0f}")
        logger.info(f"  Average price: ₹{price_range[2]:.0f}")
        
    except Exception as e:
        logger.error(f"Failed to seed flight data: {e}")
        db.rollback()
        raise

def create_popular_routes(db: Session):
    """Create additional flights for popular routes to improve search results"""
    
    popular_routes = [
        ("Mumbai", "Delhi"),
        ("Delhi", "Mumbai"), 
        ("Bangalore", "Mumbai"),
        ("Mumbai", "Bangalore"),
        ("Chennai", "Delhi"),
        ("Delhi", "Chennai"),
        ("Hyderabad", "Mumbai"),
        ("Mumbai", "Hyderabad"),
        ("Kolkata", "Delhi"),
        ("Delhi", "Kolkata")
    ]
    
    aircraft = db.query(Aircraft).first()
    if not aircraft:
        return
    
    base_date = datetime.now().replace(hour=6, minute=0, second=0, microsecond=0)
    
    for from_city, to_city in popular_routes:
        # Create 3-5 flights per day for next 7 days for popular routes
        for day_offset in range(7):
            current_date = base_date + timedelta(days=day_offset)
            flights_per_day = random.randint(3, 5)
            
            for i in range(flights_per_day):
                departure_hour = 6 + (i * 4) + random.randint(0, 2)  # Spread throughout day
                departure_hour = min(departure_hour, 22)  # Cap at 22:00
                departure_time = current_date.replace(hour=departure_hour, minute=random.choice([0, 30]))
                
                duration_minutes = random.randint(90, 180)  # 1.5-3 hours for domestic
                arrival_time = departure_time + timedelta(minutes=duration_minutes)
                
                price = random.randint(4000, 12000)
                
                flight = Flight(
                    from_city=from_city,
                    to_city=to_city,
                    from_airport_code="BOM" if from_city == "Mumbai" else "DEL",
                    to_airport_code="BOM" if to_city == "Mumbai" else "DEL", 
                    departure_time=departure_time,
                    arrival_time=arrival_time,
                    duration=duration_minutes,
                    price=price,
                    airline="Safe Travel Airways",
                    flight_number=f"ST{random.randint(1000, 1999)}",
                    aircraft_type="Airbus A320",
                    aircraft_id=aircraft.id
                )
                
                db.add(flight)
    
    try:
        db.commit()
        logger.info("Created additional flights for popular routes")
    except Exception as e:
        logger.error(f"Failed to create popular route flights: {e}")
        db.rollback()
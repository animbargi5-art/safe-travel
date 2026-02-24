from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from typing import Optional, List
from datetime import datetime, date
from app.database_dep import get_db
from app.models.flight import Flight
from app.schemas.flight import FlightSearchRequest, FlightSearchResponse

router = APIRouter(prefix="/flights", tags=["Flights"])

@router.get("/search", response_model=List[FlightSearchResponse])
def search_flights(
    from_city: Optional[str] = Query(None, description="Departure city"),
    to_city: Optional[str] = Query(None, description="Destination city"),
    departure_date: Optional[date] = Query(None, description="Departure date (YYYY-MM-DD)"),
    return_date: Optional[date] = Query(None, description="Return date (YYYY-MM-DD)"),
    min_price: Optional[float] = Query(None, description="Minimum price filter"),
    max_price: Optional[float] = Query(None, description="Maximum price filter"),
    sort_by: Optional[str] = Query("price", description="Sort by: price, departure_time, duration"),
    sort_order: Optional[str] = Query("asc", description="Sort order: asc, desc"),
    limit: Optional[int] = Query(50, description="Maximum number of results"),
    db: Session = Depends(get_db)
):
    """
    Enhanced flight search with multiple filters and sorting options
    """
    
    query = db.query(Flight)
    
    # City filters with flexible matching
    if from_city:
        query = query.filter(
            or_(
                Flight.from_city.ilike(f"%{from_city}%"),
                Flight.from_airport_code.ilike(f"%{from_city}%")
            )
        )
    
    if to_city:
        query = query.filter(
            or_(
                Flight.to_city.ilike(f"%{to_city}%"),
                Flight.to_airport_code.ilike(f"%{to_city}%")
            )
        )
    
    # Date filters
    if departure_date:
        query = query.filter(func.date(Flight.departure_time) == departure_date)
    
    # Price filters
    if min_price is not None:
        query = query.filter(Flight.price >= min_price)
    
    if max_price is not None:
        query = query.filter(Flight.price <= max_price)
    
    # Sorting
    if sort_by == "price":
        if sort_order == "desc":
            query = query.order_by(Flight.price.desc())
        else:
            query = query.order_by(Flight.price.asc())
    elif sort_by == "departure_time":
        if sort_order == "desc":
            query = query.order_by(Flight.departure_time.desc())
        else:
            query = query.order_by(Flight.departure_time.asc())
    elif sort_by == "duration":
        if sort_order == "desc":
            query = query.order_by(Flight.duration.desc())
        else:
            query = query.order_by(Flight.duration.asc())
    else:
        # Default to price ascending
        query = query.order_by(Flight.price.asc())
    
    # Limit results
    query = query.limit(limit)
    
    flights = query.all()
    
    return flights

@router.get("/popular-routes")
def get_popular_routes(db: Session = Depends(get_db)):
    """Get popular flight routes based on booking frequency"""
    
    # Get unique routes with flight counts
    routes = db.query(
        Flight.from_city,
        Flight.to_city,
        func.count(Flight.id).label('flight_count'),
        func.min(Flight.price).label('min_price'),
        func.avg(Flight.price).label('avg_price')
    ).group_by(
        Flight.from_city, 
        Flight.to_city
    ).order_by(
        func.count(Flight.id).desc()
    ).limit(10).all()
    
    return [
        {
            "from_city": route.from_city,
            "to_city": route.to_city,
            "flight_count": route.flight_count,
            "min_price": float(route.min_price) if route.min_price else 0,
            "avg_price": float(route.avg_price) if route.avg_price else 0
        }
        for route in routes
    ]

@router.get("/cities")
def get_available_cities(db: Session = Depends(get_db)):
    """Get list of available departure and destination cities"""
    
    departure_cities = db.query(Flight.from_city).distinct().all()
    destination_cities = db.query(Flight.to_city).distinct().all()
    
    all_cities = set()
    for city in departure_cities:
        all_cities.add(city[0])
    for city in destination_cities:
        all_cities.add(city[0])
    
    return {
        "cities": sorted(list(all_cities)),
        "departure_cities": sorted([city[0] for city in departure_cities]),
        "destination_cities": sorted([city[0] for city in destination_cities])
    }

@router.get("/price-range")
def get_price_range(
    from_city: Optional[str] = None,
    to_city: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get price range for flights, optionally filtered by route"""
    
    query = db.query(
        func.min(Flight.price).label('min_price'),
        func.max(Flight.price).label('max_price'),
        func.avg(Flight.price).label('avg_price')
    )
    
    if from_city:
        query = query.filter(Flight.from_city.ilike(f"%{from_city}%"))
    
    if to_city:
        query = query.filter(Flight.to_city.ilike(f"%{to_city}%"))
    
    result = query.first()
    
    return {
        "min_price": float(result.min_price) if result.min_price else 0,
        "max_price": float(result.max_price) if result.max_price else 0,
        "avg_price": float(result.avg_price) if result.avg_price else 0
    }

@router.get("/{flight_id}")
def get_flight_details(flight_id: int, db: Session = Depends(get_db)):
    """Get detailed information about a specific flight"""
    
    flight = db.query(Flight).filter(Flight.id == flight_id).first()
    
    if not flight:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flight not found"
        )
    
    return flight

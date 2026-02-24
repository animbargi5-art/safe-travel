"""
Smart Recommendations API routes - AI-powered personalized recommendations
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session
import logging

from app.database_dep import get_db
from app.services.ml_service import MLService
from app.services.currency_service import get_currency_service
from app.services.live_monitoring import get_monitoring_service
from app.routes.auth import get_current_user
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/smart-recommendations", tags=["smart-recommendations"])

# Request/Response models
class FlightRecommendationRequest(BaseModel):
    from_city: Optional[str] = None
    to_city: Optional[str] = None
    preferred_currency: Optional[str] = "USD"
    region: Optional[str] = "US"
    limit: int = 10

class SeatRecommendationRequest(BaseModel):
    flight_id: int

class SmartSearchRequest(BaseModel):
    query: str
    preferences: Optional[Dict[str, Any]] = None
    currency: Optional[str] = "USD"
    region: Optional[str] = "US"

class RecommendationResponse(BaseModel):
    id: int
    title: str
    description: str
    score: float
    reasons: List[str]
    price_info: Dict[str, Any]
    metadata: Dict[str, Any]

@router.get("/flight-recommendations")
async def get_flight_recommendations(
    from_city: Optional[str] = None,
    to_city: Optional[str] = None,
    currency: str = "USD",
    region: str = "US",
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get AI-powered personalized flight recommendations"""
    try:
        # Log activity
        monitoring = get_monitoring_service()
        monitoring.log_activity("SMART_RECOMMENDATION_REQUEST", current_user.id, {
            "type": "flight_recommendations",
            "from_city": from_city,
            "to_city": to_city,
            "currency": currency,
            "region": region
        })
        
        # Get ML recommendations
        ml_service = MLService(db)
        recommendations = ml_service.get_personalized_flight_recommendations(
            user_id=current_user.id,
            from_city=from_city,
            to_city=to_city,
            limit=limit
        )
        
        # Enhance with currency conversion
        currency_service = get_currency_service()
        enhanced_recommendations = []
        
        for rec in recommendations:
            # Convert price to user's preferred currency
            price_conversion = currency_service.get_regional_price(
                base_price_usd=rec['price'],
                region=region,
                target_currency=currency
            )
            
            enhanced_rec = {
                "id": rec['id'],
                "title": f"{rec['from_city']} → {rec['to_city']}",
                "description": f"Flight with {rec['airline']} departing {rec['departure_time'].strftime('%Y-%m-%d %H:%M')}",
                "score": rec['score'],
                "reasons": rec['reasons'],
                "price_info": {
                    "original_price_usd": rec['price'],
                    "converted_price": price_conversion['converted_amount'],
                    "currency": currency,
                    "formatted_price": price_conversion['formatted_amount'],
                    "regional_adjustment": price_conversion['regional_multiplier']
                },
                "metadata": {
                    "flight_id": rec['id'],
                    "from_city": rec['from_city'],
                    "to_city": rec['to_city'],
                    "departure_time": rec['departure_time'].isoformat(),
                    "airline": rec['airline'],
                    "recommendation_type": "personalized_flight"
                }
            }
            enhanced_recommendations.append(enhanced_rec)
        
        return {
            "recommendations": enhanced_recommendations,
            "user_preferences": ml_service.get_user_preferences(current_user.id),
            "currency": currency,
            "region": region,
            "total_count": len(enhanced_recommendations)
        }
    
    except Exception as e:
        logger.error(f"Flight recommendations failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to get flight recommendations")

@router.get("/seat-recommendations/{flight_id}")
async def get_seat_recommendations(
    flight_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get AI-powered personalized seat recommendations"""
    try:
        # Log activity
        monitoring = get_monitoring_service()
        monitoring.log_activity("SMART_RECOMMENDATION_REQUEST", current_user.id, {
            "type": "seat_recommendations",
            "flight_id": flight_id
        })
        
        # Get ML seat recommendations
        ml_service = MLService(db)
        recommendations = ml_service.get_seat_recommendations(
            user_id=current_user.id,
            flight_id=flight_id
        )
        
        enhanced_recommendations = []
        for rec in recommendations:
            enhanced_rec = {
                "id": rec['seat_id'],
                "title": f"Seat {rec['seat_number']}",
                "description": f"{rec['seat_class']} class seat in row {rec['row']}, column {rec['col']}",
                "score": rec['score'],
                "reasons": rec['reasons'],
                "price_info": {
                    "base_price": 0,  # Seats don't have separate pricing in this system
                    "currency": "USD"
                },
                "metadata": {
                    "seat_id": rec['seat_id'],
                    "seat_number": rec['seat_number'],
                    "seat_class": rec['seat_class'],
                    "row": rec['row'],
                    "col": rec['col'],
                    "recommendation_type": "personalized_seat"
                }
            }
            enhanced_recommendations.append(enhanced_rec)
        
        return {
            "recommendations": enhanced_recommendations,
            "flight_id": flight_id,
            "total_count": len(enhanced_recommendations)
        }
    
    except Exception as e:
        logger.error(f"Seat recommendations failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to get seat recommendations")

@router.post("/smart-search")
async def smart_search(
    request: SmartSearchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """AI-powered smart search with natural language processing"""
    try:
        # Log activity
        monitoring = get_monitoring_service()
        monitoring.log_activity("SMART_SEARCH_REQUEST", current_user.id, {
            "query": request.query,
            "currency": request.currency,
            "region": request.region
        })
        
        # Parse natural language query
        parsed_query = _parse_search_query(request.query)
        
        # Get ML service
        ml_service = MLService(db)
        currency_service = get_currency_service()
        
        results = []
        
        # Flight search
        if parsed_query.get('type') in ['flight', 'travel', 'trip']:
            flight_recs = ml_service.get_personalized_flight_recommendations(
                user_id=current_user.id,
                from_city=parsed_query.get('from_city'),
                to_city=parsed_query.get('to_city'),
                limit=5
            )
            
            for rec in flight_recs:
                price_conversion = currency_service.get_regional_price(
                    base_price_usd=rec['price'],
                    region=request.region,
                    target_currency=request.currency
                )
                
                results.append({
                    "id": rec['id'],
                    "title": f"✈️ {rec['from_city']} → {rec['to_city']}",
                    "description": f"Smart match: {rec['airline']} flight",
                    "score": rec['score'] + 10,  # Boost for smart search
                    "reasons": ["Smart search match"] + rec['reasons'],
                    "price_info": {
                        "converted_price": price_conversion['converted_amount'],
                        "formatted_price": price_conversion['formatted_amount'],
                        "currency": request.currency
                    },
                    "metadata": {
                        "type": "flight",
                        "flight_id": rec['id'],
                        "search_relevance": "high"
                    }
                })
        
        # Route recommendations based on preferences
        user_preferences = ml_service.get_user_preferences(current_user.id)
        for route in user_preferences.get('preferred_routes', [])[:3]:
            results.append({
                "id": f"route_{len(results)}",
                "title": f"🎯 {route['route']}",
                "description": f"Your frequently traveled route (traveled {route['frequency']} times)",
                "score": route['preference_score'] * 100,
                "reasons": [f"You've traveled this route {route['frequency']} times"],
                "price_info": {
                    "estimated_price": "Varies",
                    "currency": request.currency
                },
                "metadata": {
                    "type": "route_suggestion",
                    "route": route['route'],
                    "frequency": route['frequency']
                }
            })
        
        # Sort by score
        results.sort(key=lambda x: x['score'], reverse=True)
        
        return {
            "query": request.query,
            "parsed_query": parsed_query,
            "results": results[:10],
            "user_preferences_applied": True,
            "currency": request.currency,
            "region": request.region,
            "total_results": len(results)
        }
    
    except Exception as e:
        logger.error(f"Smart search failed: {e}")
        raise HTTPException(status_code=500, detail="Smart search failed")

@router.get("/user-insights")
async def get_user_insights(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive user insights and preferences"""
    try:
        ml_service = MLService(db)
        
        # Get user preferences
        preferences = ml_service.get_user_preferences(current_user.id)
        
        # Get demand predictions for user's preferred routes
        demand_predictions = []
        for route in preferences.get('preferred_routes', [])[:3]:
            prediction = ml_service.predict_demand(route['route'])
            demand_predictions.append(prediction)
        
        # Get booking pattern analysis
        booking_patterns = preferences.get('booking_patterns', {})
        
        insights = {
            "user_id": current_user.id,
            "preferences": preferences,
            "demand_predictions": demand_predictions,
            "booking_insights": {
                "typical_advance_booking": f"{booking_patterns.get('advance_days', 14)} days",
                "price_sensitivity": preferences.get('price_sensitivity', 'medium'),
                "preferred_times": preferences.get('preferred_times', []),
                "seat_preferences": {
                    "class": preferences.get('preferred_seat_class', 'ECONOMY'),
                    "position": preferences.get('preferred_seat_position', 'WINDOW')
                }
            },
            "recommendations": {
                "best_booking_time": f"{booking_patterns.get('advance_days', 14)} days in advance",
                "preferred_departure_times": preferences.get('preferred_times', []),
                "seasonal_trends": preferences.get('seasonal_preferences', {})
            }
        }
        
        return insights
    
    except Exception as e:
        logger.error(f"User insights failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user insights")

@router.get("/trending-destinations")
async def get_trending_destinations(
    currency: str = "USD",
    region: str = "US",
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get trending destinations with AI-powered insights"""
    try:
        # This would typically use real analytics data
        # For demo, we'll create smart trending destinations
        
        currency_service = get_currency_service()
        
        trending_destinations = [
            {
                "destination": "Mumbai",
                "from_cities": ["Delhi", "Bangalore", "Chennai"],
                "trend_score": 95,
                "reasons": ["High booking volume", "Popular business route", "Frequent flights"],
                "avg_price_usd": 8500,
                "seasonal_factor": "High demand"
            },
            {
                "destination": "Dubai",
                "from_cities": ["Mumbai", "Delhi", "Bangalore"],
                "trend_score": 88,
                "reasons": ["International hub", "Business travel", "Tourism peak"],
                "avg_price_usd": 25000,
                "seasonal_factor": "Winter season peak"
            },
            {
                "destination": "Singapore",
                "from_cities": ["Mumbai", "Chennai", "Bangalore"],
                "trend_score": 82,
                "reasons": ["Tech conferences", "Business meetings", "Stopover destination"],
                "avg_price_usd": 22000,
                "seasonal_factor": "Conference season"
            },
            {
                "destination": "Bangkok",
                "from_cities": ["Delhi", "Mumbai", "Chennai"],
                "trend_score": 78,
                "reasons": ["Tourism surge", "Affordable destination", "Cultural attractions"],
                "avg_price_usd": 18000,
                "seasonal_factor": "Tourist season"
            },
            {
                "destination": "London",
                "from_cities": ["Mumbai", "Delhi", "Bangalore"],
                "trend_score": 75,
                "reasons": ["Business travel", "Education", "Cultural exchange"],
                "avg_price_usd": 45000,
                "seasonal_factor": "Business season"
            }
        ]
        
        # Convert prices to user's currency
        enhanced_destinations = []
        for dest in trending_destinations[:limit]:
            price_conversion = currency_service.get_regional_price(
                base_price_usd=dest['avg_price_usd'],
                region=region,
                target_currency=currency
            )
            
            enhanced_dest = {
                **dest,
                "price_info": {
                    "original_price_usd": dest['avg_price_usd'],
                    "converted_price": price_conversion['converted_amount'],
                    "currency": currency,
                    "formatted_price": price_conversion['formatted_amount']
                }
            }
            enhanced_destinations.append(enhanced_dest)
        
        return {
            "trending_destinations": enhanced_destinations,
            "currency": currency,
            "region": region,
            "analysis_period": "Last 30 days",
            "total_destinations": len(enhanced_destinations)
        }
    
    except Exception as e:
        logger.error(f"Trending destinations failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to get trending destinations")

def _parse_search_query(query: str) -> Dict[str, Any]:
    """Parse natural language search query"""
    query_lower = query.lower()
    parsed = {"type": "general"}
    
    # Detect search type
    if any(word in query_lower for word in ["flight", "fly", "travel", "trip", "book"]):
        parsed["type"] = "flight"
    elif any(word in query_lower for word in ["seat", "window", "aisle"]):
        parsed["type"] = "seat"
    
    # Extract cities (simple pattern matching)
    city_patterns = [
        "from", "to", "delhi", "mumbai", "bangalore", "chennai", "hyderabad",
        "pune", "kolkata", "ahmedabad", "jaipur", "lucknow", "kanpur", "nagpur",
        "indore", "thane", "bhopal", "visakhapatnam", "pimpri", "patna",
        "dubai", "singapore", "bangkok", "london", "new york", "tokyo"
    ]
    
    words = query_lower.split()
    for i, word in enumerate(words):
        if word in ["from", "leaving"] and i + 1 < len(words):
            parsed["from_city"] = words[i + 1].title()
        elif word in ["to", "going", "destination"] and i + 1 < len(words):
            parsed["to_city"] = words[i + 1].title()
    
    # Extract preferences
    if "cheap" in query_lower or "budget" in query_lower:
        parsed["price_preference"] = "low"
    elif "premium" in query_lower or "business" in query_lower:
        parsed["price_preference"] = "high"
    
    if "morning" in query_lower:
        parsed["time_preference"] = "morning"
    elif "evening" in query_lower:
        parsed["time_preference"] = "evening"
    
    return parsed
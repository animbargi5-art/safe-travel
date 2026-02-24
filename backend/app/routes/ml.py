"""
Machine Learning routes for intelligent recommendations and predictions
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from app.database_dep import get_db
from app.services.ml_service import MLService
from app.routes.auth import get_current_user
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ml", tags=["machine-learning"])

@router.get("/preferences/{user_id}")
def get_user_preferences(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's analyzed preferences from booking history"""
    
    # Users can only access their own preferences (or admin can access any)
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        ml_service = MLService(db)
        preferences = ml_service.get_user_preferences(user_id)
        
        return {
            "user_id": user_id,
            "preferences": preferences,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Error getting user preferences: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to analyze user preferences")

@router.get("/recommendations/flights")
def get_flight_recommendations(
    from_city: Optional[str] = None,
    to_city: Optional[str] = None,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get personalized flight recommendations for current user"""
    
    try:
        ml_service = MLService(db)
        recommendations = ml_service.get_personalized_flight_recommendations(
            user_id=current_user.id,
            from_city=from_city,
            to_city=to_city,
            limit=limit
        )
        
        return {
            "user_id": current_user.id,
            "recommendations": recommendations,
            "filters": {
                "from_city": from_city,
                "to_city": to_city,
                "limit": limit
            },
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Error getting flight recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get flight recommendations")

@router.get("/recommendations/seats/{flight_id}")
def get_seat_recommendations(
    flight_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get personalized seat recommendations for a specific flight"""
    
    try:
        ml_service = MLService(db)
        recommendations = ml_service.get_seat_recommendations(
            user_id=current_user.id,
            flight_id=flight_id
        )
        
        return {
            "user_id": current_user.id,
            "flight_id": flight_id,
            "recommendations": recommendations,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Error getting seat recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get seat recommendations")

@router.get("/demand/predict")
def predict_route_demand(
    route: str,
    date_range: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Predict demand for a specific route"""
    
    try:
        ml_service = MLService(db)
        prediction = ml_service.predict_demand(route, date_range)
        
        return {
            "prediction": prediction,
            "requested_by": current_user.id,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Error predicting demand: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to predict route demand")

@router.post("/anomaly/detect")
def detect_booking_anomaly(
    booking_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Detect anomalies in booking patterns"""
    
    try:
        ml_service = MLService(db)
        analysis = ml_service.detect_booking_anomalies(
            user_id=current_user.id,
            booking_data=booking_data
        )
        
        return {
            "user_id": current_user.id,
            "analysis": analysis,
            "booking_data": booking_data,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Error detecting anomalies: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to detect booking anomalies")

@router.get("/analytics/user-insights")
def get_user_insights(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive user insights and analytics"""
    
    try:
        ml_service = MLService(db)
        
        # Get user preferences
        preferences = ml_service.get_user_preferences(current_user.id)
        
        # Get flight recommendations
        flight_recommendations = ml_service.get_personalized_flight_recommendations(
            user_id=current_user.id,
            limit=5
        )
        
        return {
            "user_id": current_user.id,
            "insights": {
                "preferences": preferences,
                "recommended_flights": flight_recommendations,
                "analysis_date": "2024-02-23",
                "data_points": len(preferences.get('preferred_routes', [])) + len(preferences.get('preferred_times', []))
            },
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Error getting user insights: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get user insights")
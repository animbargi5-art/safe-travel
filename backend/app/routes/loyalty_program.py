"""
Loyalty Program API routes - Points, rewards, and tier benefits
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session
import logging

from app.database_dep import get_db
from app.routes.auth import get_current_user
from app.services.loyalty_program_service import get_loyalty_service
from app.services.live_monitoring import get_monitoring_service
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/loyalty", tags=["loyalty-program"])

# Request/Response models
class RedeemRewardRequest(BaseModel):
    reward_id: str

@router.get("/profile")
async def get_loyalty_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's complete loyalty profile
    """
    try:
        # Log activity
        monitoring = get_monitoring_service()
        monitoring.log_activity("LOYALTY_PROFILE_VIEW", current_user.id, {})
        
        # Get loyalty service
        loyalty_service = get_loyalty_service(db)
        
        # Get loyalty profile
        profile = loyalty_service.get_user_loyalty_profile(current_user.id)
        
        return profile
        
    except Exception as e:
        logger.error(f"Failed to get loyalty profile: {e}")
        raise HTTPException(status_code=500, detail="Failed to get loyalty profile")

@router.get("/tiers")
async def get_tier_information():
    """
    Get information about all loyalty tiers
    """
    return {
        "tiers": [
            {
                "name": "BRONZE",
                "threshold": 0,
                "benefits": {
                    "points_multiplier": 1.0,
                    "discount_percentage": 0.0,
                    "free_cancellation": False,
                    "priority_support": False,
                    "lounge_access": False,
                    "free_seat_selection": False,
                    "extra_baggage": 0,
                    "upgrade_probability": 0.0
                },
                "color": "#CD7F32",
                "description": "Start your journey with Safe Travel"
            },
            {
                "name": "SILVER",
                "threshold": 10000,
                "benefits": {
                    "points_multiplier": 1.25,
                    "discount_percentage": 5.0,
                    "free_cancellation": True,
                    "priority_support": False,
                    "lounge_access": False,
                    "free_seat_selection": True,
                    "extra_baggage": 1,
                    "upgrade_probability": 0.1
                },
                "color": "#C0C0C0",
                "description": "Enhanced benefits for regular travelers"
            },
            {
                "name": "GOLD",
                "threshold": 25000,
                "benefits": {
                    "points_multiplier": 1.5,
                    "discount_percentage": 10.0,
                    "free_cancellation": True,
                    "priority_support": True,
                    "lounge_access": False,
                    "free_seat_selection": True,
                    "extra_baggage": 2,
                    "upgrade_probability": 0.2
                },
                "color": "#FFD700",
                "description": "Premium benefits for frequent flyers"
            },
            {
                "name": "PLATINUM",
                "threshold": 50000,
                "benefits": {
                    "points_multiplier": 1.75,
                    "discount_percentage": 15.0,
                    "free_cancellation": True,
                    "priority_support": True,
                    "lounge_access": True,
                    "free_seat_selection": True,
                    "extra_baggage": 3,
                    "upgrade_probability": 0.35
                },
                "color": "#E5E4E2",
                "description": "Exclusive benefits for VIP travelers"
            },
            {
                "name": "DIAMOND",
                "threshold": 100000,
                "benefits": {
                    "points_multiplier": 2.0,
                    "discount_percentage": 20.0,
                    "free_cancellation": True,
                    "priority_support": True,
                    "lounge_access": True,
                    "free_seat_selection": True,
                    "extra_baggage": 5,
                    "upgrade_probability": 0.5
                },
                "color": "#B9F2FF",
                "description": "Ultimate luxury for elite travelers"
            }
        ]
    }

@router.get("/rewards")
async def get_reward_catalog(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get available rewards catalog
    """
    try:
        loyalty_service = get_loyalty_service(db)
        
        # Get user's points to show affordability
        profile = loyalty_service.get_user_loyalty_profile(current_user.id)
        user_points = profile["available_points"]
        
        # Get all rewards with affordability info
        rewards = []
        for reward_id, reward in loyalty_service.reward_catalog.items():
            can_afford = user_points >= reward['points_cost']
            
            rewards.append({
                "id": reward_id,
                "name": reward['name'],
                "description": reward['description'],
                "type": reward['type'].value,
                "points_cost": reward['points_cost'],
                "value": reward['value'],
                "validity_days": reward['validity_days'],
                "can_afford": can_afford,
                "points_needed": max(0, reward['points_cost'] - user_points)
            })
        
        # Sort by points cost
        rewards.sort(key=lambda x: x['points_cost'])
        
        return {
            "rewards": rewards,
            "user_points": user_points,
            "affordable_count": len([r for r in rewards if r['can_afford']])
        }
        
    except Exception as e:
        logger.error(f"Failed to get reward catalog: {e}")
        raise HTTPException(status_code=500, detail="Failed to get rewards")

@router.post("/redeem")
async def redeem_reward(
    request: RedeemRewardRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Redeem a loyalty reward
    """
    try:
        # Log activity
        monitoring = get_monitoring_service()
        monitoring.log_activity("LOYALTY_REWARD_REDEEM", current_user.id, {
            "reward_id": request.reward_id
        })
        
        # Get loyalty service
        loyalty_service = get_loyalty_service(db)
        
        # Redeem reward
        result = loyalty_service.redeem_reward(current_user.id, request.reward_id)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to redeem reward: {e}")
        raise HTTPException(status_code=500, detail="Failed to redeem reward")

@router.get("/upgrade-opportunities")
async def get_tier_upgrade_opportunities(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get tier upgrade opportunities and benefits
    """
    try:
        loyalty_service = get_loyalty_service(db)
        opportunities = loyalty_service.get_tier_upgrade_opportunities(current_user.id)
        
        return opportunities
        
    except Exception as e:
        logger.error(f"Failed to get upgrade opportunities: {e}")
        raise HTTPException(status_code=500, detail="Failed to get upgrade opportunities")

@router.get("/offers")
async def get_personalized_offers(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get personalized offers based on loyalty profile
    """
    try:
        loyalty_service = get_loyalty_service(db)
        offers = loyalty_service.get_personalized_offers(current_user.id)
        
        return {
            "offers": offers,
            "total_offers": len(offers)
        }
        
    except Exception as e:
        logger.error(f"Failed to get personalized offers: {e}")
        raise HTTPException(status_code=500, detail="Failed to get offers")

@router.post("/calculate-points")
async def calculate_booking_points(
    booking_amount: float,
    seat_class: str = "ECONOMY",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Calculate points that would be earned for a booking
    """
    try:
        if booking_amount <= 0:
            raise HTTPException(status_code=400, detail="Invalid booking amount")
        
        if seat_class not in ["ECONOMY", "BUSINESS", "FIRST"]:
            raise HTTPException(status_code=400, detail="Invalid seat class")
        
        loyalty_service = get_loyalty_service(db)
        points = loyalty_service.calculate_points_for_booking(booking_amount, seat_class, current_user.id)
        
        return {
            "booking_amount": booking_amount,
            "seat_class": seat_class,
            "base_points": points.base_points,
            "bonus_points": points.bonus_points,
            "tier_multiplier": points.tier_multiplier,
            "total_points": points.total_points,
            "reason": points.reason
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to calculate points: {e}")
        raise HTTPException(status_code=500, detail="Failed to calculate points")

@router.get("/leaderboard")
async def get_loyalty_leaderboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get loyalty program leaderboard (mock data for demo)
    """
    try:
        # Mock leaderboard data (in production, calculate from database)
        leaderboard = [
            {
                "rank": 1,
                "user_name": "Travel Enthusiast",
                "tier": "DIAMOND",
                "points": 156789,
                "destinations": 47,
                "is_current_user": False
            },
            {
                "rank": 2,
                "user_name": "Frequent Flyer",
                "tier": "PLATINUM",
                "points": 89234,
                "destinations": 32,
                "is_current_user": False
            },
            {
                "rank": 3,
                "user_name": "Globe Trotter",
                "tier": "PLATINUM",
                "points": 76543,
                "destinations": 28,
                "is_current_user": False
            },
            {
                "rank": 4,
                "user_name": "Adventure Seeker",
                "tier": "GOLD",
                "points": 45678,
                "destinations": 19,
                "is_current_user": False
            },
            {
                "rank": 5,
                "user_name": current_user.full_name,
                "tier": "SILVER",
                "points": 12345,
                "destinations": 8,
                "is_current_user": True
            }
        ]
        
        return {
            "leaderboard": leaderboard,
            "user_rank": 5,
            "total_members": 15847
        }
        
    except Exception as e:
        logger.error(f"Failed to get leaderboard: {e}")
        raise HTTPException(status_code=500, detail="Failed to get leaderboard")

@router.get("/analytics")
async def get_loyalty_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get loyalty program analytics (admin only)
    """
    try:
        # Check if user is admin
        if current_user.email != "test@safetravelapp.com":
            raise HTTPException(status_code=403, detail="Admin access required")
        
        # Mock analytics data
        return {
            "total_members": 15847,
            "active_members": 12456,
            "tier_distribution": {
                "BRONZE": {"count": 8934, "percentage": 56.4},
                "SILVER": {"count": 4523, "percentage": 28.5},
                "GOLD": {"count": 1789, "percentage": 11.3},
                "PLATINUM": {"count": 456, "percentage": 2.9},
                "DIAMOND": {"count": 145, "percentage": 0.9}
            },
            "points_statistics": {
                "total_points_issued": 45678912,
                "total_points_redeemed": 12345678,
                "average_points_per_user": 2879,
                "redemption_rate": 27.0
            },
            "popular_rewards": [
                {"reward": "5% Discount", "redemptions": 2345, "points_used": 5862500},
                {"reward": "Free Domestic Flight", "redemptions": 456, "points_used": 6840000},
                {"reward": "Business Class Upgrade", "redemptions": 234, "points_used": 1872000},
                {"reward": "Lounge Access", "redemptions": 789, "points_used": 2367000}
            ],
            "monthly_trends": [
                {"month": "Jan", "new_members": 234, "points_issued": 1234567, "redemptions": 456},
                {"month": "Feb", "new_members": 345, "points_issued": 1456789, "redemptions": 567},
                {"month": "Mar", "new_members": 456, "points_issued": 1678901, "redemptions": 678},
                {"month": "Apr", "new_members": 567, "points_issued": 1890123, "redemptions": 789},
                {"month": "May", "new_members": 678, "points_issued": 2012345, "redemptions": 890}
            ],
            "engagement_metrics": {
                "average_bookings_per_member": 3.2,
                "tier_upgrade_rate": 15.7,
                "member_retention_rate": 78.9,
                "points_earning_rate": 1247.5
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get loyalty analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get analytics")

@router.get("/earning-guide")
async def get_points_earning_guide():
    """
    Get guide on how to earn loyalty points
    """
    return {
        "earning_methods": [
            {
                "method": "Flight Bookings",
                "description": "Earn points for every flight you book",
                "rates": {
                    "ECONOMY": "1 point per $1 spent",
                    "BUSINESS": "1.5 points per $1 spent",
                    "FIRST": "2 points per $1 spent"
                },
                "example": "A $500 economy flight earns 500 base points"
            },
            {
                "method": "Tier Bonuses",
                "description": "Get bonus points based on your tier",
                "rates": {
                    "BRONZE": "No bonus (1x multiplier)",
                    "SILVER": "25% bonus (1.25x multiplier)",
                    "GOLD": "50% bonus (1.5x multiplier)",
                    "PLATINUM": "75% bonus (1.75x multiplier)",
                    "DIAMOND": "100% bonus (2x multiplier)"
                },
                "example": "Gold members earn 750 points for a $500 flight"
            },
            {
                "method": "Special Promotions",
                "description": "Earn extra points during promotional periods",
                "examples": [
                    "Double points weekends",
                    "Bonus points for new destinations",
                    "Seasonal promotions",
                    "Partner airline bonuses"
                ]
            },
            {
                "method": "Referrals",
                "description": "Earn points when friends book flights",
                "rate": "2,500 points per successful referral",
                "conditions": "Friend must complete their first booking"
            }
        ],
        "tips": [
            "Book higher class tickets for more points per dollar",
            "Take advantage of promotional periods",
            "Refer friends to earn bonus points",
            "Maintain tier status for ongoing bonuses",
            "Use loyalty credit cards for additional earning"
        ]
    }
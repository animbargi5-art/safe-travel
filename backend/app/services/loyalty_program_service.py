"""
Loyalty Program Service - Points, rewards, and tier benefits
Manages user loyalty points, tier progression, and reward redemption
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from enum import Enum
from dataclasses import dataclass

from app.models.user import User
from app.models.booking import Booking
from app.models.flight import Flight

logger = logging.getLogger(__name__)

class LoyaltyTier(Enum):
    BRONZE = "BRONZE"
    SILVER = "SILVER"
    GOLD = "GOLD"
    PLATINUM = "PLATINUM"
    DIAMOND = "DIAMOND"

class RewardType(Enum):
    DISCOUNT = "DISCOUNT"
    FREE_FLIGHT = "FREE_FLIGHT"
    UPGRADE = "UPGRADE"
    LOUNGE_ACCESS = "LOUNGE_ACCESS"
    EXTRA_BAGGAGE = "EXTRA_BAGGAGE"
    PRIORITY_BOARDING = "PRIORITY_BOARDING"

@dataclass
class LoyaltyPoints:
    """Loyalty points calculation result"""
    base_points: int
    bonus_points: int
    tier_multiplier: float
    total_points: int
    reason: str

@dataclass
class TierBenefits:
    """Tier-specific benefits"""
    tier: LoyaltyTier
    points_multiplier: float
    discount_percentage: float
    free_cancellation: bool
    priority_support: bool
    lounge_access: bool
    free_seat_selection: bool
    extra_baggage: int
    upgrade_probability: float

class LoyaltyProgramService:
    """
    Comprehensive loyalty program service
    """
    
    def __init__(self, db: Session):
        self.db = db
        
        # Tier thresholds (points required)
        self.tier_thresholds = {
            LoyaltyTier.BRONZE: 0,
            LoyaltyTier.SILVER: 10000,
            LoyaltyTier.GOLD: 25000,
            LoyaltyTier.PLATINUM: 50000,
            LoyaltyTier.DIAMOND: 100000
        }
        
        # Tier benefits configuration
        self.tier_benefits = {
            LoyaltyTier.BRONZE: TierBenefits(
                tier=LoyaltyTier.BRONZE,
                points_multiplier=1.0,
                discount_percentage=0.0,
                free_cancellation=False,
                priority_support=False,
                lounge_access=False,
                free_seat_selection=False,
                extra_baggage=0,
                upgrade_probability=0.0
            ),
            LoyaltyTier.SILVER: TierBenefits(
                tier=LoyaltyTier.SILVER,
                points_multiplier=1.25,
                discount_percentage=5.0,
                free_cancellation=True,
                priority_support=False,
                lounge_access=False,
                free_seat_selection=True,
                extra_baggage=1,
                upgrade_probability=0.1
            ),
            LoyaltyTier.GOLD: TierBenefits(
                tier=LoyaltyTier.GOLD,
                points_multiplier=1.5,
                discount_percentage=10.0,
                free_cancellation=True,
                priority_support=True,
                lounge_access=False,
                free_seat_selection=True,
                extra_baggage=2,
                upgrade_probability=0.2
            ),
            LoyaltyTier.PLATINUM: TierBenefits(
                tier=LoyaltyTier.PLATINUM,
                points_multiplier=1.75,
                discount_percentage=15.0,
                free_cancellation=True,
                priority_support=True,
                lounge_access=True,
                free_seat_selection=True,
                extra_baggage=3,
                upgrade_probability=0.35
            ),
            LoyaltyTier.DIAMOND: TierBenefits(
                tier=LoyaltyTier.DIAMOND,
                points_multiplier=2.0,
                discount_percentage=20.0,
                free_cancellation=True,
                priority_support=True,
                lounge_access=True,
                free_seat_selection=True,
                extra_baggage=5,
                upgrade_probability=0.5
            )
        }
        
        # Points earning rates
        self.points_rates = {
            'ECONOMY': 1.0,      # 1 point per dollar
            'BUSINESS': 1.5,     # 1.5 points per dollar
            'FIRST': 2.0         # 2 points per dollar
        }
        
        # Reward catalog
        self.reward_catalog = {
            'DISCOUNT_5': {
                'type': RewardType.DISCOUNT,
                'name': '5% Discount',
                'description': '5% off your next booking',
                'points_cost': 2500,
                'value': 5.0,
                'validity_days': 90
            },
            'DISCOUNT_10': {
                'type': RewardType.DISCOUNT,
                'name': '10% Discount',
                'description': '10% off your next booking',
                'points_cost': 5000,
                'value': 10.0,
                'validity_days': 90
            },
            'DISCOUNT_15': {
                'type': RewardType.DISCOUNT,
                'name': '15% Discount',
                'description': '15% off your next booking',
                'points_cost': 7500,
                'value': 15.0,
                'validity_days': 90
            },
            'FREE_DOMESTIC': {
                'type': RewardType.FREE_FLIGHT,
                'name': 'Free Domestic Flight',
                'description': 'Free economy flight within India',
                'points_cost': 15000,
                'value': 8000.0,
                'validity_days': 365
            },
            'FREE_INTERNATIONAL': {
                'type': RewardType.FREE_FLIGHT,
                'name': 'Free International Flight',
                'description': 'Free economy flight to select international destinations',
                'points_cost': 35000,
                'value': 25000.0,
                'validity_days': 365
            },
            'UPGRADE_BUSINESS': {
                'type': RewardType.UPGRADE,
                'name': 'Business Class Upgrade',
                'description': 'Upgrade to business class on your next flight',
                'points_cost': 8000,
                'value': 5000.0,
                'validity_days': 180
            },
            'UPGRADE_FIRST': {
                'type': RewardType.UPGRADE,
                'name': 'First Class Upgrade',
                'description': 'Upgrade to first class on your next flight',
                'points_cost': 15000,
                'value': 10000.0,
                'validity_days': 180
            },
            'LOUNGE_ACCESS': {
                'type': RewardType.LOUNGE_ACCESS,
                'name': 'Airport Lounge Access',
                'description': 'Access to premium airport lounges',
                'points_cost': 3000,
                'value': 1500.0,
                'validity_days': 30
            },
            'EXTRA_BAGGAGE': {
                'type': RewardType.EXTRA_BAGGAGE,
                'name': 'Extra Baggage Allowance',
                'description': 'Additional 20kg baggage allowance',
                'points_cost': 2000,
                'value': 1000.0,
                'validity_days': 60
            },
            'PRIORITY_BOARDING': {
                'type': RewardType.PRIORITY_BOARDING,
                'name': 'Priority Boarding',
                'description': 'Board the aircraft before general passengers',
                'points_cost': 1500,
                'value': 500.0,
                'validity_days': 60
            }
        }
        
        logger.info("🏆 Loyalty Program Service initialized")
    
    def get_user_loyalty_profile(self, user_id: int) -> Dict[str, Any]:
        """Get comprehensive loyalty profile for user"""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise ValueError("User not found")
            
            # Calculate total points earned
            total_points = self._calculate_total_points(user_id)
            
            # Determine current tier
            current_tier = self._determine_tier(total_points)
            
            # Get tier benefits
            benefits = self.tier_benefits[current_tier]
            
            # Calculate points to next tier
            next_tier, points_to_next = self._calculate_points_to_next_tier(total_points)
            
            # Get recent activity
            recent_activity = self._get_recent_activity(user_id)
            
            # Get available rewards
            available_rewards = self._get_available_rewards(total_points)
            
            # Calculate tier progress
            tier_progress = self._calculate_tier_progress(total_points, current_tier)
            
            return {
                "user_id": user_id,
                "total_points": total_points,
                "available_points": total_points,  # In production, subtract redeemed points
                "current_tier": current_tier.value,
                "tier_benefits": {
                    "points_multiplier": benefits.points_multiplier,
                    "discount_percentage": benefits.discount_percentage,
                    "free_cancellation": benefits.free_cancellation,
                    "priority_support": benefits.priority_support,
                    "lounge_access": benefits.lounge_access,
                    "free_seat_selection": benefits.free_seat_selection,
                    "extra_baggage": benefits.extra_baggage,
                    "upgrade_probability": benefits.upgrade_probability
                },
                "tier_progress": {
                    "current_tier": current_tier.value,
                    "next_tier": next_tier.value if next_tier else None,
                    "points_to_next": points_to_next,
                    "progress_percentage": tier_progress
                },
                "recent_activity": recent_activity,
                "available_rewards": available_rewards,
                "lifetime_stats": self._get_lifetime_stats(user_id)
            }
            
        except Exception as e:
            logger.error(f"Failed to get loyalty profile for user {user_id}: {e}")
            raise
    
    def calculate_points_for_booking(self, booking_amount: float, seat_class: str, user_id: int) -> LoyaltyPoints:
        """Calculate loyalty points for a booking"""
        try:
            # Get user's current tier
            total_points = self._calculate_total_points(user_id)
            current_tier = self._determine_tier(total_points)
            tier_benefits = self.tier_benefits[current_tier]
            
            # Base points calculation
            class_multiplier = self.points_rates.get(seat_class, 1.0)
            base_points = int(booking_amount * class_multiplier)
            
            # Tier bonus
            tier_multiplier = tier_benefits.points_multiplier
            bonus_points = int(base_points * (tier_multiplier - 1.0))
            
            # Total points
            total_earned = base_points + bonus_points
            
            return LoyaltyPoints(
                base_points=base_points,
                bonus_points=bonus_points,
                tier_multiplier=tier_multiplier,
                total_points=total_earned,
                reason=f"Booking in {seat_class} class with {current_tier.value} tier bonus"
            )
            
        except Exception as e:
            logger.error(f"Failed to calculate points for booking: {e}")
            raise
    
    def redeem_reward(self, user_id: int, reward_id: str) -> Dict[str, Any]:
        """Redeem a loyalty reward"""
        try:
            # Check if reward exists
            if reward_id not in self.reward_catalog:
                return {
                    "success": False,
                    "message": "Reward not found"
                }
            
            reward = self.reward_catalog[reward_id]
            
            # Check user's available points
            total_points = self._calculate_total_points(user_id)
            if total_points < reward['points_cost']:
                return {
                    "success": False,
                    "message": f"Insufficient points. Need {reward['points_cost']}, have {total_points}"
                }
            
            # Create redemption record (in production, store in database)
            redemption = {
                "id": f"RED_{user_id}_{int(datetime.utcnow().timestamp())}",
                "user_id": user_id,
                "reward_id": reward_id,
                "reward_name": reward['name'],
                "points_cost": reward['points_cost'],
                "redeemed_at": datetime.utcnow(),
                "expires_at": datetime.utcnow() + timedelta(days=reward['validity_days']),
                "status": "ACTIVE",
                "reward_details": reward
            }
            
            # Store redemption (mock storage)
            self._store_redemption(redemption)
            
            return {
                "success": True,
                "message": f"Successfully redeemed {reward['name']}",
                "redemption": {
                    "id": redemption["id"],
                    "reward_name": reward['name'],
                    "points_cost": reward['points_cost'],
                    "expires_at": redemption["expires_at"].isoformat(),
                    "reward_code": redemption["id"]  # Use as reward code
                },
                "remaining_points": total_points - reward['points_cost']
            }
            
        except Exception as e:
            logger.error(f"Failed to redeem reward: {e}")
            return {
                "success": False,
                "message": "Failed to redeem reward"
            }
    
    def get_tier_upgrade_opportunities(self, user_id: int) -> Dict[str, Any]:
        """Get opportunities for tier upgrades"""
        try:
            total_points = self._calculate_total_points(user_id)
            current_tier = self._determine_tier(total_points)
            
            # Get all higher tiers
            upgrade_opportunities = []
            
            for tier, threshold in self.tier_thresholds.items():
                if threshold > total_points:
                    points_needed = threshold - total_points
                    benefits = self.tier_benefits[tier]
                    
                    # Calculate potential savings/benefits
                    estimated_annual_bookings = self._estimate_annual_bookings(user_id)
                    annual_savings = estimated_annual_bookings * benefits.discount_percentage / 100 * 10000  # Assume avg booking $100
                    
                    upgrade_opportunities.append({
                        "tier": tier.value,
                        "points_needed": points_needed,
                        "benefits": {
                            "discount_percentage": benefits.discount_percentage,
                            "points_multiplier": benefits.points_multiplier,
                            "free_cancellation": benefits.free_cancellation,
                            "priority_support": benefits.priority_support,
                            "lounge_access": benefits.lounge_access,
                            "extra_baggage": benefits.extra_baggage
                        },
                        "estimated_annual_savings": annual_savings,
                        "bookings_needed": int(points_needed / 10000) + 1  # Rough estimate
                    })
            
            return {
                "current_tier": current_tier.value,
                "current_points": total_points,
                "upgrade_opportunities": upgrade_opportunities[:2]  # Show next 2 tiers
            }
            
        except Exception as e:
            logger.error(f"Failed to get tier upgrade opportunities: {e}")
            raise
    
    def get_personalized_offers(self, user_id: int) -> List[Dict[str, Any]]:
        """Get personalized offers based on user's loyalty profile"""
        try:
            total_points = self._calculate_total_points(user_id)
            current_tier = self._determine_tier(total_points)
            benefits = self.tier_benefits[current_tier]
            
            offers = []
            
            # Tier-specific offers
            if current_tier == LoyaltyTier.BRONZE:
                offers.append({
                    "id": "SILVER_BOOST",
                    "title": "🥈 Silver Tier Boost",
                    "description": "Earn 2x points on your next 3 bookings to reach Silver faster!",
                    "type": "POINTS_MULTIPLIER",
                    "value": 2.0,
                    "conditions": "Valid for next 3 bookings within 30 days",
                    "expires_at": (datetime.utcnow() + timedelta(days=30)).isoformat()
                })
            
            elif current_tier == LoyaltyTier.SILVER:
                offers.append({
                    "id": "GOLD_FAST_TRACK",
                    "title": "🥇 Gold Fast Track",
                    "description": "Book 2 international flights and get instant Gold status!",
                    "type": "TIER_UPGRADE",
                    "value": "GOLD",
                    "conditions": "Book 2 international flights within 60 days",
                    "expires_at": (datetime.utcnow() + timedelta(days=60)).isoformat()
                })
            
            # Points-based offers
            if total_points >= 5000:
                offers.append({
                    "id": "WEEKEND_BONUS",
                    "title": "🎉 Weekend Bonus Points",
                    "description": "Earn 50% bonus points on weekend bookings!",
                    "type": "WEEKEND_BONUS",
                    "value": 1.5,
                    "conditions": "Valid for bookings made on Saturday or Sunday",
                    "expires_at": (datetime.utcnow() + timedelta(days=7)).isoformat()
                })
            
            # Seasonal offers
            current_month = datetime.utcnow().month
            if current_month in [12, 1, 2]:  # Winter
                offers.append({
                    "id": "WINTER_ESCAPE",
                    "title": "❄️ Winter Escape Special",
                    "description": f"Extra {benefits.discount_percentage + 5}% off warm destination flights!",
                    "type": "SEASONAL_DISCOUNT",
                    "value": benefits.discount_percentage + 5,
                    "conditions": "Valid for flights to tropical destinations",
                    "expires_at": (datetime.utcnow() + timedelta(days=30)).isoformat()
                })
            
            # Referral offers
            offers.append({
                "id": "REFER_FRIEND",
                "title": "👥 Refer & Earn",
                "description": "Refer friends and earn 2,500 points for each successful booking!",
                "type": "REFERRAL",
                "value": 2500,
                "conditions": "Friend must complete their first booking",
                "expires_at": (datetime.utcnow() + timedelta(days=365)).isoformat()
            })
            
            return offers
            
        except Exception as e:
            logger.error(f"Failed to get personalized offers: {e}")
            return []
    
    def _calculate_total_points(self, user_id: int) -> int:
        """Calculate total loyalty points for user"""
        try:
            # Get all confirmed bookings
            bookings = self.db.query(Booking).filter(
                and_(
                    Booking.user_id == user_id,
                    Booking.status == "CONFIRMED"
                )
            ).all()
            
            total_points = 0
            for booking in bookings:
                # Get flight details
                flight = self.db.query(Flight).filter(Flight.id == booking.flight_id).first()
                if flight:
                    # Calculate points for this booking
                    seat_class = getattr(booking, 'seat_class', 'ECONOMY')
                    points = self.calculate_points_for_booking(booking.price, seat_class, user_id)
                    total_points += points.total_points
            
            return total_points
            
        except Exception as e:
            logger.error(f"Failed to calculate total points: {e}")
            return 0
    
    def _determine_tier(self, total_points: int) -> LoyaltyTier:
        """Determine loyalty tier based on points"""
        for tier in reversed(list(LoyaltyTier)):
            if total_points >= self.tier_thresholds[tier]:
                return tier
        return LoyaltyTier.BRONZE
    
    def _calculate_points_to_next_tier(self, total_points: int) -> Tuple[Optional[LoyaltyTier], int]:
        """Calculate points needed for next tier"""
        current_tier = self._determine_tier(total_points)
        
        # Find next tier
        tier_list = list(LoyaltyTier)
        current_index = tier_list.index(current_tier)
        
        if current_index < len(tier_list) - 1:
            next_tier = tier_list[current_index + 1]
            points_needed = self.tier_thresholds[next_tier] - total_points
            return next_tier, points_needed
        
        return None, 0  # Already at highest tier
    
    def _calculate_tier_progress(self, total_points: int, current_tier: LoyaltyTier) -> float:
        """Calculate progress percentage within current tier"""
        tier_list = list(LoyaltyTier)
        current_index = tier_list.index(current_tier)
        
        if current_index == len(tier_list) - 1:
            return 100.0  # Highest tier
        
        current_threshold = self.tier_thresholds[current_tier]
        next_threshold = self.tier_thresholds[tier_list[current_index + 1]]
        
        progress = (total_points - current_threshold) / (next_threshold - current_threshold)
        return min(progress * 100, 100.0)
    
    def _get_recent_activity(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent loyalty activity"""
        try:
            # Get recent bookings
            recent_bookings = self.db.query(Booking).filter(
                Booking.user_id == user_id
            ).order_by(Booking.created_at.desc()).limit(limit).all()
            
            activity = []
            for booking in recent_bookings:
                flight = self.db.query(Flight).filter(Flight.id == booking.flight_id).first()
                if flight:
                    points = self.calculate_points_for_booking(booking.price, 'ECONOMY', user_id)
                    activity.append({
                        "date": booking.created_at.isoformat(),
                        "type": "BOOKING",
                        "description": f"Flight to {flight.to_city}",
                        "points_earned": points.total_points,
                        "booking_amount": booking.price
                    })
            
            return activity
            
        except Exception as e:
            logger.error(f"Failed to get recent activity: {e}")
            return []
    
    def _get_available_rewards(self, total_points: int) -> List[Dict[str, Any]]:
        """Get rewards user can afford"""
        available = []
        
        for reward_id, reward in self.reward_catalog.items():
            if total_points >= reward['points_cost']:
                available.append({
                    "id": reward_id,
                    "name": reward['name'],
                    "description": reward['description'],
                    "points_cost": reward['points_cost'],
                    "type": reward['type'].value,
                    "value": reward['value'],
                    "validity_days": reward['validity_days']
                })
        
        # Sort by points cost
        return sorted(available, key=lambda x: x['points_cost'])
    
    def _get_lifetime_stats(self, user_id: int) -> Dict[str, Any]:
        """Get lifetime statistics"""
        try:
            # Get booking statistics
            total_bookings = self.db.query(Booking).filter(Booking.user_id == user_id).count()
            total_spent = self.db.query(func.sum(Booking.price)).filter(Booking.user_id == user_id).scalar() or 0
            
            # Get unique destinations
            destinations = self.db.query(Flight.to_city).join(Booking).filter(
                Booking.user_id == user_id
            ).distinct().all()
            
            return {
                "total_bookings": total_bookings,
                "total_spent": float(total_spent),
                "destinations_visited": len(destinations),
                "member_since": "2024-01-01",  # Mock data
                "favorite_destination": destinations[0][0] if destinations else None
            }
            
        except Exception as e:
            logger.error(f"Failed to get lifetime stats: {e}")
            return {}
    
    def _estimate_annual_bookings(self, user_id: int) -> int:
        """Estimate annual bookings based on history"""
        try:
            # Get bookings from last 12 months
            one_year_ago = datetime.utcnow() - timedelta(days=365)
            annual_bookings = self.db.query(Booking).filter(
                and_(
                    Booking.user_id == user_id,
                    Booking.created_at >= one_year_ago
                )
            ).count()
            
            return max(annual_bookings, 2)  # Minimum 2 bookings estimate
            
        except Exception as e:
            logger.error(f"Failed to estimate annual bookings: {e}")
            return 2
    
    def _store_redemption(self, redemption: Dict[str, Any]):
        """Store redemption record (mock implementation)"""
        # In production, store in database
        if not hasattr(self, '_redemptions'):
            self._redemptions = {}
        
        self._redemptions[redemption["id"]] = redemption

# Helper function to get service instance
def get_loyalty_service(db: Session) -> LoyaltyProgramService:
    """Get loyalty program service instance"""
    return LoyaltyProgramService(db)
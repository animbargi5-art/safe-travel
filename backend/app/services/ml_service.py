"""
Machine Learning service for intelligent recommendations and predictions
"""

import json
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
import numpy as np
from collections import defaultdict, Counter

from app.models.user import User
from app.models.flight import Flight
from app.models.booking import Booking
from app.models.seat import Seat
from app.constants.booking_status import BookingStatus

logger = logging.getLogger(__name__)

class MLService:
    """
    Machine Learning service for personalized recommendations and predictions
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_preferences(self, user_id: int) -> Dict:
        """
        Analyze user's booking history to extract preferences
        """
        
        # Get user's confirmed bookings
        bookings = self.db.query(Booking).filter(
            and_(
                Booking.user_id == user_id,
                Booking.status == BookingStatus.CONFIRMED
            )
        ).all()
        
        if not bookings:
            return self._get_default_preferences()
        
        # Load related data
        for booking in bookings:
            booking.flight = self.db.query(Flight).filter(Flight.id == booking.flight_id).first()
            booking.seat = self.db.query(Seat).filter(Seat.id == booking.seat_id).first()
        
        preferences = {
            'preferred_routes': self._analyze_route_preferences(bookings),
            'preferred_times': self._analyze_time_preferences(bookings),
            'preferred_seat_class': self._analyze_seat_class_preferences(bookings),
            'preferred_seat_position': self._analyze_seat_position_preferences(bookings),
            'price_sensitivity': self._analyze_price_sensitivity(bookings),
            'booking_patterns': self._analyze_booking_patterns(bookings),
            'seasonal_preferences': self._analyze_seasonal_preferences(bookings)
        }
        
        logger.info(f"Analyzed preferences for user {user_id}: {len(bookings)} bookings")
        return preferences
    
    def _get_default_preferences(self) -> Dict:
        """Default preferences for new users"""
        return {
            'preferred_routes': [],
            'preferred_times': ['morning', 'evening'],
            'preferred_seat_class': 'ECONOMY',
            'preferred_seat_position': 'WINDOW',
            'price_sensitivity': 'medium',
            'booking_patterns': {'advance_days': 14},
            'seasonal_preferences': {}
        }
    
    def _analyze_route_preferences(self, bookings: List[Booking]) -> List[Dict]:
        """Analyze preferred routes from booking history"""
        
        routes = []
        for booking in bookings:
            if booking.flight:
                routes.append({
                    'from_city': booking.flight.from_city,
                    'to_city': booking.flight.to_city
                })
        
        # Count route frequency
        route_counts = Counter(
            f"{route['from_city']} → {route['to_city']}" 
            for route in routes
        )
        
        return [
            {
                'route': route,
                'frequency': count,
                'preference_score': count / len(bookings)
            }
            for route, count in route_counts.most_common(5)
        ]
    
    def _analyze_time_preferences(self, bookings: List[Booking]) -> List[str]:
        """Analyze preferred departure times"""
        
        time_preferences = []
        for booking in bookings:
            if booking.flight and booking.flight.departure_time:
                hour = booking.flight.departure_time.hour
                
                if 6 <= hour < 12:
                    time_preferences.append('morning')
                elif 12 <= hour < 17:
                    time_preferences.append('afternoon')
                elif 17 <= hour < 21:
                    time_preferences.append('evening')
                else:
                    time_preferences.append('night')
        
        # Return most common time preferences
        time_counts = Counter(time_preferences)
        return [time for time, _ in time_counts.most_common(2)]
    
    def _analyze_seat_class_preferences(self, bookings: List[Booking]) -> str:
        """Analyze preferred seat class"""
        
        seat_classes = []
        for booking in bookings:
            if booking.seat:
                seat_classes.append(booking.seat.seat_class)
        
        if not seat_classes:
            return 'ECONOMY'
        
        # Return most common seat class
        class_counts = Counter(seat_classes)
        return class_counts.most_common(1)[0][0]
    
    def _analyze_seat_position_preferences(self, bookings: List[Booking]) -> str:
        """Analyze preferred seat position (window/aisle/middle)"""
        
        positions = []
        for booking in bookings:
            if booking.seat:
                position = self._get_seat_position(booking.seat.col)
                positions.append(position)
        
        if not positions:
            return 'WINDOW'
        
        # Return most common position
        position_counts = Counter(positions)
        return position_counts.most_common(1)[0][0]
    
    def _get_seat_position(self, col: str) -> str:
        """Determine seat position from column"""
        col = col.upper()
        if col in ['A', 'F']:
            return 'WINDOW'
        elif col in ['C', 'D']:
            return 'AISLE'
        else:
            return 'MIDDLE'
    
    def _analyze_price_sensitivity(self, bookings: List[Booking]) -> str:
        """Analyze user's price sensitivity"""
        
        if not bookings:
            return 'medium'
        
        prices = [booking.price for booking in bookings if booking.price]
        if not prices:
            return 'medium'
        
        avg_price = np.mean(prices)
        
        # Simple categorization based on average price
        if avg_price < 5000:
            return 'high'  # Price sensitive
        elif avg_price > 15000:
            return 'low'   # Price insensitive
        else:
            return 'medium'
    
    def _analyze_booking_patterns(self, bookings: List[Booking]) -> Dict:
        """Analyze booking timing patterns"""
        
        advance_days = []
        for booking in bookings:
            if booking.flight and booking.created_at:
                days_advance = (booking.flight.departure_time.date() - booking.created_at.date()).days
                if days_advance > 0:
                    advance_days.append(days_advance)
        
        if not advance_days:
            return {'advance_days': 14}
        
        return {
            'advance_days': int(np.mean(advance_days)),
            'min_advance': min(advance_days),
            'max_advance': max(advance_days)
        }
    
    def _analyze_seasonal_preferences(self, bookings: List[Booking]) -> Dict:
        """Analyze seasonal booking preferences"""
        
        seasonal_bookings = defaultdict(int)
        for booking in bookings:
            if booking.flight:
                month = booking.flight.departure_time.month
                if month in [12, 1, 2]:
                    seasonal_bookings['winter'] += 1
                elif month in [3, 4, 5]:
                    seasonal_bookings['spring'] += 1
                elif month in [6, 7, 8]:
                    seasonal_bookings['summer'] += 1
                else:
                    seasonal_bookings['autumn'] += 1
        
        return dict(seasonal_bookings)
    
    def get_personalized_flight_recommendations(
        self, 
        user_id: int, 
        from_city: Optional[str] = None,
        to_city: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict]:
        """
        Get personalized flight recommendations based on user preferences
        """
        
        preferences = self.get_user_preferences(user_id)
        
        # Build query based on preferences
        query = self.db.query(Flight)
        
        # Filter by cities if provided
        if from_city:
            query = query.filter(Flight.from_city.ilike(f"%{from_city}%"))
        if to_city:
            query = query.filter(Flight.to_city.ilike(f"%{to_city}%"))
        
        # Get flights in the next 30 days
        start_date = datetime.now()
        end_date = start_date + timedelta(days=30)
        query = query.filter(
            and_(
                Flight.departure_time >= start_date,
                Flight.departure_time <= end_date
            )
        )
        
        flights = query.all()
        
        # Score flights based on preferences
        scored_flights = []
        for flight in flights:
            score = self._calculate_flight_score(flight, preferences)
            scored_flights.append({
                'flight': flight,
                'score': score,
                'recommendation_reasons': self._get_recommendation_reasons(flight, preferences)
            })
        
        # Sort by score and return top recommendations
        scored_flights.sort(key=lambda x: x['score'], reverse=True)
        
        recommendations = []
        for item in scored_flights[:limit]:
            flight = item['flight']
            recommendations.append({
                'id': flight.id,
                'from_city': flight.from_city,
                'to_city': flight.to_city,
                'departure_time': flight.departure_time,
                'price': flight.price,
                'airline': flight.airline,
                'score': item['score'],
                'reasons': item['recommendation_reasons']
            })
        
        return recommendations
    
    def _calculate_flight_score(self, flight: Flight, preferences: Dict) -> float:
        """Calculate recommendation score for a flight"""
        
        score = 0.0
        
        # Route preference score
        route = f"{flight.from_city} → {flight.to_city}"
        for pref_route in preferences['preferred_routes']:
            if pref_route['route'] == route:
                score += pref_route['preference_score'] * 30
                break
        
        # Time preference score
        if flight.departure_time:
            hour = flight.departure_time.hour
            flight_time = 'morning' if 6 <= hour < 12 else 'afternoon' if 12 <= hour < 17 else 'evening' if 17 <= hour < 21 else 'night'
            
            if flight_time in preferences['preferred_times']:
                score += 20
        
        # Price sensitivity score
        price_sensitivity = preferences['price_sensitivity']
        if price_sensitivity == 'high' and flight.price < 8000:
            score += 15
        elif price_sensitivity == 'low' and flight.price > 15000:
            score += 10
        elif price_sensitivity == 'medium' and 5000 <= flight.price <= 15000:
            score += 15
        
        # Airline preference (if we had historical data)
        if flight.airline:
            score += 5  # Base airline bonus
        
        # Recency bonus (prefer flights not too far in future)
        days_until_flight = (flight.departure_time.date() - datetime.now().date()).days
        advance_preference = preferences['booking_patterns']['advance_days']
        
        if abs(days_until_flight - advance_preference) <= 7:
            score += 10
        
        return score
    
    def _get_recommendation_reasons(self, flight: Flight, preferences: Dict) -> List[str]:
        """Get reasons why this flight is recommended"""
        
        reasons = []
        
        # Check route preference
        route = f"{flight.from_city} → {flight.to_city}"
        for pref_route in preferences['preferred_routes']:
            if pref_route['route'] == route:
                reasons.append(f"You frequently travel this route")
                break
        
        # Check time preference
        if flight.departure_time:
            hour = flight.departure_time.hour
            flight_time = 'morning' if 6 <= hour < 12 else 'afternoon' if 12 <= hour < 17 else 'evening' if 17 <= hour < 21 else 'night'
            
            if flight_time in preferences['preferred_times']:
                reasons.append(f"Matches your preferred {flight_time} departure time")
        
        # Check price preference
        price_sensitivity = preferences['price_sensitivity']
        if price_sensitivity == 'high' and flight.price < 8000:
            reasons.append("Great value for budget-conscious travel")
        elif price_sensitivity == 'low' and flight.price > 15000:
            reasons.append("Premium option matching your preferences")
        
        # Check airline
        if flight.airline:
            reasons.append(f"Flying with {flight.airline}")
        
        if not reasons:
            reasons.append("Popular choice among travelers")
        
        return reasons
    
    def get_seat_recommendations(self, user_id: int, flight_id: int) -> List[Dict]:
        """
        Get personalized seat recommendations for a flight
        """
        
        preferences = self.get_user_preferences(user_id)
        
        # Get available seats for the flight
        flight = self.db.query(Flight).filter(Flight.id == flight_id).first()
        if not flight:
            return []
        
        # Get all seats for the aircraft
        all_seats = self.db.query(Seat).filter(Seat.aircraft_id == flight.aircraft_id).all()
        
        # Get booked seats
        booked_seat_ids = self.db.query(Booking.seat_id).filter(
            and_(
                Booking.flight_id == flight_id,
                Booking.status.in_([BookingStatus.HOLD, BookingStatus.CONFIRMED])
            )
        ).all()
        booked_seat_ids = [seat_id[0] for seat_id in booked_seat_ids]
        
        # Filter available seats
        available_seats = [seat for seat in all_seats if seat.id not in booked_seat_ids]
        
        # Score seats based on preferences
        scored_seats = []
        for seat in available_seats:
            score = self._calculate_seat_score(seat, preferences)
            scored_seats.append({
                'seat': seat,
                'score': score,
                'reasons': self._get_seat_recommendation_reasons(seat, preferences)
            })
        
        # Sort by score
        scored_seats.sort(key=lambda x: x['score'], reverse=True)
        
        # Return top 5 recommendations
        recommendations = []
        for item in scored_seats[:5]:
            seat = item['seat']
            recommendations.append({
                'seat_id': seat.id,
                'seat_number': seat.seat_number,
                'seat_class': seat.seat_class,
                'row': seat.row,
                'col': seat.col,
                'score': item['score'],
                'reasons': item['reasons']
            })
        
        return recommendations
    
    def _calculate_seat_score(self, seat: Seat, preferences: Dict) -> float:
        """Calculate recommendation score for a seat"""
        
        score = 0.0
        
        # Seat class preference
        if seat.seat_class == preferences['preferred_seat_class']:
            score += 30
        
        # Seat position preference
        position = self._get_seat_position(seat.col)
        if position == preferences['preferred_seat_position']:
            score += 25
        
        # Row preference (front rows generally preferred)
        if seat.seat_class == 'FIRST' and seat.row <= 3:
            score += 20
        elif seat.seat_class == 'BUSINESS' and seat.row <= 10:
            score += 15
        elif seat.seat_class == 'ECONOMY' and seat.row <= 15:
            score += 10
        
        # Aisle access bonus
        if position == 'AISLE':
            score += 5
        
        return score
    
    def _get_seat_recommendation_reasons(self, seat: Seat, preferences: Dict) -> List[str]:
        """Get reasons why this seat is recommended"""
        
        reasons = []
        
        if seat.seat_class == preferences['preferred_seat_class']:
            reasons.append(f"Your preferred {seat.seat_class.lower()} class")
        
        position = self._get_seat_position(seat.col)
        if position == preferences['preferred_seat_position']:
            reasons.append(f"Your preferred {position.lower()} seat")
        
        if seat.row <= 10:
            reasons.append("Front section for quicker boarding/deplaning")
        
        if position == 'AISLE':
            reasons.append("Easy aisle access")
        elif position == 'WINDOW':
            reasons.append("Great window views")
        
        if not reasons:
            reasons.append("Good available option")
        
        return reasons
    
    def predict_demand(self, route: str, date_range: int = 30) -> Dict:
        """
        Predict demand for a route over the next period
        """
        
        # Parse route
        try:
            from_city, to_city = route.split(' → ')
        except ValueError:
            return {'error': 'Invalid route format. Use "City1 → City2"'}
        
        # Get historical bookings for this route
        start_date = datetime.now() - timedelta(days=90)  # Look at last 90 days
        end_date = datetime.now()
        
        historical_bookings = self.db.query(Booking).join(Flight).filter(
            and_(
                Flight.from_city == from_city,
                Flight.to_city == to_city,
                Booking.created_at >= start_date,
                Booking.created_at <= end_date,
                Booking.status == BookingStatus.CONFIRMED
            )
        ).all()
        
        if not historical_bookings:
            return {
                'route': route,
                'predicted_demand': 'low',
                'confidence': 0.0,
                'historical_bookings': 0
            }
        
        # Simple demand prediction based on historical data
        bookings_per_day = len(historical_bookings) / 90
        
        # Predict demand level
        if bookings_per_day >= 5:
            demand_level = 'high'
            confidence = 0.8
        elif bookings_per_day >= 2:
            demand_level = 'medium'
            confidence = 0.7
        else:
            demand_level = 'low'
            confidence = 0.6
        
        return {
            'route': route,
            'predicted_demand': demand_level,
            'confidence': confidence,
            'historical_bookings': len(historical_bookings),
            'avg_bookings_per_day': round(bookings_per_day, 2),
            'prediction_period': f"Next {date_range} days"
        }
    
    def detect_booking_anomalies(self, user_id: int, booking_data: Dict) -> Dict:
        """
        Detect unusual booking patterns that might indicate fraud
        """
        
        anomalies = []
        risk_score = 0.0
        
        # Get user's booking history
        user_bookings = self.db.query(Booking).filter(Booking.user_id == user_id).all()
        
        # Check for unusual booking frequency
        recent_bookings = [
            b for b in user_bookings 
            if b.created_at >= datetime.now() - timedelta(days=1)
        ]
        
        if len(recent_bookings) > 5:
            anomalies.append("Unusually high booking frequency")
            risk_score += 0.3
        
        # Check for unusual price patterns
        if user_bookings:
            avg_price = np.mean([b.price for b in user_bookings if b.price])
            current_price = booking_data.get('price', 0)
            
            if current_price > avg_price * 3:
                anomalies.append("Booking price significantly higher than user's average")
                risk_score += 0.2
        
        # Check for unusual timing
        departure_time = booking_data.get('departure_time')
        if departure_time:
            if isinstance(departure_time, str):
                departure_time = datetime.fromisoformat(departure_time.replace('Z', '+00:00'))
            
            days_until_departure = (departure_time.date() - datetime.now().date()).days
            
            if days_until_departure < 1:
                anomalies.append("Very short booking lead time")
                risk_score += 0.2
            elif days_until_departure > 365:
                anomalies.append("Unusually long booking lead time")
                risk_score += 0.1
        
        # Determine risk level
        if risk_score >= 0.5:
            risk_level = 'high'
        elif risk_score >= 0.3:
            risk_level = 'medium'
        else:
            risk_level = 'low'
        
        return {
            'risk_level': risk_level,
            'risk_score': round(risk_score, 2),
            'anomalies': anomalies,
            'recommendation': 'manual_review' if risk_level == 'high' else 'auto_approve'
        }
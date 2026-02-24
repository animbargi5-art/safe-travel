"""
Voice Booking Service - AI-powered voice commands for flight booking
Processes natural language voice commands and converts them to booking actions
"""

import re
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
import speech_recognition as sr
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

@dataclass
class VoiceCommand:
    """Structured voice command data"""
    intent: str
    entities: Dict[str, Any]
    confidence: float
    raw_text: str
    processed_text: str

@dataclass
class BookingIntent:
    """Parsed booking intent from voice"""
    action: str  # search, book, cancel, modify
    from_city: Optional[str] = None
    to_city: Optional[str] = None
    departure_date: Optional[str] = None
    return_date: Optional[str] = None
    passengers: int = 1
    class_preference: str = "ECONOMY"
    time_preference: Optional[str] = None
    price_preference: Optional[str] = None

class VoiceBookingService:
    """
    Advanced voice booking service with natural language processing
    """
    
    def __init__(self):
        # City mappings for voice recognition
        self.city_mappings = {
            # Indian cities
            'mumbai': 'Mumbai', 'bombay': 'Mumbai',
            'delhi': 'Delhi', 'new delhi': 'Delhi',
            'bangalore': 'Bangalore', 'bengaluru': 'Bangalore',
            'chennai': 'Chennai', 'madras': 'Chennai',
            'hyderabad': 'Hyderabad',
            'pune': 'Pune', 'poona': 'Pune',
            'kolkata': 'Kolkata', 'calcutta': 'Kolkata',
            'ahmedabad': 'Ahmedabad',
            'jaipur': 'Jaipur',
            'lucknow': 'Lucknow',
            'kanpur': 'Kanpur',
            'nagpur': 'Nagpur',
            'indore': 'Indore',
            'thane': 'Thane',
            'bhopal': 'Bhopal',
            'visakhapatnam': 'Visakhapatnam', 'vizag': 'Visakhapatnam',
            'pimpri': 'Pimpri-Chinchwad',
            'patna': 'Patna',
            'vadodara': 'Vadodara', 'baroda': 'Vadodara',
            'ghaziabad': 'Ghaziabad',
            'ludhiana': 'Ludhiana',
            'agra': 'Agra',
            'nashik': 'Nashik',
            'faridabad': 'Faridabad',
            'meerut': 'Meerut',
            'rajkot': 'Rajkot',
            'kalyan': 'Kalyan-Dombivali',
            'vasai': 'Vasai-Virar',
            'varanasi': 'Varanasi', 'benares': 'Varanasi',
            'srinagar': 'Srinagar',
            'aurangabad': 'Aurangabad',
            'dhanbad': 'Dhanbad',
            'amritsar': 'Amritsar',
            'navi mumbai': 'Navi Mumbai',
            'allahabad': 'Allahabad', 'prayagraj': 'Allahabad',
            'ranchi': 'Ranchi',
            'howrah': 'Howrah',
            'coimbatore': 'Coimbatore',
            'jabalpur': 'Jabalpur',
            'gwalior': 'Gwalior',
            'vijayawada': 'Vijayawada',
            'jodhpur': 'Jodhpur',
            'madurai': 'Madurai',
            'raipur': 'Raipur',
            'kota': 'Kota',
            'chandigarh': 'Chandigarh',
            'guwahati': 'Guwahati',
            'solapur': 'Solapur',
            'hubli': 'Hubli-Dharwad', 'dharwad': 'Hubli-Dharwad',
            'tiruchirappalli': 'Tiruchirappalli', 'trichy': 'Tiruchirappalli',
            'bareilly': 'Bareilly',
            'mysore': 'Mysore', 'mysuru': 'Mysore',
            'tiruppur': 'Tiruppur',
            'gurgaon': 'Gurgaon', 'gurugram': 'Gurgaon',
            'aligarh': 'Aligarh',
            'jalandhar': 'Jalandhar',
            'bhubaneswar': 'Bhubaneswar',
            'salem': 'Salem',
            'warangal': 'Warangal',
            'mira': 'Mira-Bhayandar',
            'thiruvananthapuram': 'Thiruvananthapuram', 'trivandrum': 'Thiruvananthapuram',
            'bhiwandi': 'Bhiwandi',
            'saharanpur': 'Saharanpur',
            'guntur': 'Guntur',
            'amravati': 'Amravati',
            'bikaner': 'Bikaner',
            'noida': 'Noida',
            'jamshedpur': 'Jamshedpur',
            'bhilai': 'Bhilai Nagar',
            'cuttack': 'Cuttack',
            'firozabad': 'Firozabad',
            'kochi': 'Kochi', 'cochin': 'Kochi',
            'bhavnagar': 'Bhavnagar',
            'dehradun': 'Dehradun',
            'durgapur': 'Durgapur',
            'asansol': 'Asansol',
            'nanded': 'Nanded-Waghala',
            'kolhapur': 'Kolhapur',
            'ajmer': 'Ajmer',
            'gulbarga': 'Gulbarga',
            'jamnagar': 'Jamnagar',
            'ujjain': 'Ujjain',
            'loni': 'Loni',
            'siliguri': 'Siliguri',
            'jhansi': 'Jhansi',
            'ulhasnagar': 'Ulhasnagar',
            'nellore': 'Nellore',
            'jammu': 'Jammu',
            'sangli': 'Sangli-Miraj & Kupwad',
            'belgaum': 'Belgaum', 'belagavi': 'Belgaum',
            'mangalore': 'Mangalore', 'mangaluru': 'Mangalore',
            'ambattur': 'Ambattur',
            'tirunelveli': 'Tirunelveli',
            'malegaon': 'Malegaon',
            'gaya': 'Gaya',
            'jalgaon': 'Jalgaon',
            'udaipur': 'Udaipur',
            'maheshtala': 'Maheshtala',
            
            # International cities
            'dubai': 'Dubai',
            'singapore': 'Singapore',
            'bangkok': 'Bangkok',
            'london': 'London',
            'new york': 'New York', 'nyc': 'New York',
            'tokyo': 'Tokyo',
            'paris': 'Paris',
            'sydney': 'Sydney',
            'melbourne': 'Melbourne',
            'toronto': 'Toronto',
            'vancouver': 'Vancouver',
            'los angeles': 'Los Angeles', 'la': 'Los Angeles',
            'san francisco': 'San Francisco',
            'chicago': 'Chicago',
            'boston': 'Boston',
            'washington': 'Washington DC', 'dc': 'Washington DC',
            'miami': 'Miami',
            'las vegas': 'Las Vegas', 'vegas': 'Las Vegas',
            'seattle': 'Seattle',
            'amsterdam': 'Amsterdam',
            'frankfurt': 'Frankfurt',
            'zurich': 'Zurich',
            'vienna': 'Vienna',
            'rome': 'Rome',
            'milan': 'Milan',
            'barcelona': 'Barcelona',
            'madrid': 'Madrid',
            'lisbon': 'Lisbon',
            'brussels': 'Brussels',
            'copenhagen': 'Copenhagen',
            'stockholm': 'Stockholm',
            'oslo': 'Oslo',
            'helsinki': 'Helsinki',
            'moscow': 'Moscow',
            'istanbul': 'Istanbul',
            'cairo': 'Cairo',
            'johannesburg': 'Johannesburg',
            'cape town': 'Cape Town',
            'nairobi': 'Nairobi',
            'lagos': 'Lagos',
            'casablanca': 'Casablanca',
            'doha': 'Doha',
            'abu dhabi': 'Abu Dhabi',
            'riyadh': 'Riyadh',
            'jeddah': 'Jeddah',
            'kuwait': 'Kuwait City',
            'muscat': 'Muscat',
            'tehran': 'Tehran',
            'baghdad': 'Baghdad',
            'beirut': 'Beirut',
            'tel aviv': 'Tel Aviv',
            'jerusalem': 'Jerusalem',
            'hong kong': 'Hong Kong',
            'macau': 'Macau',
            'taipei': 'Taipei',
            'seoul': 'Seoul',
            'busan': 'Busan',
            'osaka': 'Osaka',
            'kyoto': 'Kyoto',
            'manila': 'Manila',
            'jakarta': 'Jakarta',
            'kuala lumpur': 'Kuala Lumpur',
            'ho chi minh': 'Ho Chi Minh City', 'saigon': 'Ho Chi Minh City',
            'hanoi': 'Hanoi',
            'phnom penh': 'Phnom Penh',
            'yangon': 'Yangon', 'rangoon': 'Yangon',
            'dhaka': 'Dhaka',
            'kathmandu': 'Kathmandu',
            'colombo': 'Colombo',
            'male': 'Male',
            'perth': 'Perth',
            'brisbane': 'Brisbane',
            'adelaide': 'Adelaide',
            'auckland': 'Auckland',
            'wellington': 'Wellington',
            'christchurch': 'Christchurch',
            'fiji': 'Suva',
            'tahiti': 'Papeete'
        }
        
        # Time expressions
        self.time_patterns = {
            'morning': ['morning', 'am', 'early'],
            'afternoon': ['afternoon', 'noon', 'pm'],
            'evening': ['evening', 'night', 'late'],
            'today': ['today', 'now'],
            'tomorrow': ['tomorrow'],
            'next week': ['next week', 'week'],
            'weekend': ['weekend', 'saturday', 'sunday']
        }
        
        # Class preferences
        self.class_patterns = {
            'ECONOMY': ['economy', 'cheap', 'budget', 'basic'],
            'BUSINESS': ['business', 'premium', 'comfort'],
            'FIRST': ['first', 'luxury', 'first class']
        }
        
        # Price preferences
        self.price_patterns = {
            'low': ['cheap', 'budget', 'affordable', 'low cost', 'economical'],
            'medium': ['reasonable', 'moderate', 'average'],
            'high': ['expensive', 'premium', 'luxury', 'first class']
        }
        
        # Intent patterns
        self.intent_patterns = {
            'search': [
                r'find.*flight', r'search.*flight', r'look.*flight',
                r'show.*flight', r'get.*flight', r'flight.*to',
                r'travel.*to', r'go.*to', r'fly.*to'
            ],
            'book': [
                r'book.*flight', r'reserve.*flight', r'buy.*ticket',
                r'purchase.*flight', r'confirm.*booking'
            ],
            'cancel': [
                r'cancel.*flight', r'cancel.*booking', r'cancel.*ticket'
            ],
            'modify': [
                r'change.*flight', r'modify.*booking', r'reschedule.*flight',
                r'update.*booking'
            ]
        }
        
        logger.info("🎤 Voice Booking Service initialized with comprehensive city mappings")
    
    def process_voice_command(self, audio_data: bytes = None, text_input: str = None) -> VoiceCommand:
        """
        Process voice command from audio or text input
        """
        try:
            if text_input:
                # Direct text input (for testing or text-based voice commands)
                raw_text = text_input.lower().strip()
            else:
                # Process audio data
                raw_text = self._speech_to_text(audio_data)
            
            if not raw_text:
                return VoiceCommand(
                    intent="unknown",
                    entities={},
                    confidence=0.0,
                    raw_text="",
                    processed_text=""
                )
            
            # Clean and process text
            processed_text = self._clean_text(raw_text)
            
            # Extract intent and entities
            intent = self._extract_intent(processed_text)
            entities = self._extract_entities(processed_text)
            confidence = self._calculate_confidence(intent, entities, processed_text)
            
            return VoiceCommand(
                intent=intent,
                entities=entities,
                confidence=confidence,
                raw_text=raw_text,
                processed_text=processed_text
            )
            
        except Exception as e:
            logger.error(f"Voice command processing failed: {e}")
            return VoiceCommand(
                intent="error",
                entities={"error": str(e)},
                confidence=0.0,
                raw_text=raw_text if 'raw_text' in locals() else "",
                processed_text=""
            )
    
    def _speech_to_text(self, audio_data: bytes) -> str:
        """Convert speech audio to text"""
        try:
            # Initialize speech recognition
            r = sr.Recognizer()
            
            # Convert audio data to AudioFile
            with sr.AudioFile(audio_data) as source:
                audio = r.record(source)
            
            # Recognize speech using Google Speech Recognition
            text = r.recognize_google(audio)
            logger.info(f"🎤 Speech recognized: {text}")
            return text.lower()
            
        except sr.UnknownValueError:
            logger.warning("Could not understand audio")
            return ""
        except sr.RequestError as e:
            logger.error(f"Speech recognition error: {e}")
            return ""
        except Exception as e:
            logger.error(f"Speech to text conversion failed: {e}")
            return ""
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra spaces and punctuation
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip().lower()
    
    def _extract_intent(self, text: str) -> str:
        """Extract user intent from text"""
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    return intent
        
        # Default to search if cities are mentioned
        if self._has_cities(text):
            return "search"
        
        return "unknown"
    
    def _extract_entities(self, text: str) -> Dict[str, Any]:
        """Extract entities (cities, dates, preferences) from text"""
        entities = {}
        
        # Extract cities
        cities = self._extract_cities(text)
        if len(cities) >= 1:
            entities['from_city'] = cities[0]
        if len(cities) >= 2:
            entities['to_city'] = cities[1]
        elif len(cities) == 1:
            # If only one city mentioned, assume it's destination
            entities['to_city'] = cities[0]
        
        # Extract time preferences
        time_pref = self._extract_time_preference(text)
        if time_pref:
            entities['time_preference'] = time_pref
        
        # Extract class preferences
        class_pref = self._extract_class_preference(text)
        if class_pref:
            entities['class_preference'] = class_pref
        
        # Extract price preferences
        price_pref = self._extract_price_preference(text)
        if price_pref:
            entities['price_preference'] = price_pref
        
        # Extract passenger count
        passengers = self._extract_passenger_count(text)
        if passengers:
            entities['passengers'] = passengers
        
        # Extract dates
        dates = self._extract_dates(text)
        if dates:
            entities.update(dates)
        
        return entities
    
    def _extract_cities(self, text: str) -> List[str]:
        """Extract city names from text"""
        cities = []
        
        # Look for city patterns
        for city_key, city_name in self.city_mappings.items():
            if city_key in text:
                if city_name not in cities:
                    cities.append(city_name)
        
        return cities
    
    def _has_cities(self, text: str) -> bool:
        """Check if text contains city names"""
        return any(city_key in text for city_key in self.city_mappings.keys())
    
    def _extract_time_preference(self, text: str) -> Optional[str]:
        """Extract time preference from text"""
        for time_key, patterns in self.time_patterns.items():
            for pattern in patterns:
                if pattern in text:
                    return time_key
        return None
    
    def _extract_class_preference(self, text: str) -> Optional[str]:
        """Extract class preference from text"""
        for class_key, patterns in self.class_patterns.items():
            for pattern in patterns:
                if pattern in text:
                    return class_key
        return None
    
    def _extract_price_preference(self, text: str) -> Optional[str]:
        """Extract price preference from text"""
        for price_key, patterns in self.price_patterns.items():
            for pattern in patterns:
                if pattern in text:
                    return price_key
        return None
    
    def _extract_passenger_count(self, text: str) -> Optional[int]:
        """Extract number of passengers from text"""
        # Look for number patterns
        number_patterns = {
            'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
            'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10
        }
        
        for word, number in number_patterns.items():
            if word in text:
                return number
        
        # Look for digit patterns
        digit_match = re.search(r'(\d+)\s*(?:passenger|people|person|ticket)', text)
        if digit_match:
            return int(digit_match.group(1))
        
        return None
    
    def _extract_dates(self, text: str) -> Dict[str, str]:
        """Extract dates from text"""
        dates = {}
        
        # Simple date extraction
        if 'today' in text:
            dates['departure_date'] = datetime.now().strftime('%Y-%m-%d')
        elif 'tomorrow' in text:
            dates['departure_date'] = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        elif 'next week' in text:
            dates['departure_date'] = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        
        return dates
    
    def _calculate_confidence(self, intent: str, entities: Dict[str, Any], text: str) -> float:
        """Calculate confidence score for the parsed command"""
        confidence = 0.0
        
        # Base confidence for recognized intent
        if intent != "unknown":
            confidence += 0.3
        
        # Confidence for entities
        if entities.get('from_city') or entities.get('to_city'):
            confidence += 0.4
        
        if entities.get('time_preference'):
            confidence += 0.1
        
        if entities.get('class_preference'):
            confidence += 0.1
        
        if entities.get('departure_date'):
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def convert_to_booking_intent(self, voice_command: VoiceCommand) -> BookingIntent:
        """Convert voice command to structured booking intent"""
        entities = voice_command.entities
        
        return BookingIntent(
            action=voice_command.intent,
            from_city=entities.get('from_city'),
            to_city=entities.get('to_city'),
            departure_date=entities.get('departure_date'),
            return_date=entities.get('return_date'),
            passengers=entities.get('passengers', 1),
            class_preference=entities.get('class_preference', 'ECONOMY'),
            time_preference=entities.get('time_preference'),
            price_preference=entities.get('price_preference')
        )
    
    def generate_response(self, voice_command: VoiceCommand, booking_intent: BookingIntent) -> Dict[str, Any]:
        """Generate appropriate response for voice command"""
        if voice_command.confidence < 0.3:
            return {
                "success": False,
                "message": "I didn't understand that. Could you please repeat your request?",
                "suggestions": [
                    "Try: 'Find flights from Mumbai to Delhi'",
                    "Try: 'Book a cheap flight to Bangalore tomorrow'",
                    "Try: 'Show me business class flights to Singapore'"
                ]
            }
        
        if booking_intent.action == "search":
            return self._generate_search_response(booking_intent)
        elif booking_intent.action == "book":
            return self._generate_booking_response(booking_intent)
        elif booking_intent.action == "cancel":
            return self._generate_cancel_response(booking_intent)
        elif booking_intent.action == "modify":
            return self._generate_modify_response(booking_intent)
        else:
            return {
                "success": False,
                "message": "I can help you search, book, cancel, or modify flights. What would you like to do?",
                "suggestions": [
                    "Search for flights",
                    "Book a flight",
                    "Cancel a booking",
                    "Modify a booking"
                ]
            }
    
    def _generate_search_response(self, intent: BookingIntent) -> Dict[str, Any]:
        """Generate response for flight search"""
        message_parts = ["I'll help you find flights"]
        
        if intent.from_city and intent.to_city:
            message_parts.append(f"from {intent.from_city} to {intent.to_city}")
        elif intent.to_city:
            message_parts.append(f"to {intent.to_city}")
        elif intent.from_city:
            message_parts.append(f"from {intent.from_city}")
        
        if intent.departure_date:
            message_parts.append(f"on {intent.departure_date}")
        
        if intent.class_preference != "ECONOMY":
            message_parts.append(f"in {intent.class_preference.lower()} class")
        
        if intent.passengers > 1:
            message_parts.append(f"for {intent.passengers} passengers")
        
        message = " ".join(message_parts) + "."
        
        return {
            "success": True,
            "message": message,
            "action": "search_flights",
            "parameters": {
                "from_city": intent.from_city,
                "to_city": intent.to_city,
                "departure_date": intent.departure_date,
                "class": intent.class_preference,
                "passengers": intent.passengers,
                "time_preference": intent.time_preference,
                "price_preference": intent.price_preference
            }
        }
    
    def _generate_booking_response(self, intent: BookingIntent) -> Dict[str, Any]:
        """Generate response for flight booking"""
        if not intent.from_city or not intent.to_city:
            return {
                "success": False,
                "message": "To book a flight, I need both departure and destination cities. Could you specify both?",
                "action": "request_details"
            }
        
        message = f"I'll help you book a flight from {intent.from_city} to {intent.to_city}"
        
        if intent.departure_date:
            message += f" on {intent.departure_date}"
        
        message += ". Let me search for available options first."
        
        return {
            "success": True,
            "message": message,
            "action": "search_and_book",
            "parameters": {
                "from_city": intent.from_city,
                "to_city": intent.to_city,
                "departure_date": intent.departure_date,
                "class": intent.class_preference,
                "passengers": intent.passengers
            }
        }
    
    def _generate_cancel_response(self, intent: BookingIntent) -> Dict[str, Any]:
        """Generate response for booking cancellation"""
        return {
            "success": True,
            "message": "I can help you cancel your booking. Please provide your booking reference number or email address.",
            "action": "cancel_booking",
            "parameters": {}
        }
    
    def _generate_modify_response(self, intent: BookingIntent) -> Dict[str, Any]:
        """Generate response for booking modification"""
        return {
            "success": True,
            "message": "I can help you modify your booking. Please provide your booking reference number and what you'd like to change.",
            "action": "modify_booking",
            "parameters": {}
        }

# Global voice service instance
_voice_service = None

def get_voice_service() -> VoiceBookingService:
    """Get or create voice booking service instance"""
    global _voice_service
    if _voice_service is None:
        _voice_service = VoiceBookingService()
    return _voice_service
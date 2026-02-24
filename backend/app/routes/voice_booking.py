"""
Voice Booking API routes - Voice-powered flight booking
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from typing import Dict, Any, Optional
from pydantic import BaseModel
import logging

from app.routes.auth import get_current_user
from app.services.voice_booking_service import get_voice_service
from app.services.live_monitoring import get_monitoring_service
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/voice-booking", tags=["voice-booking"])

# Request/Response models
class VoiceTextRequest(BaseModel):
    text: str
    language: str = "en"

class VoiceCommandResponse(BaseModel):
    success: bool
    message: str
    action: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    suggestions: Optional[list] = None
    confidence: float
    raw_text: str
    processed_text: str

@router.post("/process-text", response_model=VoiceCommandResponse)
async def process_voice_text(
    request: VoiceTextRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Process voice command from text input
    """
    try:
        # Log activity
        monitoring = get_monitoring_service()
        monitoring.log_activity("VOICE_COMMAND_TEXT", current_user.id, {
            "text": request.text[:100],  # First 100 chars for privacy
            "language": request.language
        })
        
        # Get voice service
        voice_service = get_voice_service()
        
        # Process voice command
        voice_command = voice_service.process_voice_command(text_input=request.text)
        
        # Convert to booking intent
        booking_intent = voice_service.convert_to_booking_intent(voice_command)
        
        # Generate response
        response = voice_service.generate_response(voice_command, booking_intent)
        
        return VoiceCommandResponse(
            success=response["success"],
            message=response["message"],
            action=response.get("action"),
            parameters=response.get("parameters"),
            suggestions=response.get("suggestions"),
            confidence=voice_command.confidence,
            raw_text=voice_command.raw_text,
            processed_text=voice_command.processed_text
        )
        
    except Exception as e:
        logger.error(f"Voice text processing failed: {e}")
        raise HTTPException(status_code=500, detail="Voice processing failed")

@router.post("/process-audio", response_model=VoiceCommandResponse)
async def process_voice_audio(
    audio_file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Process voice command from audio file
    """
    try:
        # Validate audio file
        if not audio_file.content_type.startswith('audio/'):
            raise HTTPException(status_code=400, detail="Invalid audio file format")
        
        # Log activity
        monitoring = get_monitoring_service()
        monitoring.log_activity("VOICE_COMMAND_AUDIO", current_user.id, {
            "filename": audio_file.filename,
            "content_type": audio_file.content_type,
            "size": audio_file.size if hasattr(audio_file, 'size') else 'unknown'
        })
        
        # Read audio data
        audio_data = await audio_file.read()
        
        # Get voice service
        voice_service = get_voice_service()
        
        # Process voice command
        voice_command = voice_service.process_voice_command(audio_data=audio_data)
        
        # Convert to booking intent
        booking_intent = voice_service.convert_to_booking_intent(voice_command)
        
        # Generate response
        response = voice_service.generate_response(voice_command, booking_intent)
        
        return VoiceCommandResponse(
            success=response["success"],
            message=response["message"],
            action=response.get("action"),
            parameters=response.get("parameters"),
            suggestions=response.get("suggestions"),
            confidence=voice_command.confidence,
            raw_text=voice_command.raw_text,
            processed_text=voice_command.processed_text
        )
        
    except Exception as e:
        logger.error(f"Voice audio processing failed: {e}")
        raise HTTPException(status_code=500, detail="Voice processing failed")

@router.get("/supported-commands")
async def get_supported_commands():
    """
    Get list of supported voice commands and examples
    """
    return {
        "commands": {
            "search": {
                "description": "Search for flights",
                "examples": [
                    "Find flights from Mumbai to Delhi",
                    "Show me cheap flights to Bangalore",
                    "Search for business class flights to Singapore tomorrow",
                    "Look for morning flights from Chennai to Hyderabad"
                ]
            },
            "book": {
                "description": "Book a flight",
                "examples": [
                    "Book a flight from Delhi to Mumbai",
                    "Reserve two tickets to Bangalore tomorrow",
                    "Purchase business class flight to Dubai",
                    "Book economy flight for 4 passengers to Goa"
                ]
            },
            "cancel": {
                "description": "Cancel a booking",
                "examples": [
                    "Cancel my flight booking",
                    "Cancel ticket to Mumbai",
                    "Remove my reservation"
                ]
            },
            "modify": {
                "description": "Modify existing booking",
                "examples": [
                    "Change my flight to tomorrow",
                    "Modify booking to business class",
                    "Reschedule my flight to next week"
                ]
            }
        },
        "supported_cities": {
            "indian_cities": [
                "Mumbai", "Delhi", "Bangalore", "Chennai", "Hyderabad", "Pune", 
                "Kolkata", "Ahmedabad", "Jaipur", "Lucknow", "Kanpur", "Nagpur",
                "Indore", "Thane", "Bhopal", "Visakhapatnam", "Patna", "Vadodara",
                "Ghaziabad", "Ludhiana", "Agra", "Nashik", "Faridabad", "Meerut",
                "Rajkot", "Varanasi", "Srinagar", "Aurangabad", "Dhanbad", "Amritsar",
                "Allahabad", "Ranchi", "Howrah", "Coimbatore", "Jabalpur", "Gwalior"
            ],
            "international_cities": [
                "Dubai", "Singapore", "Bangkok", "London", "New York", "Tokyo",
                "Paris", "Sydney", "Melbourne", "Toronto", "Los Angeles", "Amsterdam",
                "Frankfurt", "Hong Kong", "Kuala Lumpur", "Doha", "Abu Dhabi"
            ]
        },
        "time_expressions": [
            "today", "tomorrow", "next week", "weekend",
            "morning", "afternoon", "evening", "night"
        ],
        "class_preferences": [
            "economy", "business", "first class", "premium"
        ],
        "price_preferences": [
            "cheap", "budget", "affordable", "reasonable", "premium", "luxury"
        ]
    }

@router.get("/voice-tips")
async def get_voice_tips():
    """
    Get tips for better voice recognition
    """
    return {
        "tips": [
            "Speak clearly and at a moderate pace",
            "Use full city names (e.g., 'Mumbai' instead of 'Bombay')",
            "Include specific dates when possible (e.g., 'tomorrow', 'next Monday')",
            "Mention the number of passengers if more than one",
            "Specify class preference if not economy",
            "Use simple, direct sentences",
            "Avoid background noise for better recognition"
        ],
        "best_practices": [
            "Start with action words: 'Find', 'Book', 'Search', 'Show'",
            "Include both departure and destination cities",
            "Mention time preferences: 'morning flight', 'evening departure'",
            "Be specific about dates: 'December 25th' or 'next Friday'",
            "State passenger count: 'for 2 people', 'for family of 4'"
        ],
        "common_phrases": {
            "search": [
                "Find flights from [city] to [city]",
                "Show me flights to [city] tomorrow",
                "Search for cheap flights to [city]",
                "Look for business class flights to [city]"
            ],
            "book": [
                "Book a flight from [city] to [city]",
                "Reserve tickets to [city] for [date]",
                "Purchase [number] tickets to [city]",
                "Book [class] class flight to [city]"
            ]
        }
    }

@router.post("/test-voice-command")
async def test_voice_command(
    command: str,
    current_user: User = Depends(get_current_user)
):
    """
    Test voice command processing (for development/testing)
    """
    try:
        voice_service = get_voice_service()
        
        # Process command
        voice_command = voice_service.process_voice_command(text_input=command)
        booking_intent = voice_service.convert_to_booking_intent(voice_command)
        response = voice_service.generate_response(voice_command, booking_intent)
        
        return {
            "input": command,
            "voice_command": {
                "intent": voice_command.intent,
                "entities": voice_command.entities,
                "confidence": voice_command.confidence,
                "raw_text": voice_command.raw_text,
                "processed_text": voice_command.processed_text
            },
            "booking_intent": {
                "action": booking_intent.action,
                "from_city": booking_intent.from_city,
                "to_city": booking_intent.to_city,
                "departure_date": booking_intent.departure_date,
                "passengers": booking_intent.passengers,
                "class_preference": booking_intent.class_preference,
                "time_preference": booking_intent.time_preference,
                "price_preference": booking_intent.price_preference
            },
            "response": response
        }
        
    except Exception as e:
        logger.error(f"Voice command test failed: {e}")
        raise HTTPException(status_code=500, detail="Voice command test failed")

@router.get("/voice-analytics")
async def get_voice_analytics(
    current_user: User = Depends(get_current_user)
):
    """
    Get voice command analytics for admin users
    """
    # Check if user is admin
    if current_user.email != "test@safetravelapp.com":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # This would typically pull from a database of voice command logs
    return {
        "total_commands": 1247,
        "success_rate": 87.3,
        "most_common_intents": [
            {"intent": "search", "count": 892, "percentage": 71.5},
            {"intent": "book", "count": 234, "percentage": 18.8},
            {"intent": "modify", "count": 78, "percentage": 6.3},
            {"intent": "cancel", "count": 43, "percentage": 3.4}
        ],
        "popular_routes": [
            {"route": "Mumbai → Delhi", "count": 156},
            {"route": "Bangalore → Chennai", "count": 134},
            {"route": "Delhi → Goa", "count": 98},
            {"route": "Mumbai → Dubai", "count": 87},
            {"route": "Chennai → Singapore", "count": 76}
        ],
        "confidence_distribution": {
            "high (>0.8)": 68.2,
            "medium (0.5-0.8)": 23.1,
            "low (<0.5)": 8.7
        },
        "language_usage": {
            "english": 94.2,
            "hindi": 4.1,
            "other": 1.7
        },
        "time_preferences": {
            "morning": 34.5,
            "evening": 28.7,
            "afternoon": 21.3,
            "any_time": 15.5
        }
    }
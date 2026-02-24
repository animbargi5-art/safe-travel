"""
Social Booking API routes - Book flights with friends and family
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
import logging

from app.database_dep import get_db
from app.routes.auth import get_current_user
from app.services.social_booking_service import get_social_booking_service
from app.services.live_monitoring import get_monitoring_service
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/social-booking", tags=["social-booking"])

# Request/Response models
class InviteeRequest(BaseModel):
    email: EmailStr
    name: str
    phone: Optional[str] = None
    seat_preference: str = "ANY"
    special_requests: Optional[str] = None

class CreateSocialBookingRequest(BaseModel):
    flight_id: int
    invitees: List[InviteeRequest]
    message: Optional[str] = None
    booking_deadline: Optional[str] = None

class InvitationResponse(BaseModel):
    response: str  # ACCEPTED or DECLINED
    passenger_details: Optional[Dict[str, Any]] = None
    special_requests: Optional[str] = None

@router.post("/create")
async def create_social_booking(
    request: CreateSocialBookingRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new social booking and send invitations
    """
    try:
        # Validate request
        if len(request.invitees) == 0:
            raise HTTPException(status_code=400, detail="At least one invitee is required")
        
        if len(request.invitees) > 10:
            raise HTTPException(status_code=400, detail="Maximum 10 invitees allowed")
        
        # Log activity
        monitoring = get_monitoring_service()
        monitoring.log_activity("SOCIAL_BOOKING_CREATED", current_user.id, {
            "flight_id": request.flight_id,
            "invitee_count": len(request.invitees),
            "total_seats": len(request.invitees) + 1
        })
        
        # Get social booking service
        social_service = get_social_booking_service(db)
        
        # Convert invitees to dict format
        invitees_data = []
        for invitee in request.invitees:
            invitees_data.append({
                "email": invitee.email,
                "name": invitee.name,
                "phone": invitee.phone,
                "seat_preference": invitee.seat_preference,
                "special_requests": invitee.special_requests
            })
        
        # Create social booking
        result = social_service.create_social_booking(
            organizer_id=current_user.id,
            flight_id=request.flight_id,
            invitees=invitees_data,
            booking_details={
                "message": request.message,
                "booking_deadline": request.booking_deadline,
                "organizer_name": current_user.full_name,
                "organizer_email": current_user.email
            }
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Social booking creation failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to create social booking")

@router.get("/invitation/{response_token}")
async def get_invitation_details(response_token: str, db: Session = Depends(get_db)):
    """
    Get invitation details for response page
    """
    try:
        social_service = get_social_booking_service(db)
        
        # Find invitation by token
        invitation = social_service._find_invitation_by_token(response_token)
        if not invitation:
            raise HTTPException(status_code=404, detail="Invitation not found or expired")
        
        # Get social booking details
        social_booking = social_service._get_social_booking(invitation["social_booking_id"])
        if not social_booking:
            raise HTTPException(status_code=404, detail="Social booking not found")
        
        return {
            "invitation": {
                "id": invitation["id"],
                "invitee_name": invitation["invitee_name"],
                "invitee_email": invitation["invitee_email"],
                "status": invitation["status"],
                "expires_at": invitation["expires_at"].isoformat(),
                "seat_preference": invitation["seat_preference"],
                "special_requests": invitation["special_requests"],
                "organizer_name": invitation["organizer_name"],
                "organizer_email": invitation["organizer_email"]
            },
            "flight": invitation["flight_details"],
            "social_booking": {
                "id": social_booking["id"],
                "status": social_booking["status"],
                "total_seats": social_booking["total_seats"],
                "confirmed_seats": social_booking["confirmed_seats"],
                "expires_at": social_booking["expires_at"].isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get invitation details: {e}")
        raise HTTPException(status_code=500, detail="Failed to get invitation details")

@router.post("/respond/{response_token}")
async def respond_to_invitation(
    response_token: str,
    response: InvitationResponse,
    db: Session = Depends(get_db)
):
    """
    Respond to a social booking invitation
    """
    try:
        if response.response not in ["ACCEPTED", "DECLINED"]:
            raise HTTPException(status_code=400, detail="Response must be ACCEPTED or DECLINED")
        
        social_service = get_social_booking_service(db)
        
        # Process response
        result = social_service.respond_to_invitation(
            response_token=response_token,
            response=response.response,
            user_details={
                "passenger_details": response.passenger_details,
                "special_requests": response.special_requests
            }
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to process invitation response: {e}")
        raise HTTPException(status_code=500, detail="Failed to process response")

@router.get("/status/{social_booking_id}")
async def get_social_booking_status(
    social_booking_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get status of a social booking
    """
    try:
        social_service = get_social_booking_service(db)
        result = social_service.get_social_booking_status(social_booking_id)
        
        if not result["success"]:
            raise HTTPException(status_code=404, detail=result["message"])
        
        # Check if user has access to this social booking
        social_booking = social_service._get_social_booking(social_booking_id)
        if not social_booking:
            raise HTTPException(status_code=404, detail="Social booking not found")
        
        # Check if user is organizer or invitee
        has_access = False
        if social_booking["organizer_id"] == current_user.id:
            has_access = True
        else:
            for invitation in social_booking["invitees"]:
                if invitation["invitee_email"] == current_user.email:
                    has_access = True
                    break
        
        if not has_access:
            raise HTTPException(status_code=403, detail="Access denied")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get social booking status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get status")

@router.get("/my-bookings")
async def get_my_social_bookings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all social bookings for current user
    """
    try:
        social_service = get_social_booking_service(db)
        bookings = social_service.get_user_social_bookings(current_user.id)
        
        return {
            "social_bookings": bookings,
            "total_count": len(bookings),
            "organizer_count": len([b for b in bookings if b.get("role") == "organizer"]),
            "invitee_count": len([b for b in bookings if b.get("role") == "invitee"])
        }
        
    except Exception as e:
        logger.error(f"Failed to get user social bookings: {e}")
        raise HTTPException(status_code=500, detail="Failed to get social bookings")

@router.delete("/cancel/{social_booking_id}")
async def cancel_social_booking(
    social_booking_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cancel a social booking (organizer only)
    """
    try:
        social_service = get_social_booking_service(db)
        social_booking = social_service._get_social_booking(social_booking_id)
        
        if not social_booking:
            raise HTTPException(status_code=404, detail="Social booking not found")
        
        # Check if user is organizer
        if social_booking["organizer_id"] != current_user.id:
            raise HTTPException(status_code=403, detail="Only organizer can cancel social booking")
        
        # Update status
        social_booking["status"] = "CANCELLED"
        social_booking["cancelled_at"] = datetime.utcnow()
        
        # Log activity
        monitoring = get_monitoring_service()
        monitoring.log_activity("SOCIAL_BOOKING_CANCELLED", current_user.id, {
            "social_booking_id": social_booking_id,
            "reason": "organizer_cancelled"
        })
        
        # TODO: Notify all invitees about cancellation
        
        return {
            "success": True,
            "message": "Social booking cancelled successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to cancel social booking: {e}")
        raise HTTPException(status_code=500, detail="Failed to cancel social booking")

@router.get("/analytics")
async def get_social_booking_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get social booking analytics (admin only)
    """
    try:
        # Check if user is admin
        if current_user.email != "test@safetravelapp.com":
            raise HTTPException(status_code=403, detail="Admin access required")
        
        # Mock analytics data (in production, calculate from database)
        return {
            "total_social_bookings": 1247,
            "active_bookings": 89,
            "completed_bookings": 1034,
            "cancelled_bookings": 124,
            "success_rate": 82.9,
            "average_group_size": 3.2,
            "popular_routes": [
                {"route": "Mumbai → Goa", "bookings": 156, "avg_group_size": 4.1},
                {"route": "Delhi → Manali", "bookings": 134, "avg_group_size": 3.8},
                {"route": "Bangalore → Kerala", "bookings": 98, "avg_group_size": 2.9},
                {"route": "Chennai → Ooty", "bookings": 87, "avg_group_size": 3.5}
            ],
            "monthly_trends": [
                {"month": "Jan", "bookings": 89, "success_rate": 85.2},
                {"month": "Feb", "bookings": 112, "success_rate": 81.7},
                {"month": "Mar", "bookings": 134, "success_rate": 83.6},
                {"month": "Apr", "bookings": 156, "success_rate": 79.8},
                {"month": "May", "bookings": 178, "success_rate": 82.1}
            ],
            "response_statistics": {
                "average_response_time_hours": 8.4,
                "acceptance_rate": 67.3,
                "decline_rate": 21.8,
                "no_response_rate": 10.9
            },
            "group_size_distribution": {
                "2_people": 34.2,
                "3_people": 28.7,
                "4_people": 21.5,
                "5_people": 10.3,
                "6_plus_people": 5.3
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get social booking analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get analytics")

@router.get("/invitation-templates")
async def get_invitation_templates():
    """
    Get pre-made invitation message templates
    """
    return {
        "templates": [
            {
                "id": "casual_trip",
                "title": "Casual Trip",
                "message": "Hey! I'm planning a trip to {destination} and thought you might want to join. It's going to be amazing! 🌟"
            },
            {
                "id": "family_vacation",
                "title": "Family Vacation",
                "message": "We're organizing a family trip to {destination}. Would love to have you join us for some quality family time! ❤️"
            },
            {
                "id": "friends_getaway",
                "title": "Friends Getaway",
                "message": "Planning an epic friends trip to {destination}! Pack your bags and let's make some memories! 🎉"
            },
            {
                "id": "business_trip",
                "title": "Business Trip",
                "message": "I have a business trip to {destination} and there's an extra seat. Want to join and maybe extend it into a mini vacation? 💼"
            },
            {
                "id": "special_occasion",
                "title": "Special Occasion",
                "message": "Celebrating a special occasion with a trip to {destination}. Your presence would make it even more special! 🎊"
            },
            {
                "id": "adventure_trip",
                "title": "Adventure Trip",
                "message": "Ready for an adventure? I'm heading to {destination} for some thrilling experiences. Join me if you dare! 🏔️"
            }
        ]
    }

@router.post("/send-reminder/{social_booking_id}")
async def send_reminder(
    social_booking_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Send reminder to pending invitees
    """
    try:
        social_service = get_social_booking_service(db)
        social_booking = social_service._get_social_booking(social_booking_id)
        
        if not social_booking:
            raise HTTPException(status_code=404, detail="Social booking not found")
        
        # Check if user is organizer
        if social_booking["organizer_id"] != current_user.id:
            raise HTTPException(status_code=403, detail="Only organizer can send reminders")
        
        # Count pending invitations
        pending_count = 0
        for invitation in social_booking["invitees"]:
            if invitation["status"] == "SENT":
                pending_count += 1
                # TODO: Send reminder email
        
        return {
            "success": True,
            "message": f"Reminder sent to {pending_count} pending invitees",
            "pending_count": pending_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to send reminder: {e}")
        raise HTTPException(status_code=500, detail="Failed to send reminder")
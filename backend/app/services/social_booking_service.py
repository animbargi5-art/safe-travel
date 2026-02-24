"""
Social Booking Service - Book flights with friends and family
Handles group invitations, shared bookings, and social features
"""

import uuid
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from enum import Enum

from app.models.user import User
from app.models.flight import Flight
from app.models.booking import Booking
from app.services.email_service import email_service
from app.services.notification_service import get_notification_service

logger = logging.getLogger(__name__)

class SocialBookingStatus(Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    DECLINED = "DECLINED"
    EXPIRED = "EXPIRED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class InvitationStatus(Enum):
    SENT = "SENT"
    ACCEPTED = "ACCEPTED"
    DECLINED = "DECLINED"
    EXPIRED = "EXPIRED"

class SocialBookingService:
    """
    Service for managing social bookings and group travel
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.notification_service = get_notification_service()
    
    def create_social_booking(
        self, 
        organizer_id: int, 
        flight_id: int, 
        invitees: List[Dict[str, Any]],
        booking_details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a new social booking with invitations
        """
        try:
            # Generate unique social booking ID
            social_booking_id = str(uuid.uuid4())
            
            # Get flight details
            flight = self.db.query(Flight).filter(Flight.id == flight_id).first()
            if not flight:
                raise ValueError("Flight not found")
            
            # Get organizer details
            organizer = self.db.query(User).filter(User.id == organizer_id).first()
            if not organizer:
                raise ValueError("Organizer not found")
            
            # Create social booking record
            social_booking = {
                "id": social_booking_id,
                "organizer_id": organizer_id,
                "flight_id": flight_id,
                "status": SocialBookingStatus.PENDING.value,
                "created_at": datetime.utcnow(),
                "expires_at": datetime.utcnow() + timedelta(hours=48),  # 48 hour expiry
                "booking_details": booking_details,
                "invitees": [],
                "responses": {},
                "total_seats": len(invitees) + 1,  # Including organizer
                "confirmed_seats": 0,
                "total_cost": 0.0
            }
            
            # Process invitations
            invitations = []
            for invitee in invitees:
                invitation = self._create_invitation(
                    social_booking_id, 
                    organizer, 
                    flight, 
                    invitee,
                    booking_details
                )
                invitations.append(invitation)
                social_booking["invitees"].append(invitation)
            
            # Store social booking (in production, this would go to database)
            self._store_social_booking(social_booking)
            
            # Send invitations
            for invitation in invitations:
                self._send_invitation(invitation, organizer, flight)
            
            # Log activity
            logger.info(f"Social booking created: {social_booking_id} by user {organizer_id}")
            
            return {
                "success": True,
                "social_booking_id": social_booking_id,
                "status": social_booking["status"],
                "expires_at": social_booking["expires_at"].isoformat(),
                "invitations_sent": len(invitations),
                "total_seats": social_booking["total_seats"],
                "flight": {
                    "id": flight.id,
                    "from_city": flight.from_city,
                    "to_city": flight.to_city,
                    "departure_time": flight.departure_time.isoformat(),
                    "price": flight.price
                }
            }
            
        except Exception as e:
            logger.error(f"Social booking creation failed: {e}")
            raise
    
    def _create_invitation(
        self, 
        social_booking_id: str, 
        organizer: User, 
        flight: Flight, 
        invitee: Dict[str, Any],
        booking_details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create invitation for an invitee"""
        invitation_id = str(uuid.uuid4())
        
        return {
            "id": invitation_id,
            "social_booking_id": social_booking_id,
            "invitee_email": invitee["email"],
            "invitee_name": invitee.get("name", "Friend"),
            "invitee_phone": invitee.get("phone"),
            "status": InvitationStatus.SENT.value,
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(hours=48),
            "seat_preference": invitee.get("seat_preference", "ANY"),
            "special_requests": invitee.get("special_requests", ""),
            "response_token": str(uuid.uuid4()),
            "organizer_name": organizer.full_name,
            "organizer_email": organizer.email,
            "flight_details": {
                "from_city": flight.from_city,
                "to_city": flight.to_city,
                "departure_time": flight.departure_time.isoformat(),
                "price": flight.price,
                "airline": flight.airline
            }
        }
    
    def _store_social_booking(self, social_booking: Dict[str, Any]):
        """Store social booking (in production, use database)"""
        # For demo purposes, we'll store in a simple in-memory cache
        # In production, create proper database tables
        if not hasattr(self, '_social_bookings'):
            self._social_bookings = {}
        
        self._social_bookings[social_booking["id"]] = social_booking
    
    def _send_invitation(self, invitation: Dict[str, Any], organizer: User, flight: Flight):
        """Send invitation email to invitee"""
        try:
            # Create invitation link
            invitation_link = f"https://safetravelapp.com/social-booking/respond/{invitation['response_token']}"
            
            # Email content
            subject = f"✈️ {organizer.full_name} invited you to join a flight to {flight.to_city}!"
            
            html_content = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; color: white;">
                    <h1 style="margin: 0; font-size: 28px;">✈️ Flight Invitation</h1>
                    <p style="margin: 10px 0 0 0; font-size: 16px; opacity: 0.9;">You're invited to travel together!</p>
                </div>
                
                <div style="padding: 30px; background: white;">
                    <h2 style="color: #333; margin-bottom: 20px;">Hi {invitation['invitee_name']}!</h2>
                    
                    <p style="font-size: 16px; line-height: 1.6; color: #555;">
                        <strong>{organizer.full_name}</strong> has invited you to join a group flight booking. 
                        Here are the flight details:
                    </p>
                    
                    <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <h3 style="color: #333; margin-top: 0;">Flight Details</h3>
                        <p style="margin: 5px 0;"><strong>Route:</strong> {flight.from_city} → {flight.to_city}</p>
                        <p style="margin: 5px 0;"><strong>Departure:</strong> {flight.departure_time.strftime('%B %d, %Y at %I:%M %p')}</p>
                        <p style="margin: 5px 0;"><strong>Airline:</strong> {flight.airline}</p>
                        <p style="margin: 5px 0;"><strong>Price:</strong> ${flight.price:,.2f} per person</p>
                    </div>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{invitation_link}" 
                           style="background: #28a745; color: white; padding: 15px 30px; text-decoration: none; 
                                  border-radius: 5px; font-weight: bold; display: inline-block;">
                            ✅ Accept Invitation
                        </a>
                    </div>
                    
                    <p style="font-size: 14px; color: #666; text-align: center;">
                        This invitation expires in 48 hours. Click the button above to accept or decline.
                    </p>
                    
                    <div style="border-top: 1px solid #eee; padding-top: 20px; margin-top: 30px;">
                        <h4 style="color: #333;">Why book together?</h4>
                        <ul style="color: #555; line-height: 1.6;">
                            <li>🎯 Guaranteed seats together</li>
                            <li>💰 Potential group discounts</li>
                            <li>🤝 Shared travel experience</li>
                            <li>📱 Real-time updates for everyone</li>
                        </ul>
                    </div>
                </div>
                
                <div style="background: #f8f9fa; padding: 20px; text-align: center; color: #666; font-size: 12px;">
                    <p>Safe Travel - Making group travel easy and fun!</p>
                    <p>If you have any questions, contact {organizer.full_name} at {organizer.email}</p>
                </div>
            </div>
            """
            
            # Send email
            email_service.send_email(
                to_email=invitation['invitee_email'],
                subject=subject,
                html_content=html_content
            )
            
            logger.info(f"Invitation sent to {invitation['invitee_email']} for social booking {invitation['social_booking_id']}")
            
        except Exception as e:
            logger.error(f"Failed to send invitation: {e}")
    
    def respond_to_invitation(self, response_token: str, response: str, user_details: Dict[str, Any] = None) -> Dict[str, Any]:
        """Respond to a social booking invitation"""
        try:
            # Find invitation by response token
            invitation = self._find_invitation_by_token(response_token)
            if not invitation:
                return {
                    "success": False,
                    "message": "Invalid or expired invitation"
                }
            
            # Check if invitation is still valid
            if datetime.utcnow() > invitation["expires_at"]:
                return {
                    "success": False,
                    "message": "This invitation has expired"
                }
            
            # Update invitation status
            invitation["status"] = response.upper()
            invitation["responded_at"] = datetime.utcnow()
            if user_details:
                invitation["user_details"] = user_details
            
            # Get social booking
            social_booking = self._get_social_booking(invitation["social_booking_id"])
            if not social_booking:
                return {
                    "success": False,
                    "message": "Social booking not found"
                }
            
            # Update social booking responses
            social_booking["responses"][invitation["id"]] = {
                "status": response.upper(),
                "responded_at": datetime.utcnow().isoformat(),
                "invitee_email": invitation["invitee_email"]
            }
            
            # Check if all responses received
            total_invitations = len(social_booking["invitees"])
            total_responses = len(social_booking["responses"])
            accepted_responses = sum(1 for r in social_booking["responses"].values() if r["status"] == "ACCEPTED")
            
            # Update confirmed seats
            social_booking["confirmed_seats"] = accepted_responses + 1  # +1 for organizer
            
            # Notify organizer
            self._notify_organizer_of_response(social_booking, invitation, response)
            
            # Check if booking can be completed
            if total_responses == total_invitations:
                if accepted_responses > 0:
                    # Some people accepted, proceed with booking
                    social_booking["status"] = SocialBookingStatus.ACCEPTED.value
                    self._initiate_group_booking(social_booking)
                else:
                    # Nobody accepted, cancel
                    social_booking["status"] = SocialBookingStatus.CANCELLED.value
            
            return {
                "success": True,
                "message": f"Response recorded: {response}",
                "social_booking_status": social_booking["status"],
                "confirmed_seats": social_booking["confirmed_seats"],
                "total_seats": social_booking["total_seats"],
                "all_responses_received": total_responses == total_invitations
            }
            
        except Exception as e:
            logger.error(f"Failed to process invitation response: {e}")
            return {
                "success": False,
                "message": "Failed to process response"
            }
    
    def _find_invitation_by_token(self, response_token: str) -> Optional[Dict[str, Any]]:
        """Find invitation by response token"""
        if not hasattr(self, '_social_bookings'):
            return None
        
        for social_booking in self._social_bookings.values():
            for invitation in social_booking["invitees"]:
                if invitation["response_token"] == response_token:
                    return invitation
        
        return None
    
    def _get_social_booking(self, social_booking_id: str) -> Optional[Dict[str, Any]]:
        """Get social booking by ID"""
        if not hasattr(self, '_social_bookings'):
            return None
        
        return self._social_bookings.get(social_booking_id)
    
    def _notify_organizer_of_response(self, social_booking: Dict[str, Any], invitation: Dict[str, Any], response: str):
        """Notify organizer of invitation response"""
        try:
            organizer = self.db.query(User).filter(User.id == social_booking["organizer_id"]).first()
            if not organizer:
                return
            
            # Send notification
            message = f"{invitation['invitee_name']} has {response.lower()}ed your flight invitation to {invitation['flight_details']['to_city']}"
            
            # Send real-time notification if organizer is online
            self.notification_service.send_notification(
                user_id=organizer.id,
                notification_type="SOCIAL_BOOKING_RESPONSE",
                title="Flight Invitation Response",
                message=message,
                data={
                    "social_booking_id": social_booking["id"],
                    "invitee_name": invitation["invitee_name"],
                    "response": response,
                    "confirmed_seats": social_booking["confirmed_seats"]
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to notify organizer: {e}")
    
    def _initiate_group_booking(self, social_booking: Dict[str, Any]):
        """Initiate the actual group booking process"""
        try:
            # This would integrate with the existing booking system
            # For now, we'll just update the status and notify participants
            
            social_booking["status"] = SocialBookingStatus.COMPLETED.value
            social_booking["booking_initiated_at"] = datetime.utcnow()
            
            # Calculate total cost
            flight = self.db.query(Flight).filter(Flight.id == social_booking["flight_id"]).first()
            if flight:
                social_booking["total_cost"] = flight.price * social_booking["confirmed_seats"]
            
            # Notify all accepted participants
            organizer = self.db.query(User).filter(User.id == social_booking["organizer_id"]).first()
            
            for invitation in social_booking["invitees"]:
                if social_booking["responses"].get(invitation["id"], {}).get("status") == "ACCEPTED":
                    self._notify_booking_initiation(invitation, social_booking, organizer)
            
            logger.info(f"Group booking initiated for social booking {social_booking['id']}")
            
        except Exception as e:
            logger.error(f"Failed to initiate group booking: {e}")
    
    def _notify_booking_initiation(self, invitation: Dict[str, Any], social_booking: Dict[str, Any], organizer: User):
        """Notify participant that group booking has been initiated"""
        try:
            subject = f"🎉 Group Flight Booking Confirmed - {invitation['flight_details']['to_city']}!"
            
            html_content = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background: linear-gradient(135deg, #28a745 0%, #20c997 100%); padding: 30px; text-align: center; color: white;">
                    <h1 style="margin: 0; font-size: 28px;">🎉 Booking Confirmed!</h1>
                    <p style="margin: 10px 0 0 0; font-size: 16px; opacity: 0.9;">Your group flight is ready to book!</p>
                </div>
                
                <div style="padding: 30px; background: white;">
                    <h2 style="color: #333; margin-bottom: 20px;">Great news, {invitation['invitee_name']}!</h2>
                    
                    <p style="font-size: 16px; line-height: 1.6; color: #555;">
                        Your group flight organized by <strong>{organizer.full_name}</strong> is ready for booking. 
                        {social_booking['confirmed_seats']} people have confirmed their participation.
                    </p>
                    
                    <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <h3 style="color: #333; margin-top: 0;">Next Steps</h3>
                        <ol style="color: #555; line-height: 1.8;">
                            <li>Complete your individual booking and payment</li>
                            <li>Provide passenger details and seat preferences</li>
                            <li>Receive your e-ticket and boarding pass</li>
                            <li>Meet your group at the airport!</li>
                        </ol>
                    </div>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="https://safetravelapp.com/complete-booking/{social_booking['id']}" 
                           style="background: #007bff; color: white; padding: 15px 30px; text-decoration: none; 
                                  border-radius: 5px; font-weight: bold; display: inline-block;">
                            Complete Your Booking
                        </a>
                    </div>
                </div>
            </div>
            """
            
            email_service.send_email(
                to_email=invitation['invitee_email'],
                subject=subject,
                html_content=html_content
            )
            
        except Exception as e:
            logger.error(f"Failed to send booking initiation notification: {e}")
    
    def get_social_booking_status(self, social_booking_id: str) -> Dict[str, Any]:
        """Get status of a social booking"""
        social_booking = self._get_social_booking(social_booking_id)
        if not social_booking:
            return {
                "success": False,
                "message": "Social booking not found"
            }
        
        # Calculate response statistics
        total_invitations = len(social_booking["invitees"])
        responses = social_booking["responses"]
        accepted_count = sum(1 for r in responses.values() if r["status"] == "ACCEPTED")
        declined_count = sum(1 for r in responses.values() if r["status"] == "DECLINED")
        pending_count = total_invitations - len(responses)
        
        return {
            "success": True,
            "social_booking_id": social_booking_id,
            "status": social_booking["status"],
            "organizer_id": social_booking["organizer_id"],
            "flight_id": social_booking["flight_id"],
            "created_at": social_booking["created_at"].isoformat(),
            "expires_at": social_booking["expires_at"].isoformat(),
            "total_seats": social_booking["total_seats"],
            "confirmed_seats": social_booking["confirmed_seats"],
            "total_cost": social_booking.get("total_cost", 0),
            "statistics": {
                "total_invitations": total_invitations,
                "accepted": accepted_count,
                "declined": declined_count,
                "pending": pending_count,
                "response_rate": (len(responses) / total_invitations * 100) if total_invitations > 0 else 0
            },
            "responses": list(responses.values())
        }
    
    def get_user_social_bookings(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all social bookings for a user (as organizer or invitee)"""
        if not hasattr(self, '_social_bookings'):
            return []
        
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return []
        
        user_bookings = []
        
        for social_booking in self._social_bookings.values():
            # Check if user is organizer
            if social_booking["organizer_id"] == user_id:
                user_bookings.append({
                    **social_booking,
                    "role": "organizer",
                    "created_at": social_booking["created_at"].isoformat(),
                    "expires_at": social_booking["expires_at"].isoformat()
                })
            else:
                # Check if user is invitee
                for invitation in social_booking["invitees"]:
                    if invitation["invitee_email"] == user.email:
                        user_bookings.append({
                            **social_booking,
                            "role": "invitee",
                            "invitation_status": invitation["status"],
                            "created_at": social_booking["created_at"].isoformat(),
                            "expires_at": social_booking["expires_at"].isoformat()
                        })
                        break
        
        return sorted(user_bookings, key=lambda x: x["created_at"], reverse=True)

# Helper function to get service instance
def get_social_booking_service(db: Session) -> SocialBookingService:
    """Get social booking service instance"""
    return SocialBookingService(db)
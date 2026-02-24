"""
Email service for sending booking confirmations, payment receipts, and notifications
Supports both SMTP and modern email services like SendGrid, Mailgun
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging
import os
from jinja2 import Environment, FileSystemLoader

from app.core.config import settings

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.smtp_server = getattr(settings, 'SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = getattr(settings, 'SMTP_PORT', 587)
        self.smtp_username = getattr(settings, 'SMTP_USERNAME', '')
        self.smtp_password = getattr(settings, 'SMTP_PASSWORD', '')
        self.from_email = getattr(settings, 'FROM_EMAIL', 'noreply@safetravel.com')
        self.from_name = getattr(settings, 'FROM_NAME', 'Safe Travel')
        
        # Initialize Jinja2 for email templates
        template_dir = os.path.join(os.path.dirname(__file__), '..', 'templates', 'emails')
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))

    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        attachments: Optional[List[Dict[str, Any]]] = None
    ) -> bool:
        """
        Send an email using SMTP
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML email content
            text_content: Plain text email content (optional)
            attachments: List of attachments (optional)
        
        Returns:
            True if email sent successfully, False otherwise
        """
        
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{self.from_name} <{self.from_email}>"
            message["To"] = to_email
            
            # Add text content
            if text_content:
                text_part = MIMEText(text_content, "plain")
                message.attach(text_part)
            
            # Add HTML content
            html_part = MIMEText(html_content, "html")
            message.attach(html_part)
            
            # Add attachments
            if attachments:
                for attachment in attachments:
                    self._add_attachment(message, attachment)
            
            # Send email
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.smtp_username, self.smtp_password)
                server.sendmail(self.from_email, to_email, message.as_string())
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False

    def _add_attachment(self, message: MIMEMultipart, attachment: Dict[str, Any]):
        """Add attachment to email message"""
        try:
            with open(attachment['path'], "rb") as attachment_file:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment_file.read())
            
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {attachment["filename"]}'
            )
            message.attach(part)
        except Exception as e:
            logger.error(f"Failed to add attachment {attachment.get('filename', 'unknown')}: {str(e)}")

    def render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """Render email template with context data"""
        try:
            template = self.jinja_env.get_template(template_name)
            return template.render(**context)
        except Exception as e:
            logger.error(f"Failed to render template {template_name}: {str(e)}")
            return ""

    def send_booking_confirmation(self, booking_data: Dict[str, Any]) -> bool:
        """
        Send booking confirmation email
        
        Args:
            booking_data: Dictionary containing booking information
        
        Returns:
            True if email sent successfully
        """
        
        try:
            context = {
                'booking': booking_data,
                'passenger_name': booking_data.get('passenger_name', 'Valued Traveler'),
                'booking_id': booking_data.get('id'),
                'flight': booking_data.get('flight', {}),
                'seat': booking_data.get('seat', {}),
                'price': booking_data.get('price', 0),
                'created_at': booking_data.get('created_at'),
                'company_name': 'Safe Travel',
                'support_email': 'support@safetravel.com',
                'current_year': datetime.now().year
            }
            
            html_content = self.render_template('booking_confirmation.html', context)
            text_content = self.render_template('booking_confirmation.txt', context)
            
            subject = f"✈️ Booking Confirmation - Flight #{booking_data.get('id')}"
            
            return self.send_email(
                to_email=booking_data.get('passenger_email'),
                subject=subject,
                html_content=html_content,
                text_content=text_content
            )
            
        except Exception as e:
            logger.error(f"Failed to send booking confirmation: {str(e)}")
            return False

    def send_payment_receipt(self, payment_data: Dict[str, Any], booking_data: Dict[str, Any]) -> bool:
        """
        Send payment receipt email
        
        Args:
            payment_data: Dictionary containing payment information
            booking_data: Dictionary containing booking information
        
        Returns:
            True if email sent successfully
        """
        
        try:
            context = {
                'payment': payment_data,
                'booking': booking_data,
                'passenger_name': booking_data.get('passenger_name', 'Valued Customer'),
                'payment_id': payment_data.get('id'),
                'amount': payment_data.get('amount', 0),
                'currency': payment_data.get('currency', 'USD'),
                'payment_date': payment_data.get('completed_at'),
                'flight': booking_data.get('flight', {}),
                'seat': booking_data.get('seat', {}),
                'company_name': 'Safe Travel',
                'support_email': 'support@safetravel.com',
                'current_year': datetime.now().year
            }
            
            html_content = self.render_template('payment_receipt.html', context)
            text_content = self.render_template('payment_receipt.txt', context)
            
            subject = f"💳 Payment Receipt - ${payment_data.get('amount', 0)} for Flight #{booking_data.get('id')}"
            
            return self.send_email(
                to_email=booking_data.get('passenger_email'),
                subject=subject,
                html_content=html_content,
                text_content=text_content
            )
            
        except Exception as e:
            logger.error(f"Failed to send payment receipt: {str(e)}")
            return False

    def send_booking_reminder(self, booking_data: Dict[str, Any], hours_before: int = 24) -> bool:
        """
        Send booking reminder email
        
        Args:
            booking_data: Dictionary containing booking information
            hours_before: Hours before departure to send reminder
        
        Returns:
            True if email sent successfully
        """
        
        try:
            context = {
                'booking': booking_data,
                'passenger_name': booking_data.get('passenger_name', 'Valued Traveler'),
                'hours_before': hours_before,
                'flight': booking_data.get('flight', {}),
                'seat': booking_data.get('seat', {}),
                'departure_time': booking_data.get('flight', {}).get('departure_time'),
                'company_name': 'Safe Travel',
                'support_email': 'support@safetravel.com',
                'current_year': datetime.now().year
            }
            
            html_content = self.render_template('booking_reminder.html', context)
            text_content = self.render_template('booking_reminder.txt', context)
            
            subject = f"⏰ Flight Reminder - Departure in {hours_before} hours"
            
            return self.send_email(
                to_email=booking_data.get('passenger_email'),
                subject=subject,
                html_content=html_content,
                text_content=text_content
            )
            
        except Exception as e:
            logger.error(f"Failed to send booking reminder: {str(e)}")
            return False

    def send_booking_cancellation(self, booking_data: Dict[str, Any], refund_info: Optional[Dict[str, Any]] = None) -> bool:
        """
        Send booking cancellation email
        
        Args:
            booking_data: Dictionary containing booking information
            refund_info: Dictionary containing refund information (optional)
        
        Returns:
            True if email sent successfully
        """
        
        try:
            context = {
                'booking': booking_data,
                'refund': refund_info,
                'passenger_name': booking_data.get('passenger_name', 'Valued Customer'),
                'booking_id': booking_data.get('id'),
                'flight': booking_data.get('flight', {}),
                'seat': booking_data.get('seat', {}),
                'has_refund': refund_info is not None,
                'company_name': 'Safe Travel',
                'support_email': 'support@safetravel.com',
                'current_year': datetime.now().year
            }
            
            html_content = self.render_template('booking_cancellation.html', context)
            text_content = self.render_template('booking_cancellation.txt', context)
            
            subject = f"❌ Booking Cancelled - Flight #{booking_data.get('id')}"
            
            return self.send_email(
                to_email=booking_data.get('passenger_email'),
                subject=subject,
                html_content=html_content,
                text_content=text_content
            )
            
        except Exception as e:
            logger.error(f"Failed to send booking cancellation: {str(e)}")
            return False

    def send_welcome_email(self, user_data: Dict[str, Any]) -> bool:
        """
        Send welcome email to new users
        
        Args:
            user_data: Dictionary containing user information
        
        Returns:
            True if email sent successfully
        """
        
        try:
            context = {
                'user': user_data,
                'user_name': user_data.get('full_name', 'Valued Traveler'),
                'username': user_data.get('username'),
                'company_name': 'Safe Travel',
                'support_email': 'support@safetravel.com',
                'website_url': 'https://safetravel.com',
                'current_year': datetime.now().year
            }
            
            html_content = self.render_template('welcome.html', context)
            text_content = self.render_template('welcome.txt', context)
            
            subject = "🙏 Welcome to Safe Travel - Your Dharma-Aligned Journey Begins"
            
            return self.send_email(
                to_email=user_data.get('email'),
                subject=subject,
                html_content=html_content,
                text_content=text_content
            )
            
        except Exception as e:
            logger.error(f"Failed to send welcome email: {str(e)}")
            return False

# Global email service instance
email_service = EmailService()
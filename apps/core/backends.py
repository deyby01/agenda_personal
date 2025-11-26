"""
Email Backends - Custom email backends for the application.

This module provides custom email backends, including Resend integration.
"""

import logging
from django.core.mail.backends.base import BaseEmailBackend
from django.conf import settings

logger = logging.getLogger(__name__)


class ResendEmailBackend(BaseEmailBackend):
    """
    Custom email backend that uses Resend API to send emails.
    
    This backend integrates with Resend.com to send transactional emails.
    It's compatible with Django's email system and django-allauth.
    
    Configuration:
        RESEND_API_KEY: Your Resend API key
        RESEND_FROM_EMAIL: Default from email address (must be verified in Resend)
        
    Usage in settings.py:
        EMAIL_BACKEND = 'apps.core.backends.ResendEmailBackend'
        RESEND_API_KEY = os.environ.get('RESEND_API_KEY')
        RESEND_FROM_EMAIL = os.environ.get('RESEND_FROM_EMAIL', 'onboarding@resend.dev')
    """
    
    def __init__(self, fail_silently=False, **kwargs):
        super().__init__(fail_silently=fail_silently, **kwargs)
        self.api_key = getattr(settings, 'RESEND_API_KEY', None)
        self.from_email = getattr(settings, 'RESEND_FROM_EMAIL', None) or getattr(settings, 'DEFAULT_FROM_EMAIL', 'onboarding@resend.dev')
        
        if not self.api_key:
            logger.warning(
                "RESEND_API_KEY not configured. Email sending will fail. "
                "Set RESEND_API_KEY in your environment variables."
            )
    
    def send_messages(self, email_messages):
        """
        Send one or more EmailMessage objects using Resend API.
        
        Args:
            email_messages: List of EmailMessage objects to send
            
        Returns:
            int: Number of successfully sent emails
        """
        if not email_messages:
            return 0
        
        if not self.api_key:
            if not self.fail_silently:
                raise ValueError("RESEND_API_KEY is not configured")
            return 0
        
        try:
            import resend
            resend.api_key = self.api_key
        except ImportError:
            if not self.fail_silently:
                raise ImportError(
                    "resend package is not installed. "
                    "Install it with: pip install resend"
                )
            logger.error("resend package is not installed")
            return 0
        
        num_sent = 0
        
        for message in email_messages:
            try:
                # Prepare email data
                email_data = {
                    "from": message.from_email or self.from_email,
                    "to": message.to,
                    "subject": message.subject,
                }
                
                # Add CC and BCC if present
                if message.cc:
                    email_data["cc"] = message.cc
                if message.bcc:
                    email_data["bcc"] = message.bcc
                
                # Add reply-to if present
                if message.reply_to:
                    email_data["reply_to"] = message.reply_to
                
                # Handle email body
                if message.body:
                    # If message has both HTML and text, prefer HTML
                    if hasattr(message, 'alternatives') and message.alternatives:
                        # Find HTML alternative
                        html_content = None
                        for content, mimetype in message.alternatives:
                            if mimetype == 'text/html':
                                html_content = content
                                break
                        
                        if html_content:
                            email_data["html"] = html_content
                            email_data["text"] = message.body
                        else:
                            email_data["text"] = message.body
                    else:
                        # Check if body is HTML (simple check)
                        if '<html' in message.body.lower() or '<body' in message.body.lower():
                            email_data["html"] = message.body
                        else:
                            email_data["text"] = message.body
                
                # Send email via Resend API
                response = resend.Emails.send(email_data)
                
                # Resend returns a dict with 'id' key, not an object
                if response and isinstance(response, dict) and 'id' in response:
                    email_id = response.get('id')
                    logger.info(f"Email sent successfully via Resend. ID: {email_id}")
                    num_sent += 1
                elif response and hasattr(response, 'id'):
                    # Fallback for object response (if API changes)
                    logger.info(f"Email sent successfully via Resend. ID: {response.id}")
                    num_sent += 1
                else:
                    logger.warning(f"Email sent but no ID returned from Resend: {response}")
                    num_sent += 1
                    
            except Exception as e:
                logger.error(f"Error sending email via Resend: {str(e)}", exc_info=True)
                if not self.fail_silently:
                    raise
        
        return num_sent


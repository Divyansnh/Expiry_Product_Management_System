from flask import current_app, render_template
from flask_mail import Message
from app.core.extensions import mail
from app.models.user import User
from typing import List, Dict, Any, Optional, Union, Literal
import logging
import smtplib

logger = logging.getLogger(__name__)

EmailTemplate = Literal[
    'verify_email',
    'reset_password',
    'daily_notification',
    'expiry_notification',
    'password_reset_confirmation'
]

class EmailService:
    """Service for handling email communications."""
    
    def __init__(self) -> None:
        self.mail = mail
    
    def send_email(
        self,
        subject: str,
        recipients: List[str],
        template: EmailTemplate,
        **kwargs: Any
    ) -> bool:
        """Send an email using a template.
        
        Args:
            subject: Email subject
            recipients: List of recipient email addresses
            template: Name of the template to use
            **kwargs: Additional arguments to pass to the template
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        try:
            logger.info(f"Preparing to send email to {recipients}")
            logger.info(f"Using template: {template}")
            logger.info(f"Template kwargs: {kwargs}")
            
            # Verify email configuration
            if not all([
                current_app.config['MAIL_SERVER'],
                current_app.config['MAIL_PORT'],
                current_app.config['MAIL_USERNAME'],
                current_app.config['MAIL_PASSWORD'],
                current_app.config['MAIL_DEFAULT_SENDER']
            ]):
                logger.error("Incomplete email configuration")
                logger.error(f"Mail server: {current_app.config['MAIL_SERVER']}")
                logger.error(f"Mail port: {current_app.config['MAIL_PORT']}")
                logger.error(f"Mail username: {current_app.config['MAIL_USERNAME']}")
                logger.error(f"Mail default sender: {current_app.config['MAIL_DEFAULT_SENDER']}")
                return False
            
            msg = Message(
                subject=subject,
                recipients=recipients,
                sender=current_app.config['MAIL_DEFAULT_SENDER']
            )
            
            # Log email configuration
            logger.info(f"Mail server: {current_app.config['MAIL_SERVER']}")
            logger.info(f"Mail port: {current_app.config['MAIL_PORT']}")
            logger.info(f"Mail use TLS: {current_app.config['MAIL_USE_TLS']}")
            logger.info(f"Mail username: {current_app.config['MAIL_USERNAME']}")
            
            try:
                template_path = f'emails/{template}.html'
                logger.info(f"Attempting to render template: {template_path}")
                msg.html = render_template(template_path, **kwargs)
                logger.info("Email template rendered successfully")
            except Exception as template_error:
                logger.error(f"Error rendering email template {template_path}: {str(template_error)}", exc_info=True)
                return False
            
            try:
                self.mail.send(msg)
                logger.info(f"Email sent successfully to {recipients}")
                return True
            except smtplib.SMTPAuthenticationError as auth_error:
                logger.error("SMTP Authentication failed. Check username and password.")
                logger.error(f"Error details: {str(auth_error)}")
                return False
            except smtplib.SMTPException as smtp_error:
                logger.error(f"SMTP error while sending email: {str(smtp_error)}")
                logger.error(f"Error type: {smtp_error.__class__.__name__}")
                return False
            except Exception as send_error:
                logger.error(f"Unexpected error sending email: {str(send_error)}")
                logger.error(f"Error type: {send_error.__class__.__name__}")
                return False
                
        except Exception as e:
            logger.error(f"Error in send_email: {str(e)}", exc_info=True)
            logger.error(f"Full error details: {e.__class__.__name__}: {str(e)}")
            return False
    
    def send_verification_email(self, user: User) -> bool:
        """Send verification email to user.
        
        Args:
            user: User to send verification email to
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        try:
            # Generate verification code
            user.generate_verification_code()
            
            # Log the attempt with configuration details
            logger.info(f"Attempting to send verification email to {user.email}")
            logger.info(f"Mail server config: {current_app.config['MAIL_SERVER']}:{current_app.config['MAIL_PORT']}")
            logger.info(f"Using TLS: {current_app.config['MAIL_USE_TLS']}")
            logger.info(f"Sender: {current_app.config['MAIL_DEFAULT_SENDER']}")
            
            return self.send_email(
                subject="Verify Your Email",
                recipients=[user.email],
                template='verify_email',
                user=user,
                verification_code=user.verification_code
            )
            
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error while sending verification email: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Failed to send verification email: {str(e)}")
            return False
    
    def send_password_reset_email(self, email: str, token: str) -> bool:
        """Send password reset email.
        
        Args:
            email: Email address to send reset link to
            token: Password reset token
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        logger.info(f"Attempting to send password reset email to {email}")
        logger.info(f"Reset URL: {token}")
        result = self.send_email(
            subject='Reset Your Password - Expiry Tracker',
            recipients=[email],
            template='reset_password',
            email=email,
            reset_url=token
        )
        logger.info(f"Password reset email send result: {result}")
        return result
    
    def send_daily_notification_email(self, user: User, items: List[Dict[str, Any]]) -> bool:
        """Send daily notification email with items that need attention.
        
        Args:
            user: User to send notification to
            items: List of items to notify about
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        if not items:
            logger.info("No items to notify about")
            return False
            
        # Filter out test items and items that don't need attention
        items_needing_attention = [
            item for item in items 
            if not item['name'].lower().startswith('test') and 
            item['days_until_expiry'] <= 7  # Only include items expiring within 7 days
        ]
        
        if not items_needing_attention:
            logger.info("No items need attention at this time")
            return False
            
        logger.info(f"Sending daily notification email to {user.email} with {len(items_needing_attention)} items needing attention")
        return self.send_email(
            subject='Daily Expiry Alert Summary',
            recipients=[user.email],
            template='daily_notification',
            user=user,
            items=items_needing_attention
        )
    
    def send_expiry_notification(self, user: User, item_name: str, days_until_expiry: int) -> bool:
        """Send expiry notification email.
        
        Args:
            user: User to send notification to
            item_name: Name of the expiring item
            days_until_expiry: Number of days until expiry
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        return self.send_email(
            subject=f'Expiry Alert: {item_name}',
            recipients=[user.email],
            template='expiry_notification',
            user=user,
            item_name=item_name,
            days_until_expiry=days_until_expiry
        )

    def send_password_reset_confirmation(self, email: str) -> bool:
        """Send confirmation email after password reset.
        
        Args:
            email: Email address to send confirmation to
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        try:
            logger.info(f"Sending password reset confirmation email to {email}")
            
            return self.send_email(
                subject='Password Reset Confirmation',
                recipients=[email],
                template='password_reset_confirmation',
                email=email
            )
            
        except Exception as e:
            logger.error(f"Error sending password reset confirmation email: {str(e)}")
            return False 
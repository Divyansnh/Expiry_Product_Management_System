from flask import current_app, render_template
from flask_mail import Message
from app.core.extensions import mail
from app.models.user import User
from typing import List, Dict
import logging
import smtplib

logger = logging.getLogger(__name__)

class EmailService:
    """Service for handling email communications."""
    
    @staticmethod
    def send_email(subject, recipients, template, **kwargs):
        """Send an email using a template."""
        try:
            logger.info(f"Preparing to send email to {recipients}")
            logger.info(f"Using template: {template}")
            logger.info(f"Template kwargs: {kwargs}")
            
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
                msg.html = render_template(f'emails/{template}.html', **kwargs)
                logger.info("Email template rendered successfully")
            except Exception as template_error:
                logger.error(f"Error rendering email template: {str(template_error)}", exc_info=True)
                return False
            
            try:
                mail.send(msg)
                logger.info("Email sent successfully")
                return True
            except Exception as send_error:
                logger.error(f"Error sending email via SMTP: {str(send_error)}", exc_info=True)
                logger.error(f"Full error details: {send_error.__class__.__name__}: {str(send_error)}")
                return False
                
        except Exception as e:
            logger.error(f"Error in send_email: {str(e)}", exc_info=True)
            logger.error(f"Full error details: {e.__class__.__name__}: {str(e)}")
            return False
    
    @staticmethod
    def send_verification_email(user: User) -> bool:
        """Send verification email to user."""
        try:
            # Generate verification code
            user.generate_verification_code()
            
            # Create email message
            msg = Message(
                subject="Verify Your Email",
                recipients=[user.email],
                html=render_template(
                    'emails/verify_email.html',
                    user=user,
                    verification_code=user.verification_code
                )
            )
            
            # Log the attempt with configuration details
            logger.info(f"Attempting to send verification email to {user.email}")
            logger.info(f"Mail server config: {current_app.config['MAIL_SERVER']}:{current_app.config['MAIL_PORT']}")
            logger.info(f"Using TLS: {current_app.config['MAIL_USE_TLS']}")
            logger.info(f"Sender: {current_app.config['MAIL_DEFAULT_SENDER']}")
            
            # Send email
            mail.send(msg)
            logger.info(f"Verification email sent successfully to {user.email}")
            return True
            
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error while sending verification email: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Failed to send verification email: {str(e)}")
            return False
    
    @staticmethod
    def send_password_reset_email(email: str, token: str):
        """Send password reset email."""
        logger.info(f"Attempting to send password reset email to {email}")
        logger.info(f"Reset URL: {token}")
        result = EmailService.send_email(
            subject='Reset Your Password - Expiry Tracker',
            recipients=[email],
            template='reset_password',
            email=email,
            reset_url=token
        )
        logger.info(f"Password reset email send result: {result}")
        return result
    
    @staticmethod
    def send_daily_notification_email(user: User, items: List[Dict]):
        """Send daily notification email with items that need attention."""
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
        return EmailService.send_email(
            subject='Daily Expiry Alert Summary',
            recipients=[user.email],
            template='daily_notification',
            user=user,
            items=items_needing_attention
        )
    
    @staticmethod
    def send_expiry_notification(user: User, item_name: str, days_until_expiry: int):
        """Send expiry notification email."""
        return EmailService.send_email(
            subject=f'Expiry Alert: {item_name}',
            recipients=[user.email],
            template='expiry_notification',
            user=user,
            item_name=item_name,
            days_until_expiry=days_until_expiry
        )

    def send_password_reset_confirmation(self, email: str) -> bool:
        """Send confirmation email after password reset."""
        try:
            current_app.logger.info(f"Sending password reset confirmation email to {email}")
            
            msg = Message(
                'Password Reset Confirmation',
                sender=current_app.config['MAIL_DEFAULT_SENDER'],
                recipients=[email]
            )
            
            msg.html = render_template(
                'email/password_reset_confirmation.html',
                email=email
            )
            
            mail.send(msg)
            current_app.logger.info(f"Successfully sent password reset confirmation email to {email}")
            return True
            
        except Exception as e:
            current_app.logger.error(f"Error sending password reset confirmation email: {str(e)}")
            return False

    def __init__(self):
        self.mail = mail

    def send_verification_email(self, user):
        """Send verification email to user."""
        try:
            # Generate verification code
            user.generate_verification_code()
            
            # Create email message
            msg = Message(
                subject="Verify Your Email",
                recipients=[user.email],
                html=render_template(
                    'emails/verify_email.html',
                    user=user,
                    verification_code=user.verification_code
                )
            )
            
            # Log the attempt with configuration details
            logger.info(f"Attempting to send verification email to {user.email}")
            logger.info(f"Mail server config: {current_app.config['MAIL_SERVER']}:{current_app.config['MAIL_PORT']}")
            logger.info(f"Using TLS: {current_app.config['MAIL_USE_TLS']}")
            logger.info(f"Sender: {current_app.config['MAIL_DEFAULT_SENDER']}")
            
            # Send email
            self.mail.send(msg)
            logger.info(f"Verification email sent successfully to {user.email}")
            return True
            
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error while sending verification email: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Failed to send verification email: {str(e)}")
            return False 
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

@shared_task
def send_verification_email_task(user_email, otp_code):
    subject = 'Verify your Petso Account'
    message = f'Welcome to Petso! Your verification code is: {otp_code}'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [user_email]
    
    try:
        send_mail(subject, message, email_from, recipient_list)
        logger.info(f"Verification email sent to {user_email}")
    except Exception as e:
        logger.error(f"Failed to send verification email to {user_email}: {str(e)}")

@shared_task
def send_password_reset_email_task(user_email, reset_token):
    subject = 'Reset your Petso Password'
    message = f'Click the link to reset your password: {settings.FRONTEND_URL}/reset-password?token={reset_token}'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [user_email]
    
    try:
        send_mail(subject, message, email_from, recipient_list)
        logger.info(f"Password reset email sent to {user_email}")
    except Exception as e:
        logger.error(f"Failed to send password reset email to {user_email}: {str(e)}")

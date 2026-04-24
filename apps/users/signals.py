from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.utils import timezone
from apps.users.models import User, UserNotificationPreference, OTP
from apps.payments.models import Wallet
from apps.users.tasks import send_verification_email_task
import logging
import random
import string
from datetime import timedelta

logger = logging.getLogger(__name__)

def generate_otp_code(length=6):
    return ''.join(random.choices(string.digits, k=length))

@receiver(post_save, sender=User)
def create_dependencies_and_verify(sender, instance, created, **kwargs):
    if created:
        # Create Wallet
        Wallet.objects.create(user=instance)
        
        # Create Notification Preferences
        UserNotificationPreference.objects.create(user=instance)
        
        # Log activity
        from apps.users.models import UserActivityLog
        UserActivityLog.objects.create(
            user=instance,
            activity_type='registration',
            description=f'User {instance.email} registered.'
        )
        
        # Create OTP and send email if not verified (e.g., via social login)
        if not instance.is_verified:
            otp_code = generate_otp_code()
            OTP.objects.create(
                user=instance,
                code=otp_code,
                purpose='verification',
                expires_at=timezone.now() + timedelta(hours=24)
            )
            # Queue email via Celery (optional: no broker on serverless → do not fail registration)
            try:
                send_verification_email_task.delay(instance.email, otp_code)
                logger.info("OTP generated and Celery task queued for user: %s", instance.email)
            except Exception:
                logger.warning(
                    "Could not queue verification email for %s (broker/Celery unavailable?)",
                    instance.email,
                    exc_info=True,
                )
        
        logger.info(f"Created wallet and preferences for user: {instance.email}")

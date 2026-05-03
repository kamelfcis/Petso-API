import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.payments.models import Wallet
from apps.users.models import User, UserNotificationPreference

logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def create_user_dependencies(sender, instance, created, **kwargs):
    if not created:
        return
    Wallet.objects.create(user=instance)
    UserNotificationPreference.objects.create(user=instance)
    from apps.users.models import UserActivityLog

    UserActivityLog.objects.create(
        user=instance,
        activity_type="registration",
        description=f"User {instance.email} registered.",
    )
    logger.info("Created wallet and preferences for user: %s", instance.email)

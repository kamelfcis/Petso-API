from pathlib import Path

from django.apps import AppConfig
from django.conf import settings


class SocialConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.social"

    def ready(self):
        # Uploaded post images go under MEDIA_ROOT; ensure directory exists (VPS / fresh deploy).
        try:
            Path(settings.MEDIA_ROOT).mkdir(parents=True, exist_ok=True)
        except Exception:
            pass

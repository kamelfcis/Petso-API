import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = (
        "Create a Django admin superuser if it does not exist yet. "
        "Reads BOOTSTRAP_ADMIN_EMAIL, BOOTSTRAP_ADMIN_PASSWORD, optional BOOTSTRAP_ADMIN_NAME. "
        "Use once against your production DATABASE_URL (e.g. after vercel env pull)."
    )

    def handle(self, *args, **options):
        email = os.environ.get("BOOTSTRAP_ADMIN_EMAIL", "").strip()
        password = os.environ.get("BOOTSTRAP_ADMIN_PASSWORD", "")
        name = os.environ.get("BOOTSTRAP_ADMIN_NAME", "Admin").strip() or "Admin"

        if not email or not password:
            self.stdout.write(
                self.style.WARNING(
                    "Set BOOTSTRAP_ADMIN_EMAIL and BOOTSTRAP_ADMIN_PASSWORD, then run again."
                )
            )
            return

        User = get_user_model()
        if User.objects.filter(email=email).exists():
            self.stdout.write(self.style.WARNING(f"User already exists: {email} — nothing to do."))
            return

        User.objects.create_superuser(email=email, password=password, name=name)
        self.stdout.write(self.style.SUCCESS(f"Created superuser: {email}"))

"""Run on the server: python manage.py petso_check_vps"""

import os

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Check media directory and env when file uploads fail on VPS but work locally."

    def handle(self, *args, **options):
        root = settings.MEDIA_ROOT
        self.stdout.write(f"MEDIA_ROOT: {root}")
        if os.path.isdir(root):
            if os.access(root, os.W_OK):
                self.stdout.write(self.style.SUCCESS("MEDIA_ROOT is writable."))
            else:
                self.stdout.write(
                    self.style.ERROR(
                        "MEDIA_ROOT is NOT writable — fix ownership (e.g. chown www-data) or permissions."
                    )
                )
        else:
            self.stdout.write(
                self.style.WARNING("MEDIA_ROOT directory missing (apps.social creates it on startup).")
            )

        self.stdout.write(
            f"SERVE_MEDIA_FROM_DJANGO: {getattr(settings, 'SERVE_MEDIA_FROM_DJANGO', True)}"
        )
        pub = getattr(settings, "PETSO_PUBLIC_BASE_URL", "") or ""
        self.stdout.write(
            f"PETSO_PUBLIC_BASE_URL: {pub or '(unset - JSON media URLs use the request Host)'}"
        )
        mem = getattr(settings, "DATA_UPLOAD_MAX_MEMORY_SIZE", None)
        if mem is not None:
            mib = mem // (1024 * 1024)
            self.stdout.write(f"DATA_UPLOAD_MAX_MEMORY_SIZE: {mem} bytes (~{mib} MiB)")

        self.stdout.write("\nIf uploads work locally but not on VPS:")
        self.stdout.write("  - git pull && restart the app process")
        self.stdout.write("  - nginx: client_max_body_size >= 32m; see deployment/nginx-petso.sample.conf")
        self.stdout.write("  - .env: ALLOWED_HOSTS, PETSO_PUBLIC_BASE_URL, USE_X_FORWARDED_HOST (behind nginx)")
        self.stdout.write("  - Postman: {{base_url}} must be the VPS URL; image must be type File (no yellow warning)")

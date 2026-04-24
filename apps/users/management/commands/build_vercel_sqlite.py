"""Build deployment/petso.sqlite3 with migrations + demo admin (for bundling on Vercel)."""
import os
import subprocess
import sys
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = (
        "Create deployment/petso.sqlite3 (fresh) using settings_sqlite_bundle, then migrate + demo superuser. "
        "Commit deployment/petso.sqlite3 for Vercel. Default admin: admin@petso.local / PetsoVercel2026!"
    )

    def add_arguments(self, parser):
        parser.add_argument("--email", default="admin@petso.local")
        parser.add_argument("--password", default="PetsoVercel2026!")

    def handle(self, *args, **options):
        target = Path(settings.BASE_DIR) / "deployment" / "petso.sqlite3"
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            target.unlink()

        env = {**os.environ, "DJANGO_SETTINGS_MODULE": "petso_project.settings_sqlite_bundle"}
        manage = str(Path(settings.BASE_DIR) / "manage.py")

        self.stdout.write("Running migrate...")
        subprocess.check_call([sys.executable, manage, "migrate", "--noinput"], env=env)

        email = options["email"].strip()
        password = options["password"]
        env_super = {
            **env,
            "DJANGO_SUPERUSER_EMAIL": email,
            "DJANGO_SUPERUSER_PASSWORD": password,
            "DJANGO_SUPERUSER_NAME": "Admin",
        }
        self.stdout.write("Creating superuser...")
        subprocess.check_call(
            [sys.executable, manage, "createsuperuser", "--noinput"],
            env=env_super,
        )

        self.stdout.write(self.style.SUCCESS(f"Done: {target} (login {email})"))

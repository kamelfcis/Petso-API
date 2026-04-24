"""
Use only to build the bundled SQLite file for Vercel, e.g.:

    set DJANGO_SETTINGS_MODULE=petso_project.settings_sqlite_bundle
    python manage.py migrate --noinput
    python manage.py createsuperuser --noinput

Then commit deployment/petso.sqlite3 (see build_vercel_sqlite command).
"""
from .settings import *  # noqa: F403, F401

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": str(BASE_DIR / "deployment" / "petso.sqlite3"),
    },
}

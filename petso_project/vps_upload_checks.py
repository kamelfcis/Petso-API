"""Shared VPS / upload diagnostics (used by manage.py and root script)."""

import os

from django.conf import settings
from django.db.migrations.recorder import MigrationRecorder


def _social_post_image_column_ok():
    """Detect DB missing social.0003_post_image_field (causes: no column named image)."""
    try:
        return MigrationRecorder.Migration.objects.filter(
            app="social", name="0003_post_image_field"
        ).exists()
    except Exception:
        return None


def run_petso_vps_checks(stdout):
    root = settings.MEDIA_ROOT
    stdout.write(f"MEDIA_ROOT: {root}\n")
    if os.path.isdir(root):
        if os.access(root, os.W_OK):
            stdout.write("MEDIA_ROOT is writable.\n")
        else:
            stdout.write(
                "ERROR: MEDIA_ROOT is NOT writable - fix ownership (e.g. chown www-data) or permissions.\n"
            )
    else:
        stdout.write(
            "WARNING: MEDIA_ROOT directory missing (apps.social creates it on startup).\n"
        )

    mig_ok = _social_post_image_column_ok()
    if mig_ok is False:
        stdout.write(
            "ERROR: Migration social.0003_post_image_field is not applied.\n"
            "  Run: python manage.py migrate social\n"
            "  (Fixes: OperationalError: table social_post has no column named image)\n"
        )
    elif mig_ok is True:
        stdout.write("Database: social Post.image migration applied (0003_post_image_field).\n")

    stdout.write(
        f"SERVE_MEDIA_FROM_DJANGO: {getattr(settings, 'SERVE_MEDIA_FROM_DJANGO', True)}\n"
    )
    pub = getattr(settings, "PETSO_PUBLIC_BASE_URL", "") or ""
    stdout.write(
        f"PETSO_PUBLIC_BASE_URL: {pub or '(unset - JSON media URLs use the request Host)'}\n"
    )
    mem = getattr(settings, "DATA_UPLOAD_MAX_MEMORY_SIZE", None)
    if mem is not None:
        mib = mem // (1024 * 1024)
        stdout.write(f"DATA_UPLOAD_MAX_MEMORY_SIZE: {mem} bytes (~{mib} MiB)\n")

    stdout.write("\nIf uploads work locally but not on VPS:\n")
    stdout.write("  - git pull && restart the app process\n")
    stdout.write("  - python manage.py migrate   (required after pull if Post.image was added)\n")
    stdout.write("  - nginx: client_max_body_size >= 32m; see deployment/nginx-petso.sample.conf\n")
    stdout.write("  - .env: ALLOWED_HOSTS, PETSO_PUBLIC_BASE_URL, USE_X_FORWARDED_HOST (behind nginx)\n")
    stdout.write(
        "  - Postman: base_url must be the VPS URL; image must be type File (no yellow warning)\n"
    )

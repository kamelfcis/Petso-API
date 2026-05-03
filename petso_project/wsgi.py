"""
WSGI config for petso_project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os
import re
from pathlib import Path


def _assert_petso_deployment_matches_current_repo() -> None:
    """Fail fast if an old tree still ships Celery (otherwise Redis retry spam on signup)."""
    pkg = Path(__file__).resolve().parent
    if (pkg / "celery.py").exists():
        raise RuntimeError(
            "Stale deploy: petso_project/celery.py exists but this repo removed Celery. "
            "From project root: git pull origin main, delete petso_project/celery.py if it remains, "
            "pip uninstall -y celery, restart Waitress."
        )
    if (pkg.parent / "apps" / "users" / "tasks.py").exists():
        raise RuntimeError(
            "Stale deploy: apps/users/tasks.py exists (old Celery tasks). "
            "git pull origin main and remove that file if git did not delete it."
        )
    init = pkg / "__init__.py"
    if init.exists():
        txt = init.read_text(encoding="utf-8", errors="replace")
        if re.search(r"from\s+\.\s*celery\s+import", txt):
            raise RuntimeError(
                "Stale deploy: petso_project/__init__.py still imports Celery. "
                "Replace it with the empty __init__.py from latest main (git pull)."
            )


_assert_petso_deployment_matches_current_repo()

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "petso_project.settings")

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()

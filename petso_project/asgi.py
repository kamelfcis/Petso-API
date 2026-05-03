"""
ASGI config for petso_project.

DJANGO_SETTINGS_MODULE and django.setup() must run before any import that
loads Django models (e.g. apps.chat.routing → consumers → models).
Otherwise deployments like Vercel raise ImproperlyConfigured on AUTH_USER_MODEL.
"""
import os
import re
from pathlib import Path


def _assert_petso_deployment_matches_current_repo() -> None:
    pkg = Path(__file__).resolve().parent
    if (pkg / "celery.py").exists():
        raise RuntimeError(
            "Stale deploy: petso_project/celery.py exists but this repo removed Celery. "
            "git pull origin main, delete petso_project/celery.py if needed, pip uninstall -y celery."
        )
    if (pkg.parent / "apps" / "users" / "tasks.py").exists():
        raise RuntimeError(
            "Stale deploy: apps/users/tasks.py exists. git pull origin main and remove it if needed."
        )
    init = pkg / "__init__.py"
    if init.exists():
        txt = init.read_text(encoding="utf-8", errors="replace")
        if re.search(r"from\s+\.\s*celery\s+import", txt):
            raise RuntimeError(
                "Stale deploy: petso_project/__init__.py still imports Celery. git pull and fix __init__.py."
            )


_assert_petso_deployment_matches_current_repo()

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "petso_project.settings")

import django

django.setup()

from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

from apps.chat.routing import websocket_urlpatterns

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": AuthMiddlewareStack(URLRouter(websocket_urlpatterns)),
    }
)

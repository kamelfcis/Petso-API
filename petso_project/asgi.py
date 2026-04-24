"""
ASGI config for petso_project.

DJANGO_SETTINGS_MODULE and django.setup() must run before any import that
loads Django models (e.g. apps.chat.routing → consumers → models).
Otherwise deployments like Vercel raise ImproperlyConfigured on AUTH_USER_MODEL.
"""
import os

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

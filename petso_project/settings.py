import os
import tempfile
from pathlib import Path
from datetime import timedelta
import environ

# Initialize environ
env = environ.Env(
    DEBUG=(bool, False)
)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Vercel serverless: deploy filesystem is read-only except temp dir.
# VERCEL_ENV is always set on Vercel (production | preview | development); VERCEL=1 is also common.
IS_VERCEL = bool(os.environ.get('VERCEL_ENV')) or os.environ.get('VERCEL', '').lower() in ('1', 'true')

# Read .env file
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# Quick-start development settings - unsuitable for production
SECRET_KEY = env('SECRET_KEY', default='django-insecure-2p^rifo*lyfh=%p5q(r#w%3h61+cv@^z-c!q++b_8bl8p2tz^y')
DEBUG = env('DEBUG', default=True)

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['*'])

# Comma-separated, e.g. https://petso-api.vercel.app (needed for admin/forms behind HTTPS proxy)
_csrf_origins = env('CSRF_TRUSTED_ORIGINS', default='')
CSRF_TRUSTED_ORIGINS = [s.strip() for s in _csrf_origins.split(',') if s.strip()]

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Application definition
INSTALLED_APPS = [
    # Jazzmin must be before admin
    'jazzmin',
    
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_filters',
    'channels',
    'django_cleanup.apps.CleanupConfig',
    'drf_spectacular',
    
    # Internal apps
    'apps.users',
    'apps.farmers',
    'apps.vets',
    'apps.companies',
    'apps.ecommerce',
    'apps.orders',
    'apps.payments',
    'apps.ai',
    'apps.medical',
    'apps.social',
    'apps.chat',
    'apps.system',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'petso_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
                'apps.system.context_processors.dashboard_stats',
            ],
        },
    },
]

WSGI_APPLICATION = 'petso_project.wsgi.application'
ASGI_APPLICATION = 'petso_project.asgi.application'

# Database — one `default` connection for Django admin, REST API, and sessions.
# On Vercel without Postgres: bundled `deployment/petso.sqlite3` is copied to TMPDIR (writable).
_database_url = os.environ.get('DATABASE_URL', '').strip()
_bundled_sqlite = BASE_DIR / 'deployment' / 'petso.sqlite3'
_runtime_sqlite = Path(tempfile.gettempdir()) / 'petso.sqlite3'

if IS_VERCEL and _database_url and not _database_url.lower().startswith('sqlite'):
    DATABASES = {'default': env.db('DATABASE_URL')}
elif IS_VERCEL and _bundled_sqlite.is_file():
    import shutil

    shutil.copy2(_bundled_sqlite, _runtime_sqlite)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': str(_runtime_sqlite),
        },
    }
elif IS_VERCEL:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': str(_runtime_sqlite),
        },
    }
else:
    DATABASES = {
        'default': env.db('DATABASE_URL', default=f'sqlite:///{BASE_DIR}/db.sqlite3'),
    }

# Auth
AUTH_USER_MODEL = 'users.User'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# DRF
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# Swagger / Spectacular settings
SPECTACULAR_SETTINGS = {
    'TITLE': 'Petso SaaS API',
    'DESCRIPTION': 'Complete API documentation for the Petso Backend',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
        'persistAuthorization': True,
        'displayOperationId': True,
    },
}

# Simple JWT
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
}

# CORS
CORS_ALLOW_ALL_ORIGINS = True

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static & Media
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

MEDIA_URL = 'media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Email
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend' if DEBUG else 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env('EMAIL_HOST', default='')
EMAIL_PORT = env('EMAIL_PORT', default=587)
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')
EMAIL_USE_TLS = env('EMAIL_USE_TLS', default=True)

# Celery
CELERY_BROKER_URL = env('CELERY_BROKER_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = env('CELERY_BROKER_URL', default='redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
# Fail fast when broker is down (otherwise .delay() can stall the process for a long TCP timeout)
CELERY_BROKER_TRANSPORT_OPTIONS = {
    'socket_connect_timeout': int(os.environ.get('CELERY_SOCKET_CONNECT_TIMEOUT', '3')),
    'socket_timeout': int(os.environ.get('CELERY_SOCKET_TIMEOUT', '3')),
}

# Channels (Vercel without REDIS_URL: in-memory layer so HTTP ASGI boots; WebSockets won't scale across instances)
_redis_url = os.environ.get('REDIS_URL', '').strip()
if IS_VERCEL and not _redis_url:
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels.layers.InMemoryChannelLayer',
        },
    }
else:
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels_redis.core.RedisChannelLayer',
            'CONFIG': {
                'hosts': [_redis_url or env('REDIS_URL', default='redis://localhost:6379/1')],
            },
        },
    }

# Jazzmin settings
JAZZMIN_SETTINGS = {
    "site_title": "Petso Admin",
    "site_header": "Petso",
    "site_brand": "Petso Backend",
    "site_logo": "logo.png",
    "login_logo": "logo.png",
    "welcome_sign": "Welcome to Petso Admin Panel",
    "copyright": "Petso Ltd",
    "user_avatar": None,
    "topmenu_links": [
        {"name": "Home",  "url": "admin:index", "permissions": ["auth.view_user"]},
    ],
    "show_sidebar": True,
    "navigation_expanded": True,
    "order_with_respect_to": ["users", "farmers", "vets", "companies", "ecommerce", "orders", "payments", "ai", "medical", "social", "chat", "system"],
    "icons": {
        "users.User": "fas fa-users",
        "ecommerce.Product": "fas fa-shopping-cart",
        "orders.Order": "fas fa-box",
        "payments.Wallet": "fas fa-wallet",
        "ai.AICase": "fas fa-brain",
        "medical.Appointment": "fas fa-stethoscope",
        "social.Post": "fas fa-share-alt",
        "chat.Chat": "fas fa-comments",
        "system.Notification": "fas fa-bell",
    },
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",
    "related_modal_active": False,
    "custom_css": "admin/petso_admin.css",
    "custom_js": None,
    "show_ui_builder": False,
    "changeform_format": "horizontal_tabs",
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-light",
    "accent": "accent-primary",
    "navbar": "navbar-white navbar-light",
    "no_navbar_border": False,
    "navbar_fixed": False,
    "layout_fixed": False,
    "footer_fixed": False,
    "sidebar_fixed": False,
    "sidebar": "sidebar-light-primary",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": False,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "default",
}

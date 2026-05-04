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


def _load_dotenv(base: Path) -> None:
    """Load `.env` without django-environ 'Invalid line' noise on blank/whitespace-only rows."""
    path = base / '.env'
    if not path.is_file():
        return
    try:
        text = path.read_text(encoding='utf-8', errors='replace')
    except OSError:
        return
    lines = [ln for ln in text.splitlines(True) if ln.strip()]
    if not lines:
        return
    fd, tmp = tempfile.mkstemp(prefix='petso_', suffix='.env', text=True)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as wf:
            wf.writelines(lines)
        environ.Env.read_env(tmp, overwrite=False)
    finally:
        try:
            os.unlink(tmp)
        except OSError:
            pass


# Vercel serverless: deploy filesystem is read-only except temp dir.
# VERCEL_ENV is always set on Vercel (production | preview | development); VERCEL=1 is also common.
IS_VERCEL = bool(os.environ.get('VERCEL_ENV')) or os.environ.get('VERCEL', '').lower() in ('1', 'true')

# Read .env file (blank lines / whitespace-only lines are skipped)
_load_dotenv(BASE_DIR)

# Quick-start development settings - unsuitable for production
SECRET_KEY = env('SECRET_KEY', default='django-insecure-2p^rifo*lyfh=%p5q(r#w%3h61+cv@^z-c!q++b_8bl8p2tz^y')
DEBUG = env('DEBUG', default=True)

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['*'])
# Production: set in `.env`, e.g. ALLOWED_HOSTS=95.216.63.81,localhost,127.0.0.1 — see `.env.example` (VPS block).

# Comma-separated, e.g. https://petso-api.vercel.app (needed for admin/forms behind HTTPS proxy)
_csrf_origins = env('CSRF_TRUSTED_ORIGINS', default='')
CSRF_TRUSTED_ORIGINS = [s.strip() for s in _csrf_origins.split(',') if s.strip()]

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Behind nginx/Caddy: trust X-Forwarded-Host so absolute URLs (e.g. media in JSON) use the public host.
USE_X_FORWARDED_HOST = env.bool('USE_X_FORWARDED_HOST', default=not DEBUG)

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

# Simple JWT (SIGNING_KEY stretched so short SECRET_KEY does not trigger PyJWT InsecureKeyLengthWarning)
def _jwt_signing_key(secret: str) -> str:
    s = secret
    while len(s.encode('utf-8')) < 32:
        s += '!'
    return s


SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'SIGNING_KEY': _jwt_signing_key(SECRET_KEY),
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
# Serve uploaded files from Django (Waitress/VPS). Set False if nginx serves /media/.
SERVE_MEDIA_FROM_DJANGO = env.bool('SERVE_MEDIA_FROM_DJANGO', default=True)
# Optional: public API base URL without trailing slash (e.g. https://api.example.com). Forces correct
# image/image_url in JSON when the app sits behind a reverse proxy and Host headers differ.
PETSO_PUBLIC_BASE_URL = env('PETSO_PUBLIC_BASE_URL', default='').strip().rstrip('/')

# Multipart / file uploads (raise if nginx body limit is higher than this)
PETSO_MAX_UPLOAD_MB = max(int(env('PETSO_MAX_UPLOAD_MB', default='32') or 32), 3)
_max_upload_bytes = PETSO_MAX_UPLOAD_MB * 1024 * 1024
DATA_UPLOAD_MAX_MEMORY_SIZE = _max_upload_bytes
FILE_UPLOAD_MAX_MEMORY_SIZE = _max_upload_bytes

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Email
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend' if DEBUG else 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env('EMAIL_HOST', default='')
EMAIL_PORT = env('EMAIL_PORT', default=587)
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')
EMAIL_USE_TLS = env('EMAIL_USE_TLS', default=True)

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

# Optional: faster password hashing for demo / small VPS (signup does PBKDF2 on every register).
# Default Django PBKDF2 uses 720k iterations — can add seconds on a slow CPU.
# Set PETSO_FAST_PASSWORD_HASHING=1 only if you accept weaker hashing than production norms.
_fast_pw = os.environ.get("PETSO_FAST_PASSWORD_HASHING", "").strip().lower() in ("1", "true", "yes")
if _fast_pw:
    PASSWORD_HASHERS = [
        "petso_project.hashers.PetsoDemoPBKDF2PasswordHasher",
        "django.contrib.auth.hashers.PBKDF2PasswordHasher",
        "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
        "django.contrib.auth.hashers.Argon2PasswordHasher",
        "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
        "django.contrib.auth.hashers.ScryptPasswordHasher",
    ]


def _configure_sqlite_pragmas(sender, connection, **kwargs):
    if connection.vendor != "sqlite":
        return
    try:
        with connection.cursor() as cursor:
            cursor.execute("PRAGMA journal_mode=WAL;")
            cursor.execute("PRAGMA synchronous=NORMAL;")
            cursor.execute("PRAGMA busy_timeout=8000;")
    except Exception:
        pass


from django.db.backends.signals import connection_created  # noqa: E402

connection_created.connect(_configure_sqlite_pragmas)

"""
Django settings for ticketsystem project.
"""

from pathlib import Path
from datetime import timedelta
import os
from dotenv import load_dotenv
from celery.schedules import crontab

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# ─── Jazzmin Admin Theme ──────────────────────────────────────────────────────
JAZZMIN_SETTINGS = {
    # Title on the login screen and browser tab
    "site_title": "BrightPass Admin",
    "site_header": "BrightPass",
    "site_brand": "BrightPass",
    "site_logo": None,
    "login_logo": None,
    "site_icon": None,
    "welcome_sign": "Welcome to BrightPass Admin",
    "copyright": "BrightPass Ltd",

    # Top menu links
    "topmenu_links": [
        {"name": "Home", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "Site", "url": "/api/health/", "new_window": True},
    ],

    # User menu links (top right)
    "usermenu_links": [
        {"name": "Support", "url": "https://github.com/", "new_window": True},
    ],

    # Sidebar navigation
    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": [],
    "hide_models": [],

    # Custom icons for apps/models (Font Awesome 5 free)
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "accounts.user": "fas fa-user-circle",
        "accounts.userprofile": "fas fa-id-card",
        "events.event": "fas fa-calendar-alt",
        "events.category": "fas fa-tags",
        "events.venue": "fas fa-map-marker-alt",
        "events.tickettier": "fas fa-layer-group",
        "events.kplteam": "fas fa-shield-alt",
        "bookings.booking": "fas fa-ticket-alt",
        "bookings.ticket": "fas fa-qrcode",
        "payments.payment": "fas fa-money-bill-wave",
        "payments.refund": "fas fa-undo",
    },
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",

    # Sidebar ordering — controls which apps/models appear and in what order
    "order_with_respect_to": [
        "events",
        "events.event",
        "events.kplteam",
        "events.tickettier",
        "events.category",
        "events.venue",
        "bookings",
        "bookings.booking",
        "bookings.ticket",
        "payments",
        "payments.payment",
        "payments.refund",
        "accounts",
        "accounts.user",
        "accounts.userprofile",
        "auth",
    ],

    # UI tweaks
    "related_modal_active": True,
    "custom_css": None,
    "custom_js": None,
    "use_google_fonts_cdn": True,
    "show_ui_builder": False,
    "changeform_format": "horizontal_tabs",
    "changeform_format_overrides": {
        "auth.user": "collapsible",
        "auth.group": "vertical_tabs",
    },
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-success",
    "accent": "accent-teal",
    "navbar": "navbar-dark",
    "no_navbar_border": False,
    "navbar_fixed": True,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-dark-success",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "default",
    "default_theme_mode": "light",
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success",
    },
}
# ─────────────────────────────────────────────────────────────────────────────


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-uo1fxtelblki1n)=jrb!f$l%5&88va!6akmsq5cy6^m_u@!gk$"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# TheSportsDB API v1 — https://www.thesportsdb.com/documentation
THESPORTSDB_API_KEY = os.getenv("THESPORTSDB_API_KEY", "123")
# v2: header X-API-KEY — https://www.thesportsdb.com/api/v2/json (see Postman collection in repo root)
THESPORTSDB_V2_API_KEY = os.getenv("THESPORTSDB_V2_API_KEY", THESPORTSDB_API_KEY)
THESPORTSDB_V2_LEAGUE_ID = os.getenv("THESPORTSDB_V2_LEAGUE_ID", "4745")
THESPORTSDB_V2_SEASON = os.getenv("THESPORTSDB_V2_SEASON", "")

# Celery — use Redis for broker (see requirements.txt)
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://127.0.0.1:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", CELERY_BROKER_URL)

CELERY_BEAT_SCHEDULE = {
    "sync-kpl-thesportsdb-incremental": {
        "task": "events.tasks.sync_kpl_thesportsdb_incremental",
        "schedule": timedelta(hours=int(os.getenv("KPL_SYNC_INTERVAL_HOURS", "4"))),
    },
    "sync-kpl-thesportsdb-full": {
        "task": "events.tasks.sync_kpl_thesportsdb_full",
        "schedule": crontab(
            hour=int(os.getenv("KPL_FULL_SYNC_HOUR_UTC", "3")),
            minute=int(os.getenv("KPL_FULL_SYNC_MINUTE_UTC", "0")),
        ),
    },
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "ticketsystem-cache",
    }
}


# Application definition

INSTALLED_APPS = [
    "jazzmin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third party
    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",
    "django_filters",
    # Local apps
    "accounts",
    "events",
    "bookings",
    "payments",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # Serve static files
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "ticketsystem.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "ticketsystem" / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "ticketsystem.wsgi.application"


# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Custom User Model
AUTH_USER_MODEL = "accounts.User"

# REST Framework Configuration
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",  # Changed to AllowAny for public access
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
}

# JWT Settings
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# CORS Settings
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:56667",
    "http://localhost:56667",
]
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = True  # For development only

# M-Pesa Daraja API Configuration
MPESA_CONSUMER_KEY = os.getenv("MPESA_CONSUMER_KEY", "")
MPESA_CONSUMER_SECRET = os.getenv("MPESA_CONSUMER_SECRET", "")
MPESA_PASSKEY = os.getenv("MPESA_PASSKEY", "")
MPESA_SHORTCODE = os.getenv("MPESA_SHORTCODE", "")
MPESA_ENVIRONMENT = os.getenv("MPESA_ENVIRONMENT", "sandbox")  # sandbox or production
MPESA_CALLBACK_URL = os.getenv("MPESA_CALLBACK_URL", "http://127.0.0.1:8000/api/payments/mpesa/callback/")

# Media Files
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Africa/Nairobi"  # EAT = UTC+3

CELERY_TIMEZONE = TIME_ZONE

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

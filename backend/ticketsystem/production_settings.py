"""
Production settings for Django on Railway.
Override these in railway environment variables or use this file.
"""

from .settings import *

import os
import dj_database_url

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# SECURITY
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    raise ValueError('DJANGO_SECRET_KEY environment variable is required')

ALLOWED_HOSTS = [h.strip() for h in os.environ.get('ALLOWED_HOSTS', '').split(',') if h.strip()] or ['*']

# CORS settings for production
def _parse_origins(env_val, defaults):
    """Parse comma-separated origins, adding https:// if scheme is missing."""
    raw = [o.strip() for o in env_val.split(',') if o.strip()]
    if not raw:
        return defaults
    return [o if '://' in o else f'https://{o}' for o in raw]

CORS_ALLOWED_ORIGINS = _parse_origins(
    os.environ.get('CORS_ALLOWED_ORIGINS', ''),
    ['https://brightpassticket.web.app'],
)

CSRF_TRUSTED_ORIGINS = _parse_origins(
    os.environ.get('CSRF_TRUSTED_ORIGINS', ''),
    ['https://brightpassticket.web.app', 'https://backendticketsystem-production.up.railway.app'],
)

# Database - Railway provides DATABASE_URL
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL'),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# Static files - Using Whitenoise
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Email (optional - for production)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')

# Security settings
SECURE_SSL_REDIRECT = False  # Railway handles SSL termination at the proxy level
SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'True') == 'True'
CSRF_COOKIE_SECURE = os.environ.get('CSRF_COOKIE_SECURE', 'True') == 'True'

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'console-error': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
            'level': 'ERROR',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'console-error'],
            'level': os.environ.get('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': os.environ.get('DB_LOG_LEVEL', 'WARNING'),
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console', 'console-error'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['console', 'console-error'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
    'root': {
        'handlers': ['console', 'console-error'],
        'level': 'INFO',
    },
}

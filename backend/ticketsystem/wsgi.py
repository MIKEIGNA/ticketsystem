"""
WSGI config for ticketsystem project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# Use production settings if in Railway environment or DJANGO_SETTINGS_MODULE is set
if os.environ.get('RAILWAY_ENVIRONMENT') or os.environ.get('DJANGO_SETTINGS_MODULE'):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", os.environ.get('DJANGO_SETTINGS_MODULE', 'ticketsystem.production_settings'))
else:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ticketsystem.settings")

application = get_wsgi_application()

"""
Create a superuser if one doesn't exist.

Usage:
    python manage.py create_superuser_if_not_exists

Environment variables (optional):
    DJANGO_SUPERUSER_USERNAME - Default username (default: admin)
    DJANGO_SUPERUSER_EMAIL - Default email (default: admin@example.com)
    DJANGO_SUPERUSER_PASSWORD - Default password (default: admin123)
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.conf import settings
import os

User = get_user_model()


class Command(BaseCommand):
    help = 'Create a superuser if one does not already exist'

    def handle(self, *args, **options):
        # Check if superuser already exists
        if User.objects.filter(is_superuser=True).exists():
            count = User.objects.filter(is_superuser=True).count()
            self.stdout.write(
                self.style.SUCCESS(f'{count} superuser(s) already exist. Skipping creation.')
            )
            return

        # Get credentials from environment or use defaults
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin123')

        # Create superuser
        try:
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created superuser: {username} ({email})')
            )
            self.stdout.write(
                self.style.WARNING('Please change the default password after first login!')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Failed to create superuser: {e}')
            )

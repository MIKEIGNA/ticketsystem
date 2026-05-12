"""
Fix event slugs that contain characters not allowed in Django's <slug:> URL pattern.
Slugs must only contain [-a-zA-Z0-9_].

Usage:
    python manage.py fix_event_slugs
    python manage.py fix_event_slugs --dry-run
"""

import re
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from events.models import Event

SLUG_SAFE = re.compile(r'^[-a-zA-Z0-9_]+$')


class Command(BaseCommand):
    help = "Fix event slugs containing invalid URL characters"

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        fixed = 0

        for event in Event.objects.all():
            if SLUG_SAFE.match(event.slug):
                continue  # already valid

            # Re-slugify using the event title + date
            date_str = event.start_datetime.strftime("%Y-%m-%d")
            new_slug = slugify(f"{event.title}-{date_str}")[:200]

            # Ensure uniqueness
            if Event.objects.filter(slug=new_slug).exclude(pk=event.pk).exists():
                new_slug = f"{new_slug}-{str(event.pk)[:8]}"

            self.stdout.write(
                f"{'[DRY] ' if dry_run else ''}"
                f"Fix: '{event.slug}' → '{new_slug}'"
            )

            if not dry_run:
                event.slug = new_slug
                event.save(update_fields=["slug"])
                fixed += 1

        if dry_run:
            self.stdout.write(self.style.WARNING("Dry run — no changes saved."))
        else:
            self.stdout.write(self.style.SUCCESS(f"Fixed {fixed} slug(s)."))

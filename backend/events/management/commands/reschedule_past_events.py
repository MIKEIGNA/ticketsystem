"""
Reschedule past FKF/sports events to upcoming dates.

Finds all published sports events whose start_datetime is in the past
and moves them to the next upcoming weekend, preserving the time-of-day.

Usage:
    python manage.py reschedule_past_events
    python manage.py reschedule_past_events --dry-run
"""

from datetime import date, timedelta, datetime
from django.core.management.base import BaseCommand
from django.utils import timezone
from events.models import Event, Category


def _next_weekend_dates():
    """Return (saturday, sunday) for the next upcoming weekend."""
    today = date.today()
    days_until_saturday = (5 - today.weekday()) % 7
    if days_until_saturday == 0:
        days_until_saturday = 7
    saturday = today + timedelta(days=days_until_saturday)
    sunday = saturday + timedelta(days=1)
    return saturday, sunday


class Command(BaseCommand):
    help = "Reschedule past sports events to the next upcoming weekend"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Preview changes without saving",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        now = timezone.now()
        saturday, sunday = _next_weekend_dates()

        # Find past published sports events
        try:
            sports_cat = Category.objects.get(name="Sports")
        except Category.DoesNotExist:
            self.stdout.write(self.style.ERROR("Sports category not found"))
            return

        past_events = Event.objects.filter(
            category=sports_cat,
            status="published",
            start_datetime__lt=now,
        ).order_by("start_datetime")

        if not past_events.exists():
            self.stdout.write(self.style.SUCCESS("No past events to reschedule."))
            return

        self.stdout.write(f"Found {past_events.count()} past event(s) to reschedule")
        self.stdout.write(f"Next Saturday: {saturday}  |  Next Sunday: {sunday}")

        # Split roughly half to Saturday, half to Sunday
        events_list = list(past_events)
        mid = len(events_list) // 2

        updated = 0
        for i, event in enumerate(events_list):
            target_date = saturday if i < mid else sunday
            old_start = event.start_datetime
            old_time = old_start.time()

            # Build new datetime preserving the original time-of-day
            new_start = timezone.make_aware(
                datetime.combine(target_date, old_time)
            )
            new_end = new_start + timedelta(hours=2)

            # Update slug to reflect new date (avoid duplicate slug)
            old_slug = event.slug
            # Replace the date portion in the slug if it ends with a date
            import re
            new_date_str = target_date.strftime("%Y-%m-%d")
            new_slug = re.sub(r'\d{4}-\d{2}-\d{2}$', new_date_str, old_slug)
            if new_slug == old_slug:
                new_slug = f"{old_slug}-{new_date_str}"

            # Ensure slug uniqueness
            if Event.objects.filter(slug=new_slug).exclude(pk=event.pk).exists():
                new_slug = f"{new_slug}-{i}"

            self.stdout.write(
                f"  {'[DRY RUN] ' if dry_run else ''}"
                f"{event.title[:50]}: {old_start.date()} → {target_date}"
            )

            if not dry_run:
                event.start_datetime = new_start
                event.end_datetime = new_end
                event.slug = new_slug
                event.save(update_fields=["start_datetime", "end_datetime", "slug"])
                updated += 1

        if dry_run:
            self.stdout.write(self.style.WARNING(f"\nDry run — no changes saved. Would reschedule {len(events_list)} event(s)."))
        else:
            self.stdout.write(self.style.SUCCESS(f"\n✓ Rescheduled {updated} event(s) to next weekend."))

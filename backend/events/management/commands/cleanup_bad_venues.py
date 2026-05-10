"""
Clean up events with generic/bad venue names from TheSportsDB.

Usage:
    python manage.py cleanup_bad_venues --dry-run  # Preview changes
    python manage.py cleanup_bad_venues            # Apply changes
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from events.models import Event, Venue


BAD_VENUE_NAMES = [
    "kenyan premier league",
    "kenyan premier league stadium",
    "premier league stadium",
]


def is_bad_venue_name(name: str) -> bool:
    """Check if venue name is generic/bad."""
    if not name:
        return True
    name_lower = name.lower().strip()
    return any(bad in name_lower for bad in BAD_VENUE_NAMES)


class Command(BaseCommand):
    help = "Clean up events with generic venue names from TheSportsDB"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Preview changes without applying them",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        # Find all venues with bad names
        bad_venues = []
        for venue in Venue.objects.all():
            if is_bad_venue_name(venue.name):
                bad_venues.append(venue)

        if not bad_venues:
            self.stdout.write(self.style.SUCCESS("No bad venues found!"))
            return

        self.stdout.write(f"Found {len(bad_venues)} venue(s) with bad names:")
        for venue in bad_venues:
            self.stdout.write(f"  - {venue.name} (ID: {venue.id})")

        # Find events using these venues
        events_to_fix = Event.objects.filter(venue__in=bad_venues).select_related("venue")

        self.stdout.write(f"\nFound {events_to_fix.count()} event(s) to fix:")

        fixed_count = 0
        skipped_count = 0

        for event in events_to_fix:
            match_data = event.match_data or {}
            stadium_from_match = match_data.get("stadium", "")

            # Determine the correct venue name
            if stadium_from_match and not is_bad_venue_name(stadium_from_match):
                new_venue_name = stadium_from_match
                source = "match_data.stadium"
            else:
                new_venue_name = "Venue TBA"
                source = "default (no valid stadium found)"

            self.stdout.write(f"\n  Event: {event.title}")
            self.stdout.write(f"    Current venue: {event.venue.name}")
            self.stdout.write(f"    New venue: {new_venue_name} (from {source})")

            if dry_run:
                continue

            # Get or create the correct venue
            if new_venue_name != "Venue TBA":
                correct_venue, created = Venue.objects.get_or_create(
                    name=new_venue_name,
                    defaults={
                        "address": new_venue_name,
                        "city": event.venue.city if event.venue.city != "Unknown" else "Unknown",
                        "country": "Kenya",
                        "capacity": 10000,
                        "is_active": True,
                    },
                )
                if created:
                    self.stdout.write(f"    Created new venue: {new_venue_name}")
            else:
                # Use existing "Venue TBA" or create it
                correct_venue, created = Venue.objects.get_or_create(
                    name="Venue TBA",
                    defaults={
                        "address": "Venue TBA",
                        "city": "Unknown",
                        "country": "Kenya",
                        "capacity": 10000,
                        "is_active": True,
                    },
                )

            # Update event venue
            event.venue = correct_venue

            # Also update match_data.stadium if it was bad
            if is_bad_venue_name(stadium_from_match):
                match_data["stadium"] = ""
                event.match_data = match_data
                self.stdout.write(f"    Cleared bad stadium from match_data")

            event.save(update_fields=["venue", "match_data"] if is_bad_venue_name(stadium_from_match) else ["venue"])
            fixed_count += 1

        if dry_run:
            self.stdout.write(self.style.WARNING("\nDry run complete. No changes were made."))
            self.stdout.write("Run without --dry-run to apply changes.")
        else:
            self.stdout.write(self.style.SUCCESS(f"\nFixed {fixed_count} event(s)."))
            if skipped_count:
                self.stdout.write(self.style.WARNING(f"Skipped {skipped_count} event(s)."))

"""
Sync Kenyan Premier League fixtures from TheSportsDB API v2 into Event rows.

Examples:
    python manage.py sync_thesportsdb_kpl --mode incremental
    python manage.py sync_thesportsdb_kpl --mode full --season 2025-2026
    python manage.py sync_thesportsdb_kpl --organizer-id <uuid>

Requires THESPORTSDB_V2_API_KEY (or THESPORTSDB_API_KEY) with v2 access; see Postman collection.
"""

from django.core.management.base import BaseCommand

from events.v2_schedule_sync import sync_kpl_v2_schedule


class Command(BaseCommand):
    help = "Upsert KPL schedule from TheSportsDB v2 (full season or incremental next/previous batches)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--mode",
            choices=("full", "incremental"),
            default="incremental",
            help="full: /schedule/league/{id}/{season}; incremental: next+previous league batches",
        )
        parser.add_argument("--league-id", type=str, default=None, help="Override league id (default 4745)")
        parser.add_argument("--season", type=str, default=None, help="Season label e.g. 2025-2026 (full mode)")
        parser.add_argument("--organizer-id", type=str, default=None, help="Organizer user UUID")

    def handle(self, *args, **options):
        stats = sync_kpl_v2_schedule(
            options["mode"],
            league_id=options["league_id"],
            season=options["season"],
            organizer_id=options["organizer_id"],
            log=self.stdout.write,
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"Done: created={stats['created']} updated={stats['updated']} skipped={stats['skipped']}"
            )
        )

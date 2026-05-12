"""
Import FKF fixtures as sports events (KPL club badges from TheSportsDB league 4745).

Usage:
    python manage.py import_fkf_fixtures [--organizer-id <uuid>] [--clear-existing]
    python manage.py import_fkf_fixtures --refresh-logos
"""

from datetime import datetime, timedelta, date
from django.utils import timezone
from django.core.management.base import BaseCommand
from django.db import transaction
from events.models import Category, Venue, Event, TicketTier
from events.kpl_team_logos import get_team_assets, KPL_THESPORTSDB
from accounts.models import User


def _next_weekend_dates():
    """Return (saturday_str, sunday_str) for the next upcoming weekend."""
    today = date.today()
    days_until_saturday = (5 - today.weekday()) % 7
    if days_until_saturday == 0:
        days_until_saturday = 7  # already Saturday — use next one
    saturday = today + timedelta(days=days_until_saturday)
    sunday = saturday + timedelta(days=1)
    return saturday.strftime("%Y-%m-%d"), sunday.strftime("%Y-%m-%d")


# FKF League Branding
FKF_BRANDING = {
    "name": "FKF Premier League",
    "logo": "https://footballkenya.org/wp-content/uploads/2023/02/fkf-logo.png",
    "colors": {"red": "#DC3232", "black": "#000000", "green": "#43A047"},
}

TITLE_SPONSOR = {
    "name": "SportPesa",
    "logo": "https://www.sportpesa.co.ke/assets/images/sportpesa-logo.png",
    "colors": {"primary": "#0059B3", "white": "#FFFFFF"},
}

# Fixtures use "saturday"/"sunday" as day — resolved to real dates at import time
FKF_FIXTURES_TEMPLATE = [
    {
        "match_id": "FKF-2026-32-01",
        "home_team": "Murang'a SEAL",
        "away_team": "Kakamega Homeboyz",
        "day": "saturday",
        "time": "14:00",
        "stadium": "St. Sebastian Park",
        "category": "B",
        "base_price_regular": 200,
        "base_price_vip": 500,
    },
    {
        "match_id": "FKF-2026-32-02",
        "home_team": "KCB FC",
        "away_team": "Bandari FC",
        "day": "saturday",
        "time": "15:00",
        "stadium": "Police Sacco Stadium",
        "category": "B",
        "base_price_regular": 200,
        "base_price_vip": 500,
    },
    {
        "match_id": "FKF-2026-32-03",
        "home_team": "Gor Mahia",
        "away_team": "Kenya Police FC",
        "day": "saturday",
        "time": "16:15",
        "stadium": "Nyayo National Stadium",
        "category": "A",
        "base_price_regular": 300,
        "base_price_vip": 1000,
    },
    {
        "match_id": "FKF-2026-32-04",
        "home_team": "Shabana FC",
        "away_team": "Ulinzi Stars",
        "day": "saturday",
        "time": "14:00",
        "stadium": "Gusii Stadium",
        "category": "B",
        "base_price_regular": 200,
        "base_price_vip": 500,
    },
    {
        "match_id": "FKF-2026-32-05",
        "home_team": "AFC Leopards",
        "away_team": "Mara Sugar FC",
        "day": "saturday",
        "time": "16:15",
        "stadium": "Nyayo National Stadium",
        "category": "A",
        "base_price_regular": 300,
        "base_price_vip": 1000,
    },
    {
        "match_id": "FKF-2026-32-06",
        "home_team": "Mathare United",
        "away_team": "APS Bomet",
        "day": "sunday",
        "time": "13:00",
        "stadium": "Kasarani Annex",
        "category": "C",
        "base_price_regular": 100,
        "base_price_vip": 300,
    },
    {
        "match_id": "FKF-2026-32-07",
        "home_team": "Kariobangi Sharks",
        "away_team": "Nairobi United",
        "day": "sunday",
        "time": "14:00",
        "stadium": "Police Sacco Stadium",
        "category": "C",
        "base_price_regular": 100,
        "base_price_vip": 300,
    },
    {
        "match_id": "FKF-2026-32-08",
        "home_team": "Tusker FC",
        "away_team": "Bidco United",
        "day": "sunday",
        "time": "14:00",
        "stadium": "Kenyatta Stadium, Machakos",
        "category": "B",
        "base_price_regular": 200,
        "base_price_vip": 500,
    },
]

STADIUM_CITIES = {
    "St. Sebastian Park": "Murang'a",
    "Police Sacco Stadium": "Nairobi",
    "Nyayo National Stadium": "Nairobi",
    "Gusii Stadium": "Kisii",
    "Kasarani Annex": "Nairobi",
    "Kenyatta Stadium, Machakos": "Machakos",
}

STADIUM_CAPACITIES = {
    "Nyayo National Stadium": 30000,
    "Gusii Stadium": 15000,
    "St. Sebastian Park": 8000,
    "Police Sacco Stadium": 5000,
    "Kasarani Annex": 5000,
    "Kenyatta Stadium, Machakos": 10000,
}

CATEGORY_QUANTITIES = {
    "A": {"regular": 15000, "vip": 3000},
    "B": {"regular": 8000, "vip": 2000},
    "C": {"regular": 4000, "vip": 1000},
}


class Command(BaseCommand):
    help = "Import FKF fixtures as sports events"

    def add_arguments(self, parser):
        parser.add_argument("--organizer-id", type=str)
        parser.add_argument("--clear-existing", action="store_true")
        parser.add_argument("--refresh-logos", action="store_true")

    def handle(self, *args, **options):
        organizer_id = options["organizer_id"]
        clear_existing = options["clear_existing"]
        refresh_logos = options["refresh_logos"]

        sports_category, _ = Category.objects.get_or_create(
            name="Sports",
            defaults={
                "slug": "sports",
                "description": "Sports events including football matches, tournaments, and more",
                "icon": "trophy",
                "color": "#059669",
            },
        )

        organizer = self.get_organizer(organizer_id)
        if not organizer:
            self.stdout.write(self.style.ERROR("No organizer found."))
            return

        if refresh_logos:
            n = self.refresh_kpl_logos(sports_category)
            self.stdout.write(self.style.SUCCESS(f"Updated logos on {n} event(s)."))
            return

        if clear_existing:
            deleted_count, _ = Event.objects.filter(
                subtitle__icontains="FKF Premier League",
                category=sports_category,
            ).delete()
            self.stdout.write(f"Deleted {deleted_count} existing FKF events")

        # Resolve dynamic dates
        saturday, sunday = _next_weekend_dates()
        date_map = {"saturday": saturday, "sunday": sunday}

        created_count = 0
        with transaction.atomic():
            for template in FKF_FIXTURES_TEMPLATE:
                fixture = {**template, "date": date_map[template["day"]]}
                event = self.create_event(fixture, sports_category, organizer)
                if event:
                    self.create_ticket_tiers(event, fixture)
                    created_count += 1
                    self.stdout.write(f"Created: {event.title} on {fixture['date']}")

        self.stdout.write(self.style.SUCCESS(f"Imported {created_count} FKF fixtures!"))

    def refresh_kpl_logos(self, sports_category):
        qs = Event.objects.filter(category=sports_category, subtitle__icontains="FKF Premier League")
        updated = 0
        for event in qs:
            md = dict(event.match_data) if event.match_data else {}
            home, away = md.get("home_team"), md.get("away_team")
            if not home or not away:
                continue
            for side, logo_key, pri_key, sec_key in (
                (home, "home_team_logo", "home_team_primary_color", "home_team_secondary_color"),
                (away, "away_team_logo", "away_team_primary_color", "away_team_secondary_color"),
            ):
                assets = get_team_assets(side)
                if assets.get("logo"):
                    md[logo_key] = assets["logo"]
                if assets.get("primary_color"):
                    md[pri_key] = assets["primary_color"]
                if assets.get("secondary_color"):
                    md[sec_key] = assets["secondary_color"]
            branding = dict(md.get("branding") or {})
            branding.update({"fkf": FKF_BRANDING, "sponsor": TITLE_SPONSOR, "kpl": KPL_THESPORTSDB})
            md["branding"] = branding
            event.match_data = md
            event.save(update_fields=["match_data"])
            updated += 1
        return updated

    def get_organizer(self, organizer_id):
        if organizer_id:
            try:
                return User.objects.get(id=organizer_id)
            except User.DoesNotExist:
                pass
        return User.objects.filter(is_superuser=True).first()

    def get_or_create_venue(self, stadium_name):
        venue, created = Venue.objects.get_or_create(
            name=stadium_name,
            defaults={
                "address": stadium_name,
                "city": STADIUM_CITIES.get(stadium_name, "Unknown"),
                "country": "Kenya",
                "capacity": STADIUM_CAPACITIES.get(stadium_name, 5000),
                "is_active": True,
            },
        )
        if created:
            self.stdout.write(f"  Created venue: {venue.name}")
        return venue

    def create_event(self, fixture, category, organizer):
        home_team = fixture["home_team"]
        away_team = fixture["away_team"]
        title = f"{home_team} vs {away_team}"
        slug = (
            f"{home_team.lower().replace(' ', '-').replace(chr(39), '')}"
            f"-vs-{away_team.lower().replace(' ', '-')}"
            f"-{fixture['date']}"
        )

        if Event.objects.filter(slug=slug).exists():
            self.stdout.write(f"  Already exists: {title}")
            return None

        venue = self.get_or_create_venue(fixture["stadium"])
        start_datetime = timezone.make_aware(
            datetime.strptime(f"{fixture['date']} {fixture['time']}", "%Y-%m-%d %H:%M")
        )
        end_datetime = start_datetime + timedelta(hours=2)
        home_assets = get_team_assets(home_team)
        away_assets = get_team_assets(away_team)

        return Event.objects.create(
            title=title,
            slug=slug,
            subtitle=f"FKF Premier League — {fixture['category']} Category",
            description=self._description(fixture),
            category=category,
            venue=venue,
            organizer=organizer,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            doors_open=(start_datetime - timedelta(minutes=30)).time(),
            age_restriction="All Ages",
            status="published",
            is_public=True,
            featured=fixture["category"] == "A",
            tags=["football", "FKF", "premier league", "sports", "kenya"],
            match_data={
                "match_id": fixture["match_id"],
                "home_team": home_team,
                "away_team": away_team,
                "home_team_logo": home_assets.get("logo", ""),
                "away_team_logo": away_assets.get("logo", ""),
                "home_team_primary_color": home_assets.get("primary_color", "#000000"),
                "home_team_secondary_color": home_assets.get("secondary_color", "#FFFFFF"),
                "away_team_primary_color": away_assets.get("primary_color", "#000000"),
                "away_team_secondary_color": away_assets.get("secondary_color", "#FFFFFF"),
                "category": fixture["category"],
                "stadium": fixture["stadium"],
                "branding": {"fkf": FKF_BRANDING, "sponsor": TITLE_SPONSOR, "kpl": KPL_THESPORTSDB},
            },
        )

    def _description(self, fixture):
        info = {"A": "Top-tier match", "B": "Exciting mid-table clash", "C": "Promising match"}
        return (
            f"<h2>FKF Premier League</h2>"
            f"<p><strong>{fixture['home_team']}</strong> vs <strong>{fixture['away_team']}</strong></p>"
            f"<p>{info.get(fixture['category'], 'League match')} at {fixture['stadium']}.</p>"
            f"<p><strong>Date:</strong> {fixture['date']} | <strong>Time:</strong> {fixture['time']} EAT</p>"
        )

    def create_ticket_tiers(self, event, fixture):
        quantities = CATEGORY_QUANTITIES.get(fixture["category"], {"regular": 5000, "vip": 1000})
        for name, price_key, order, benefits in (
            ("Regular", "base_price_regular", 1, ["Standard seating", "Access to match viewing"]),
            ("VIP", "base_price_vip", 0, ["Premium seating", "Priority entry", "VIP section access"]),
        ):
            TicketTier.objects.get_or_create(
                event=event,
                name=name,
                defaults={
                    "price": fixture[price_key],
                    "currency": "KES",
                    "total_quantity": quantities["regular" if name == "Regular" else "vip"],
                    "available_quantity": quantities["regular" if name == "Regular" else "vip"],
                    "min_per_order": 1,
                    "max_per_order": 10,
                    "is_active": True,
                    "order": order,
                    "benefits": benefits,
                },
            )

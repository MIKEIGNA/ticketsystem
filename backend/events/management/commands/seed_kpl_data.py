"""
Seed KPL teams and Kenyan football stadiums into the database.

Usage:
    python manage.py seed_kpl_data
    python manage.py seed_kpl_data --update   # overwrite existing records
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from events.models import KPLTeam, Venue

# ── KPL Teams ─────────────────────────────────────────────────────────────────
KPL_TEAMS = [
    {
        "name": "AFC Leopards",
        "short_name": "AFC",
        "logo_url": "https://r2.thesportsdb.com/images/media/team/badge/4taj3p1583767536.png",
        "primary_color": "#0000FF",
        "secondary_color": "#FFFFFF",
        "home_stadium": "Nyayo National Stadium",
        "city": "Nairobi",
        "founded": 1958,
        "thesportsdb_id": "134196",
    },
    {
        "name": "APS Bomet",
        "short_name": "APS",
        "logo_url": "https://r2.thesportsdb.com/images/media/team/badge/480ss31660940507.png",
        "primary_color": "#DC3232",
        "secondary_color": "#FFFFFF",
        "home_stadium": "Bomet Green Stadium",
        "city": "Bomet",
        "founded": 2010,
        "thesportsdb_id": "",
    },
    {
        "name": "Bandari FC",
        "short_name": "BAN",
        "logo_url": "https://r2.thesportsdb.com/images/media/team/badge/j0k5hr1583767461.png",
        "primary_color": "#004A99",
        "secondary_color": "#FDB913",
        "home_stadium": "Mbaraki Sports Ground",
        "city": "Mombasa",
        "founded": 1991,
        "thesportsdb_id": "134197",
    },
    {
        "name": "Bidco United",
        "short_name": "BID",
        "logo_url": "https://r2.thesportsdb.com/images/media/team/badge/7kovoy1616161037.png",
        "primary_color": "#43A047",
        "secondary_color": "#FFFFFF",
        "home_stadium": "Thika Stadium",
        "city": "Thika",
        "founded": 2016,
        "thesportsdb_id": "",
    },
    {
        "name": "Gor Mahia",
        "short_name": "GOR",
        "logo_url": "https://r2.thesportsdb.com/images/media/team/badge/8hqogn1583765598.png",
        "primary_color": "#008000",
        "secondary_color": "#FFFFFF",
        "home_stadium": "Nyayo National Stadium",
        "city": "Nairobi",
        "founded": 1968,
        "thesportsdb_id": "134198",
    },
    {
        "name": "Kakamega Homeboyz",
        "short_name": "KHB",
        "logo_url": "https://r2.thesportsdb.com/images/media/team/badge/jk0iy41583764938.png",
        "primary_color": "#0059B3",
        "secondary_color": "#FFFFFF",
        "home_stadium": "Bukhungu Stadium",
        "city": "Kakamega",
        "founded": 1980,
        "thesportsdb_id": "134199",
    },
    {
        "name": "Kariobangi Sharks",
        "short_name": "KSH",
        "logo_url": "https://r2.thesportsdb.com/images/media/team/badge/3byxk61583357154.png",
        "primary_color": "#43A047",
        "secondary_color": "#000000",
        "home_stadium": "Kasarani Annex",
        "city": "Nairobi",
        "founded": 2010,
        "thesportsdb_id": "134200",
    },
    {
        "name": "KCB FC",
        "short_name": "KCB",
        "logo_url": "https://r2.thesportsdb.com/images/media/team/badge/ewpyvl1583765049.png",
        "primary_color": "#006837",
        "secondary_color": "#FFD700",
        "home_stadium": "Police Sacco Stadium",
        "city": "Nairobi",
        "founded": 1970,
        "thesportsdb_id": "134201",
    },
    {
        "name": "Kenya Police FC",
        "short_name": "KPF",
        "logo_url": "https://r2.thesportsdb.com/images/media/team/badge/8rc7kn1776296960.png",
        "primary_color": "#CE1126",
        "secondary_color": "#0033A0",
        "home_stadium": "Police Sacco Stadium",
        "city": "Nairobi",
        "founded": 1953,
        "thesportsdb_id": "",
    },
    {
        "name": "Mara Sugar FC",
        "short_name": "MSU",
        "logo_url": "https://r2.thesportsdb.com/images/media/team/badge/xycge61726169941.png",
        "primary_color": "#43A047",
        "secondary_color": "#FFFFFF",
        "home_stadium": "Awendo Green Stadium",
        "city": "Awendo",
        "founded": 2005,
        "thesportsdb_id": "",
    },
    {
        "name": "Mathare United",
        "short_name": "MAT",
        "logo_url": "https://r2.thesportsdb.com/images/media/team/badge/yj43x31583407667.png",
        "primary_color": "#DC3232",
        "secondary_color": "#000000",
        "home_stadium": "Kasarani Annex",
        "city": "Nairobi",
        "founded": 1994,
        "thesportsdb_id": "134202",
    },
    {
        "name": "Murang'a SEAL",
        "short_name": "MUR",
        "logo_url": "https://r2.thesportsdb.com/images/media/team/badge/yb7j381689947933.png",
        "primary_color": "#DC3232",
        "secondary_color": "#FFFFFF",
        "home_stadium": "St. Sebastian Park",
        "city": "Murang'a",
        "founded": 2015,
        "thesportsdb_id": "",
    },
    {
        "name": "Nairobi United",
        "short_name": "NAU",
        "logo_url": "https://r2.thesportsdb.com/images/media/team/badge/c22eja1759163430.png",
        "primary_color": "#0059B3",
        "secondary_color": "#FFFFFF",
        "home_stadium": "Kasarani Annex",
        "city": "Nairobi",
        "founded": 2018,
        "thesportsdb_id": "",
    },
    {
        "name": "Nzoia Sugar",
        "short_name": "NZO",
        "logo_url": "https://r2.thesportsdb.com/images/media/team/badge/fi78rj1583407331.png",
        "primary_color": "#0059B3",
        "secondary_color": "#FFFFFF",
        "home_stadium": "Sudi Stadium",
        "city": "Bungoma",
        "founded": 1978,
        "thesportsdb_id": "134203",
    },
    {
        "name": "Posta Rangers",
        "short_name": "POS",
        "logo_url": "https://r2.thesportsdb.com/images/media/team/badge/w8uos81583407110.png",
        "primary_color": "#E31E24",
        "secondary_color": "#FFFFFF",
        "home_stadium": "Jamhuri Park",
        "city": "Nairobi",
        "founded": 1925,
        "thesportsdb_id": "134204",
    },
    {
        "name": "Shabana FC",
        "short_name": "SHA",
        "logo_url": "https://r2.thesportsdb.com/images/media/team/badge/bnu4ha1689948335.png",
        "primary_color": "#FF0000",
        "secondary_color": "#FFFFFF",
        "home_stadium": "Gusii Stadium",
        "city": "Kisii",
        "founded": 1968,
        "thesportsdb_id": "",
    },
    {
        "name": "Sofapaka FC",
        "short_name": "SOF",
        "logo_url": "https://r2.thesportsdb.com/images/media/team/badge/p7qrgw1583406664.png",
        "primary_color": "#0059B3",
        "secondary_color": "#FFFFFF",
        "home_stadium": "Kenyatta Stadium, Machakos",
        "city": "Nairobi",
        "founded": 2004,
        "thesportsdb_id": "134205",
    },
    {
        "name": "Tusker FC",
        "short_name": "TUS",
        "logo_url": "https://r2.thesportsdb.com/images/media/team/badge/9rnoc81583406233.png",
        "primary_color": "#FFFF00",
        "secondary_color": "#000000",
        "home_stadium": "Ruaraka Grounds",
        "city": "Nairobi",
        "founded": 1969,
        "thesportsdb_id": "134206",
    },
    {
        "name": "Ulinzi Stars",
        "short_name": "ULI",
        "logo_url": "https://r2.thesportsdb.com/images/media/team/badge/5hzcu31583357971.png",
        "primary_color": "#ED1C24",
        "secondary_color": "#FFFFFF",
        "home_stadium": "Afraha Stadium",
        "city": "Nakuru",
        "founded": 1998,
        "thesportsdb_id": "134207",
    },
]

# ── Kenyan Football Stadiums ──────────────────────────────────────────────────
KPL_STADIUMS = [
    {
        "name": "Nyayo National Stadium",
        "address": "Langata Road, Nairobi",
        "city": "Nairobi",
        "capacity": 30000,
        "description": "Kenya's premier national stadium, home to AFC Leopards and Gor Mahia big matches.",
        "latitude": -1.3031,
        "longitude": 36.8219,
    },
    {
        "name": "Kasarani Stadium",
        "address": "Thika Road, Kasarani, Nairobi",
        "city": "Nairobi",
        "capacity": 60000,
        "description": "Moi International Sports Centre Kasarani — Kenya's largest stadium.",
        "latitude": -1.2219,
        "longitude": 36.8956,
    },
    {
        "name": "Kasarani Annex",
        "address": "Thika Road, Kasarani, Nairobi",
        "city": "Nairobi",
        "capacity": 5000,
        "description": "Training and match annex at Kasarani, used by Kariobangi Sharks and Mathare United.",
        "latitude": -1.2219,
        "longitude": 36.8956,
    },
    {
        "name": "Police Sacco Stadium",
        "address": "Ruaraka, Nairobi",
        "city": "Nairobi",
        "capacity": 5000,
        "description": "Home ground for KCB FC and Kenya Police FC.",
        "latitude": -1.2333,
        "longitude": 36.8833,
    },
    {
        "name": "Jamhuri Park",
        "address": "Ngong Road, Nairobi",
        "city": "Nairobi",
        "capacity": 3000,
        "description": "Home of Posta Rangers FC.",
        "latitude": -1.3000,
        "longitude": 36.7833,
    },
    {
        "name": "Ruaraka Grounds",
        "address": "Ruaraka, Nairobi",
        "city": "Nairobi",
        "capacity": 3000,
        "description": "Home ground of Tusker FC.",
        "latitude": -1.2333,
        "longitude": 36.8833,
    },
    {
        "name": "Bukhungu Stadium",
        "address": "Kakamega Town",
        "city": "Kakamega",
        "capacity": 15000,
        "description": "Home of Kakamega Homeboyz. Western Kenya's main football venue.",
        "latitude": 0.2827,
        "longitude": 34.7519,
    },
    {
        "name": "Gusii Stadium",
        "address": "Kisii Town",
        "city": "Kisii",
        "capacity": 15000,
        "description": "Home of Shabana FC. Main stadium in Kisii County.",
        "latitude": -0.6817,
        "longitude": 34.7667,
    },
    {
        "name": "Mbaraki Sports Ground",
        "address": "Mbaraki, Mombasa",
        "city": "Mombasa",
        "capacity": 8000,
        "description": "Home of Bandari FC on the Kenyan coast.",
        "latitude": -4.0435,
        "longitude": 39.6682,
    },
    {
        "name": "Kenyatta Stadium, Machakos",
        "address": "Machakos Town",
        "city": "Machakos",
        "capacity": 10000,
        "description": "Main stadium in Machakos County.",
        "latitude": -1.5177,
        "longitude": 37.2634,
    },
    {
        "name": "Afraha Stadium",
        "address": "Nakuru Town",
        "city": "Nakuru",
        "capacity": 10000,
        "description": "Home of Ulinzi Stars. Main stadium in Nakuru County.",
        "latitude": -0.2833,
        "longitude": 36.0667,
    },
    {
        "name": "Sudi Stadium",
        "address": "Bungoma Town",
        "city": "Bungoma",
        "capacity": 8000,
        "description": "Home of Nzoia Sugar FC.",
        "latitude": 0.5635,
        "longitude": 34.5606,
    },
    {
        "name": "St. Sebastian Park",
        "address": "Murang'a Town",
        "city": "Murang'a",
        "capacity": 8000,
        "description": "Home of Murang'a SEAL FC.",
        "latitude": -0.7167,
        "longitude": 37.1500,
    },
    {
        "name": "Thika Stadium",
        "address": "Thika Town",
        "city": "Thika",
        "capacity": 8000,
        "description": "Main stadium in Thika, used by Bidco United.",
        "latitude": -1.0332,
        "longitude": 37.0693,
    },
    {
        "name": "Awendo Green Stadium",
        "address": "Awendo Town",
        "city": "Awendo",
        "capacity": 5000,
        "description": "Home of Mara Sugar FC in Migori County.",
        "latitude": -0.6333,
        "longitude": 34.4667,
    },
    {
        "name": "Bomet Green Stadium",
        "address": "Bomet Town",
        "city": "Bomet",
        "capacity": 5000,
        "description": "Home of APS Bomet FC.",
        "latitude": -0.7833,
        "longitude": 35.3500,
    },
    {
        "name": "Kipchoge Keino Stadium",
        "address": "Eldoret Town",
        "city": "Eldoret",
        "capacity": 15000,
        "description": "Main stadium in Eldoret, Uasin Gishu County.",
        "latitude": 0.5167,
        "longitude": 35.2833,
    },
    {
        "name": "Moi Stadium, Kisumu",
        "address": "Kisumu Town",
        "city": "Kisumu",
        "capacity": 20000,
        "description": "Main stadium in Kisumu, western Kenya.",
        "latitude": -0.1022,
        "longitude": 34.7617,
    },
    {
        "name": "Mombasa Municipal Stadium",
        "address": "Mombasa Island",
        "city": "Mombasa",
        "capacity": 10000,
        "description": "Alternative venue in Mombasa for coastal football.",
        "latitude": -4.0500,
        "longitude": 39.6667,
    },
]


class Command(BaseCommand):
    help = "Seed KPL teams and Kenyan football stadiums into the database"

    def add_arguments(self, parser):
        parser.add_argument(
            "--update",
            action="store_true",
            help="Update existing records with latest data",
        )

    def handle(self, *args, **options):
        update = options["update"]

        with transaction.atomic():
            self._seed_teams(update)
            self._seed_stadiums(update)

        self.stdout.write(self.style.SUCCESS("✓ KPL seed data loaded successfully!"))

    def _seed_teams(self, update: bool):
        created = updated = skipped = 0
        for data in KPL_TEAMS:
            team, was_created = KPLTeam.objects.get_or_create(
                name=data["name"],
                defaults=data,
            )
            if was_created:
                created += 1
                self.stdout.write(f"  + Team: {team.name}")
            elif update:
                for field, value in data.items():
                    setattr(team, field, value)
                team.save()
                updated += 1
                self.stdout.write(f"  ~ Team updated: {team.name}")
            else:
                skipped += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Teams — created: {created}, updated: {updated}, skipped: {skipped}"
            )
        )

    def _seed_stadiums(self, update: bool):
        created = updated = skipped = 0
        for data in KPL_STADIUMS:
            venue, was_created = Venue.objects.get_or_create(
                name=data["name"],
                defaults={**data, "country": "Kenya", "is_active": True},
            )
            if was_created:
                created += 1
                self.stdout.write(f"  + Stadium: {venue.name}")
            elif update:
                for field, value in data.items():
                    setattr(venue, field, value)
                venue.save()
                updated += 1
                self.stdout.write(f"  ~ Stadium updated: {venue.name}")
            else:
                skipped += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Stadiums — created: {created}, updated: {updated}, skipped: {skipped}"
            )
        )

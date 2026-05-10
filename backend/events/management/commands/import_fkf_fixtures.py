"""
Import FKF fixtures as sports events (KPL club badges from TheSportsDB league 4745).

Usage:
    python manage.py import_fkf_fixtures [--organizer-id <uuid>] [--clear-existing]
    python manage.py import_fkf_fixtures --refresh-logos
"""

from datetime import datetime, timedelta
from django.utils import timezone
from django.core.management.base import BaseCommand
from django.db import transaction
from events.models import Category, Venue, Event, TicketTier
from events.kpl_team_logos import get_team_assets, KPL_THESPORTSDB
from accounts.models import User


# FKF League Branding
FKF_BRANDING = {
    "name": "FKF Premier League",
    "logo": "https://footballkenya.org/wp-content/uploads/2023/02/fkf-logo.png",
    "colors": {
        "red": "#DC3232",
        "black": "#000000",
        "green": "#43A047",
    },
}

# Title Sponsor
TITLE_SPONSOR = {
    "name": "SportPesa",
    "logo": "https://www.sportpesa.co.ke/assets/images/sportpesa-logo.png",
    "colors": {
        "primary": "#0059B3",
        "white": "#FFFFFF"
    }
}

FKF_FIXTURES = [
    {
        "match_id": "FKF-2026-32-01",
        "home_team": "Murang'a SEAL",
        "away_team": "Kakamega Homeboyz",
        "date": "2026-05-09",
        "time": "14:00",
        "stadium": "St. Sebastian Park",
        "category": "B",
        "base_price_regular": 200,
        "base_price_vip": 500
    },
    {
        "match_id": "FKF-2026-32-02",
        "home_team": "KCB FC",
        "away_team": "Bandari FC",
        "date": "2026-05-09",
        "time": "15:00",
        "stadium": "Police Sacco Stadium",
        "category": "B",
        "base_price_regular": 200,
        "base_price_vip": 500
    },
    {
        "match_id": "FKF-2026-32-03",
        "home_team": "Gor Mahia",
        "away_team": "Kenya Police FC",
        "date": "2026-05-09",
        "time": "16:15",
        "stadium": "Nyayo National Stadium",
        "category": "A",
        "base_price_regular": 300,
        "base_price_vip": 1000
    },
    {
        "match_id": "FKF-2026-32-04",
        "home_team": "Shabana FC",
        "away_team": "Ulinzi Stars",
        "date": "2026-05-09",
        "time": "14:00",
        "stadium": "Gusii Stadium",
        "category": "B",
        "base_price_regular": 200,
        "base_price_vip": 500
    },
    {
        "match_id": "FKF-2026-32-05",
        "home_team": "AFC Leopards",
        "away_team": "Mara Sugar FC",
        "date": "2026-05-09",
        "time": "16:15",
        "stadium": "Nyayo National Stadium",
        "category": "A",
        "base_price_regular": 300,
        "base_price_vip": 1000
    },
    {
        "match_id": "FKF-2026-32-06",
        "home_team": "Mathare United",
        "away_team": "APS Bomet",
        "date": "2026-05-10",
        "time": "13:00",
        "stadium": "Kasarani Annex",
        "category": "C",
        "base_price_regular": 100,
        "base_price_vip": 300
    },
    {
        "match_id": "FKF-2026-32-07",
        "home_team": "Kariobangi Sharks",
        "away_team": "Nairobi United",
        "date": "2026-05-10",
        "time": "14:00",
        "stadium": "Police Sacco Stadium",
        "category": "C",
        "base_price_regular": 100,
        "base_price_vip": 300
    },
    {
        "match_id": "FKF-2026-32-08",
        "home_team": "Tusker FC",
        "away_team": "Bidco United",
        "date": "2026-05-10",
        "time": "14:00",
        "stadium": "Kenyatta Stadium, Machakos",
        "category": "B",
        "base_price_regular": 200,
        "base_price_vip": 500
    }
]

# Stadium mapping to city
STADIUM_CITIES = {
    "St. Sebastian Park": "Murang'a",
    "Police Sacco Stadium": "Nairobi",
    "Nyayo National Stadium": "Nairobi",
    "Gusii Stadium": "Kisii",
    "Kasarani Annex": "Nairobi",
    "Kenyatta Stadium, Machakos": "Machakos",
}

# Default capacities for stadiums
STADIUM_CAPACITIES = {
    "Nyayo National Stadium": 30000,
    "Gusii Stadium": 15000,
    "St. Sebastian Park": 8000,
    "Police Sacco Stadium": 5000,
    "Kasarani Annex": 5000,
    "Kenyatta Stadium, Machakos": 10000,
}

# Ticket quantities based on match category
CATEGORY_QUANTITIES = {
    "A": {"regular": 15000, "vip": 3000},
    "B": {"regular": 8000, "vip": 2000},
    "C": {"regular": 4000, "vip": 1000},
}


class Command(BaseCommand):
    help = 'Import FKF fixtures as sports events'

    def add_arguments(self, parser):
        parser.add_argument(
            '--organizer-id',
            type=str,
            help='UUID of the user to set as event organizer (defaults to first superuser)'
        )
        parser.add_argument(
            '--clear-existing',
            action='store_true',
            help='Delete existing FKF Premier League events before importing'
        )
        parser.add_argument(
            '--refresh-logos',
            action='store_true',
            help='Update match_data team badges from TheSportsDB KPL for existing imports, then exit'
        )

    def handle(self, *args, **options):
        organizer_id = options['organizer_id']
        clear_existing = options['clear_existing']
        refresh_logos = options['refresh_logos']
        
        # Get or create Sports category
        sports_category, _ = Category.objects.get_or_create(
            name='Sports',
            defaults={
                'slug': 'sports',
                'description': 'Sports events including football matches, tournaments, and more',
                'icon': 'trophy',
                'color': '#059669',
            }
        )
        self.stdout.write(f"Using category: {sports_category.name}")
        
        # Get organizer
        organizer = self.get_organizer(organizer_id)
        if not organizer:
            self.stdout.write(
                self.style.ERROR('No organizer found. Please create a superuser or provide --organizer-id')
            )
            return
        self.stdout.write(f"Using organizer: {organizer.email}")

        if refresh_logos:
            n = self.refresh_kpl_logos(sports_category)
            self.stdout.write(
                self.style.SUCCESS(f"Updated TheSportsDB KPL logos on {n} event(s).")
            )
            return

        # Clear existing FKF Premier League events if requested
        if clear_existing:
            deleted_count, _ = Event.objects.filter(
                subtitle__icontains='FKF Premier League',
                category=sports_category,
            ).delete()
            self.stdout.write(f"Deleted {deleted_count} existing FKF Premier League events")

        # Create venues and events
        created_count = 0
        with transaction.atomic():
            for fixture in FKF_FIXTURES:
                event = self.create_event(fixture, sports_category, organizer)
                if event:
                    self.create_ticket_tiers(event, fixture)
                    created_count += 1
                    self.stdout.write(f"Created: {event.title}")
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully imported {created_count} FKF fixtures!')
        )
    
    def refresh_kpl_logos(self, sports_category):
        """Re-apply KPL TheSportsDB badges to events from a previous import."""
        qs = Event.objects.filter(
            category=sports_category,
            subtitle__icontains='FKF Premier League',
        )
        updated = 0
        for event in qs:
            md = dict(event.match_data) if event.match_data else {}
            home = md.get('home_team')
            away = md.get('away_team')
            if not home or not away:
                continue
            ha = get_team_assets(home)
            aa = get_team_assets(away)
            if ha.get('logo'):
                md['home_team_logo'] = ha['logo']
                md['home_team_primary_color'] = ha.get(
                    'primary_color', md.get('home_team_primary_color', '#000000')
                )
                md['home_team_secondary_color'] = ha.get(
                    'secondary_color', md.get('home_team_secondary_color', '#FFFFFF')
                )
            if aa.get('logo'):
                md['away_team_logo'] = aa['logo']
                md['away_team_primary_color'] = aa.get(
                    'primary_color', md.get('away_team_primary_color', '#000000')
                )
                md['away_team_secondary_color'] = aa.get(
                    'secondary_color', md.get('away_team_secondary_color', '#FFFFFF')
                )
            branding = dict(md.get('branding') or {})
            branding['fkf'] = FKF_BRANDING
            branding['sponsor'] = TITLE_SPONSOR
            branding['kpl'] = KPL_THESPORTSDB
            md['branding'] = branding
            event.match_data = md
            event.save(update_fields=['match_data'])
            updated += 1
            self.stdout.write(f"  Refreshed logos: {event.title}")
        return updated

    def get_organizer(self, organizer_id):
        """Get the organizer user"""
        if organizer_id:
            try:
                return User.objects.get(id=organizer_id)
            except User.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'User {organizer_id} not found'))
        
        # Default to first superuser
        return User.objects.filter(is_superuser=True).first()
    
    def get_or_create_venue(self, stadium_name):
        """Get or create a venue for the stadium"""
        venue, created = Venue.objects.get_or_create(
            name=stadium_name,
            defaults={
                'address': stadium_name,
                'city': STADIUM_CITIES.get(stadium_name, 'Unknown'),
                'country': 'Kenya',
                'capacity': STADIUM_CAPACITIES.get(stadium_name, 5000),
                'is_active': True,
            }
        )
        if created:
            self.stdout.write(f"  Created venue: {venue.name}")
        return venue
    
    def create_event(self, fixture, category, organizer):
        """Create an event from a fixture"""
        home_team = fixture['home_team']
        away_team = fixture['away_team']
        match_id = fixture['match_id']
        
        # Check if event already exists
        title = f"{home_team} vs {away_team}"
        slug_base = f"{home_team.lower().replace(' ', '-')}-vs-{away_team.lower().replace(' ', '-')}"
        slug = f"{slug_base}-{fixture['date']}"
        
        if Event.objects.filter(slug=slug).exists():
            self.stdout.write(f"  Event already exists: {title}")
            return None
        
        # Get or create venue
        venue = self.get_or_create_venue(fixture['stadium'])
        
        # Parse date and time
        date_str = fixture['date']
        time_str = fixture['time']
        start_datetime = timezone.make_aware(
            datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        )
        # Football matches typically last 2 hours
        end_datetime = start_datetime + timedelta(hours=2)
        
        # Get team assets (TheSportsDB KPL badges + colors)
        home_assets = get_team_assets(fixture["home_team"])
        away_assets = get_team_assets(fixture["away_team"])
        
        # Create event
        event = Event.objects.create(
            title=title,
            slug=slug,
            subtitle=f"FKF Premier League Match Day - {fixture['category']} Category",
            description=self.get_match_description(fixture),
            category=category,
            venue=venue,
            organizer=organizer,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            doors_open=(start_datetime - timedelta(minutes=30)).time(),
            age_restriction='All Ages',
            status='published',
            is_public=True,
            featured=fixture['category'] == 'A',  # Feature category A matches
            tags=['football', 'FKF', 'premier league', 'sports', 'kenya'],
            match_data={
                'match_id': fixture['match_id'],
                'home_team': fixture['home_team'],
                'away_team': fixture['away_team'],
                'home_team_logo': home_assets.get('logo', ''),
                'away_team_logo': away_assets.get('logo', ''),
                'home_team_primary_color': home_assets.get('primary_color', '#000000'),
                'home_team_secondary_color': home_assets.get('secondary_color', '#FFFFFF'),
                'away_team_primary_color': away_assets.get('primary_color', '#000000'),
                'away_team_secondary_color': away_assets.get('secondary_color', '#FFFFFF'),
                'category': fixture['category'],
                'stadium': fixture['stadium'],
                'branding': {
                    'fkf': FKF_BRANDING,
                    'sponsor': TITLE_SPONSOR,
                    'kpl': KPL_THESPORTSDB,
                }
            },
        )
        
        return event
    
    def get_match_description(self, fixture):
        """Generate match description"""
        category_info = {
            "A": "Top-tier match featuring the biggest clubs",
            "B": "Exciting mid-table clash",
            "C": "Promising match with upcoming talent"
        }
        
        return f"""
<h2>FKF Premier League Match</h2>
<p><strong>{fixture['home_team']}</strong> vs <strong>{fixture['away_team']}</strong></p>

<p>Join us for an exciting {category_info.get(fixture['category'], 'League match')} at {fixture['stadium']}.</p>

<h3>Match Details</h3>
<ul>
    <li><strong>Date:</strong> {fixture['date']}</li>
    <li><strong>Time:</strong> {fixture['time']} EAT</li>
    <li><strong>Venue:</strong> {fixture['stadium']}</li>
    <li><strong>Category:</strong> {fixture['category']}</li>
</ul>

<h3>Ticket Information</h3>
<p>Tickets available in Regular and VIP tiers. Book early to secure your seat!</p>

<p><em>Match ID: {fixture['match_id']}</em></p>
        """.strip()
    
    def create_ticket_tiers(self, event, fixture):
        """Create Regular and VIP ticket tiers for the event"""
        quantities = CATEGORY_QUANTITIES.get(fixture['category'], {"regular": 5000, "vip": 1000})
        
        # Regular tier
        regular_tier, _ = TicketTier.objects.get_or_create(
            event=event,
            name='Regular',
            defaults={
                'description': f'Standard seating - {fixture["category"]} category match',
                'price': fixture['base_price_regular'],
                'currency': 'KES',
                'total_quantity': quantities['regular'],
                'available_quantity': quantities['regular'],
                'min_per_order': 1,
                'max_per_order': 10,
                'is_active': True,
                'order': 1,
                'benefits': ['Standard seating', 'Access to match viewing'],
            }
        )
        
        # VIP tier
        vip_tier, _ = TicketTier.objects.get_or_create(
            event=event,
            name='VIP',
            defaults={
                'description': f'Premium seating with better views - {fixture["category"]} category match',
                'price': fixture['base_price_vip'],
                'currency': 'KES',
                'total_quantity': quantities['vip'],
                'available_quantity': quantities['vip'],
                'min_per_order': 1,
                'max_per_order': 10,
                'is_active': True,
                'order': 0,  # VIP shown first
                'benefits': ['Premium seating with better views', 'Access to VIP sections', 'Priority entry'],
            }
        )
        
        self.stdout.write(f"  Created ticket tiers: Regular (KES {regular_tier.price}), VIP (KES {vip_tier.price})")

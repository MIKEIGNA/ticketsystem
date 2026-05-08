"""
Import FKF fixtures as sports events.

Usage:
    python manage.py import_fkf_fixtures [--organizer-id <uuid>]
"""

import json
from datetime import datetime, timedelta
from django.utils import timezone
from django.core.management.base import BaseCommand
from django.db import transaction
from events.models import Category, Venue, Event, TicketTier
from accounts.models import User


# Team logo URLs
TEAM_ASSETS = {
    "Gor Mahia": "https://upload.wikimedia.org/wikipedia/en/7/75/Gor_Mahia_FC_logo.png",
    "AFC Leopards": "https://upload.wikimedia.org/wikipedia/en/e/e0/AFC_Leopards_logo.png",
    "Kenya Police FC": "https://pbs.twimg.com/profile_images/1450711904791535616/7fE0X4_R_400x400.jpg",
    "Tusker FC": "https://upload.wikimedia.org/wikipedia/en/d/d3/Tusker_FC_logo.png",
    "Bandari FC": "https://upload.wikimedia.org/wikipedia/en/6/6a/Bandari_FC_logo.png",
    "KCB FC": "https://upload.wikimedia.org/wikipedia/en/a/a2/KCB_FC_logo.png",
    "Kakamega Homeboyz": "https://pbs.twimg.com/profile_images/1155793080033992704/9E-1Hq-6_400x400.jpg",
    "Murang'a SEAL": "https://pbs.twimg.com/profile_images/1699042296718749696/S_6lXkZ4_400x400.jpg",
    "Shabana FC": "https://pbs.twimg.com/profile_images/1678734005161725952/xH8B0wNf_400x400.jpg",
    "Ulinzi Stars": "https://upload.wikimedia.org/wikipedia/en/1/1e/Ulinzi_Stars_logo.png",
    "Kariobangi Sharks": "https://upload.wikimedia.org/wikipedia/en/7/71/Kariobangi_Sharks_logo.png",
    "Posta Rangers": "https://pbs.twimg.com/profile_images/1283685412401254400/6-Y6p8jH_400x400.jpg",
    "Sofapaka FC": "https://upload.wikimedia.org/wikipedia/en/8/8e/Sofapaka_FC_logo.png",
    "Mathare United": "https://upload.wikimedia.org/wikipedia/en/e/e5/Mathare_United_logo.png",
    "Bidco United": "https://pbs.twimg.com/profile_images/1330843232230158337/XfHqT9f7_400x400.jpg",
    "Nairobi United": "https://pbs.twimg.com/profile_images/1689254881699311616/6p9-8_Fm_400x400.jpg",
    "Mara Sugar FC": "https://pbs.twimg.com/profile_images/1458392135916666880/P6bHkP7a_400x400.jpg",
    "APS Bomet": "https://pbs.twimg.com/profile_images/1547847775684075520/2XpU-RjX_400x400.jpg"
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
            help='Delete existing FKF events before importing'
        )

    def handle(self, *args, **options):
        organizer_id = options['organizer_id']
        clear_existing = options['clear_existing']
        
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
        
        # Clear existing FKF events if requested
        if clear_existing:
            deleted_count, _ = Event.objects.filter(
                title__icontains='FKF',
                category=sports_category
            ).delete()
            self.stdout.write(f"Deleted {deleted_count} existing FKF events")
        
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
        
        # Get team logos
        home_team_logo = TEAM_ASSETS.get(fixture['home_team'], '')
        away_team_logo = TEAM_ASSETS.get(fixture['away_team'], '')
        
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
                'home_team_logo': home_team_logo,
                'away_team_logo': away_team_logo,
                'category': fixture['category'],
                'stadium': fixture['stadium'],
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

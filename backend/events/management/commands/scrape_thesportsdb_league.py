"""
Scrape TheSportsDB league page and save fixtures as events.

Usage:
    python manage.py scrape_thesportsdb_league [--league-path <path>] [--clear-existing]
"""

from datetime import date, timedelta, datetime
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify
import uuid

from events.models import Category, Venue, Event, TicketTier
from events.thesportsdb_league_scraper import scrape_league_page
from accounts.models import User


DEFAULT_LEAGUE_PATH = "/league/4745-kenyan-premier-league"


class Command(BaseCommand):
    help = 'Scrape TheSportsDB league page and save fixtures as events'

    def add_arguments(self, parser):
        parser.add_argument(
            '--league-path',
            default=DEFAULT_LEAGUE_PATH,
            help='TheSportsDB league path (default: /league/4745-kenyan-premier-league)'
        )
        parser.add_argument(
            '--organizer-id',
            help='UUID of the organizer user to assign events to'
        )
        parser.add_argument(
            '--clear-existing',
            action='store_true',
            help='Delete existing events from this league before importing'
        )
        parser.add_argument(
            '--upcoming-only',
            action='store_true',
            help='Only import upcoming fixtures, skip results'
        )

    def handle(self, *args, **options):
        league_path = options['league_path']
        organizer_id = options['organizer_id']
        clear_existing = options['clear_existing']
        upcoming_only = options['upcoming_only']
        
        # Scrape the league page
        self.stdout.write(f"Scraping league page: {league_path}")
        try:
            page = scrape_league_page(league_path=league_path, reference_date=date.today())
        except Exception as e:
            self.stderr.write(f"Failed to scrape league page: {e}")
            return
        
        self.stdout.write(f"League: {page.league_name}")
        self.stdout.write(f"Season: {page.season}")
        self.stdout.write(f"Upcoming fixtures: {len(page.upcoming)}")
        self.stdout.write(f"Results: {len(page.results)}")
        self.stdout.write(f"Teams: {len(page.teams)}")
        
        # Get or create organizer
        organizer = self.get_organizer(organizer_id)
        if not organizer:
            self.stderr.write("Failed to get or create organizer")
            return
        self.stdout.write(f"Using organizer: {organizer.email}")
        
        # Get or create Sports category
        sports_category, _ = Category.objects.get_or_create(
            name='Sports',
            defaults={'description': 'Sports events and matches'}
        )
        
        # Clear existing events if requested
        if clear_existing:
            deleted_count, _ = Event.objects.filter(
                subtitle__icontains=page.league_name,
                category=sports_category
            ).delete()
            self.stdout.write(f"Deleted {deleted_count} existing events")
        
        # Create team lookup from scraped teams
        team_lookup = {team.name: team for team in page.teams}
        
        # Process fixtures
        fixtures = page.upcoming if upcoming_only else page.upcoming + page.results
        created_count = 0
        updated_count = 0
        
        with transaction.atomic():
            for fixture in fixtures:
                # Skip if no kickoff time
                if not fixture.kickoff_local:
                    self.stdout.write(f"Skipping fixture without kickoff: {fixture.home_team} vs {fixture.away_team}")
                    continue
                
                # Create event title and slug
                title = f"{fixture.home_team} vs {fixture.away_team}"
                base_slug = slugify(title)
                # Add event ID to make slug unique
                unique_slug = f"{base_slug}-{fixture.id_event}"
                
                # Check if event already exists
                existing_event = Event.objects.filter(
                    title=title,
                    start_datetime=fixture.kickoff_local,
                    category=sports_category
                ).first()
                
                if existing_event:
                    updated_count += 1
                    self.stdout.write(f"Updating existing event: {title}")
                    continue
                
                # Get or create venue
                venue_name = f"{page.league_name} Stadium"
                venue, _ = Venue.objects.get_or_create(
                    name=venue_name,
                    defaults={
                        'address': page.location or 'Kenya',
                        'city': page.location or 'Nairobi',
                        'capacity': 50000
                    }
                )
                
                # Calculate end datetime (2 hours after start)
                start_datetime = fixture.kickoff_local
                end_datetime = start_datetime + timedelta(hours=2)
                
                # Get team assets
                home_team = team_lookup.get(fixture.home_team)
                away_team = team_lookup.get(fixture.away_team)
                
                home_badge = home_team.badge_url if home_team else fixture.home_badge_url
                away_badge = away_team.badge_url if away_team else fixture.away_badge_url
                
                # Create event
                event = Event.objects.create(
                    title=title,
                    slug=unique_slug,
                    subtitle=f"{page.league_name} - {page.season or ''}",
                    description=f"{page.league_name} match between {fixture.home_team} and {fixture.away_team}.",
                    category=sports_category,
                    venue=venue,
                    organizer=organizer,
                    start_datetime=start_datetime,
                    end_datetime=end_datetime,
                    status='published',
                    match_data={
                        'home_team': fixture.home_team,
                        'away_team': fixture.away_team,
                        'home_team_logo': home_badge,
                        'away_team_logo': away_badge,
                        'home_score': fixture.home_score,
                        'away_score': fixture.away_score,
                        'section': fixture.section,
                        'id_event': fixture.id_event,
                        'href': fixture.href,
                        'league': {
                            'name': page.league_name,
                            'path': page.league_path,
                            'season': page.season,
                            'badge_url': page.badge_url,
                            'logo_url': page.logo_url,
                        }
                    }
                )
                
                # Create ticket tiers
                TicketTier.objects.create(
                    event=event,
                    name='Regular',
                    price=500,
                    total_quantity=1000,
                    available_quantity=1000
                )
                
                TicketTier.objects.create(
                    event=event,
                    name='VIP',
                    price=2000,
                    total_quantity=100,
                    available_quantity=100
                )
                
                created_count += 1
                self.stdout.write(f"Created event: {title} at {start_datetime}")
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully processed {len(fixtures)} fixtures! '
                f'Created: {created_count}, Updated: {updated_count}'
            )
        )
    
    def get_organizer(self, organizer_id):
        """Get or create the organizer user"""
        if organizer_id:
            try:
                return User.objects.get(id=organizer_id, is_organizer=True)
            except User.DoesNotExist:
                self.stderr.write(f"Organizer with ID {organizer_id} not found")
                return None
        
        # Try to find an existing organizer
        organizer = User.objects.filter(is_organizer=True, is_verified=True).first()
        if organizer:
            return organizer
        
        # Create a default organizer
        organizer = User.objects.create_user(
            username='thesportsdb_organizer',
            email='thesportsdb@brightpassticket.co.ke',
            password='TempPass123!',
            first_name='TheSportsDB',
            last_name='Importer',
            is_organizer=True,
            is_verified=True
        )
        self.stdout.write("Created default organizer user")
        return organizer

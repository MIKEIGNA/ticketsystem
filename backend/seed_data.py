#!/usr/bin/env python
"""Seed script to create sample data for testing."""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ticketsystem.settings')
django.setup()

from accounts.models import User
from events.models import Category, Venue, Event, TicketTier
from datetime import datetime, timedelta
import random

def seed_data():
    print("Creating sample data...")

    # Create Categories
    categories_data = [
        {'name': 'Music', 'slug': 'music', 'color': '#ec4899', 'icon': 'music', 'description': 'Concerts and live music performances'},
        {'name': 'Sports', 'slug': 'sports', 'color': '#3b82f6', 'icon': 'trophy', 'description': 'Sports matches and tournaments'},
        {'name': 'Theatre', 'slug': 'theatre', 'color': '#8b5cf6', 'icon': 'drama', 'description': 'Theatrical performances and plays'},
        {'name': 'Comedy', 'slug': 'comedy', 'color': '#f59e0b', 'icon': 'smile', 'description': 'Stand-up comedy shows'},
        {'name': 'Conferences', 'slug': 'conferences', 'color': '#10b981', 'icon': 'briefcase', 'description': 'Professional conferences and seminars'},
        {'name': 'Festivals', 'slug': 'festivals', 'color': '#ef4444', 'icon': 'calendar', 'description': 'Cultural and music festivals'},
    ]

    categories = []
    for cat_data in categories_data:
        cat, created = Category.objects.get_or_create(slug=cat_data['slug'], defaults=cat_data)
        categories.append(cat)
        print(f"  {'Created' if created else 'Found'} category: {cat.name}")

    # Create Venues
    venues_data = [
        {'name': 'KICC', 'address': 'Harambee Avenue', 'city': 'Nairobi', 'capacity': 5000},
        {'name': 'Carnivore Grounds', 'address': 'Langata Road', 'city': 'Nairobi', 'capacity': 10000},
        {'name': 'Uhuru Gardens', 'address': 'Langata Road', 'city': 'Nairobi', 'capacity': 25000},
        {'name': 'Moi International Sports Centre', 'address': 'Thika Road', 'city': 'Nairobi', 'capacity': 60000},
        {'name': 'Sarit Centre', 'address': 'Karuna Road', 'city': 'Nairobi', 'capacity': 2000},
        {'name': 'Alliance Francaise', 'address': 'Monrovia Street', 'city': 'Nairobi', 'capacity': 500},
    ]

    venues = []
    for venue_data in venues_data:
        venue, created = Venue.objects.get_or_create(name=venue_data['name'], defaults=venue_data)
        venues.append(venue)
        print(f"  {'Created' if created else 'Found'} venue: {venue.name}")

    # Create Events
    events_data = [
        {
            'title': 'Sauti Sol Live in Concert',
            'slug': 'sauti-sol-live-2026',
            'subtitle': 'The Midnight Train Tour',
            'description': 'Kenya\'s biggest band performs live! Experience an unforgettable night of music, dance, and entertainment. Featuring all their hit songs from the Midnight Train album and classic favorites.',
            'category': 'Music',
            'venue': 'Carnivore Grounds',
            'days_from_now': 14,
            'featured': True,
            'price_range': (1500, 5000),
        },
        {
            'title': 'Kenya vs Uganda Rugby Match',
            'slug': 'kenya-vs-uganda-rugby-2026',
            'subtitle': 'Elgon Cup 2026',
            'description': 'Watch the Simbas battle it out against Uganda in the annual Elgon Cup. An intense rugby match featuring East Africa\'s finest players.',
            'category': 'Sports',
            'venue': 'KICC',
            'days_from_now': 7,
            'featured': True,
            'price_range': (500, 2000),
        },
        {
            'title': 'Laugh Festival Nairobi',
            'slug': 'laugh-festival-nairobi-2026',
            'subtitle': 'Comedy Night Special',
            'description': 'The biggest comedy show in East Africa featuring top comedians from Kenya, Uganda, and Tanzania. A night of non-stop laughter!',
            'category': 'Comedy',
            'venue': 'Sarit Centre',
            'days_from_now': 21,
            'featured': False,
            'price_range': (1000, 3000),
        },
        {
            'title': 'Blankets & Wine Festival',
            'slug': 'blankets-wine-festival-2026',
            'subtitle': 'Summer Edition',
            'description': 'The iconic music and lifestyle festival returns! Bring your blankets, enjoy great wine, amazing food, and incredible live performances.',
            'category': 'Festivals',
            'venue': 'Uhuru Gardens',
            'days_from_now': 30,
            'featured': True,
            'price_range': (2000, 8000),
        },
        {
            'title': 'Tech Summit Africa 2026',
            'slug': 'tech-summit-africa-2026',
            'subtitle': 'Innovation & Technology',
            'description': 'Connect with Africa\'s leading tech innovators, startups, and investors. Keynotes, workshops, and networking opportunities.',
            'category': 'Conferences',
            'venue': 'KICC',
            'days_from_now': 45,
            'featured': False,
            'price_range': (5000, 15000),
        },
        {
            'title': 'Grease The Musical',
            'slug': 'grease-musical-nairobi-2026',
            'subtitle': 'Broadway in Nairobi',
            'description': 'The classic musical comes to Nairobi! Experience the magic of Broadway with an all-Kenyan cast.',
            'category': 'Theatre',
            'venue': 'Alliance Francaise',
            'days_from_now': 10,
            'featured': False,
            'price_range': (2000, 5000),
        },
    ]

    for event_data in events_data:
        category = Category.objects.get(name=event_data['category'])
        venue = Venue.objects.get(name=event_data['venue'])
        
        start_datetime = datetime.now() + timedelta(days=event_data['days_from_now'])
        
        event, created = Event.objects.get_or_create(
            slug=event_data['slug'],
            defaults={
                'title': event_data['title'],
                'subtitle': event_data['subtitle'],
                'description': event_data['description'],
                'category': category,
                'venue': venue,
                'start_datetime': start_datetime,
                'end_datetime': start_datetime + timedelta(hours=4),
                'featured': event_data['featured'],
                'is_public': True,
                'status': 'published',
                'organizer_id': User.objects.filter(is_superuser=True).first().id if User.objects.filter(is_superuser=True).exists() else 1,
            }
        )
        
        if created:
            # Create ticket tiers for this event
            min_price, max_price = event_data['price_range']
            tier_names = ['Early Bird', 'Regular', 'VIP', 'VVIP'] if max_price > 3000 else ['Regular', 'VIP']
            
            for i, tier_name in enumerate(tier_names):
                price = min_price + (max_price - min_price) * i // (len(tier_names) - 1) if len(tier_names) > 1 else min_price
                qty = random.randint(100, 500)
                TicketTier.objects.create(
                    event=event,
                    name=tier_name,
                    description=f'{tier_name} access to {event.title}',
                    price=price,
                    total_quantity=qty,
                    available_quantity=qty,
                    max_per_order=10,
                    is_active=True,
                )
            
            print(f"  Created event: {event.title} with {len(tier_names)} ticket tiers")
        else:
            print(f"  Found event: {event.title}")

    print("\nSample data created successfully!")
    print("\nAdmin credentials:")
    print("  Username: admin")
    print("  Password: admin123")

if __name__ == '__main__':
    seed_data()

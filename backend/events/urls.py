from django.urls import path

from .views import (
    CategoryListView,
    CategoryDetailView,
    VenueListView,
    VenueDetailView,
    EventListView,
    EventDetailView,
    FeaturedEventsView,
    MyEventsView,
    TicketTierListView,
    TicketTierDetailView,
    EventSearchView
)

urlpatterns = [
    # Categories
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('categories/<slug:slug>/', CategoryDetailView.as_view(), name='category-detail'),
    
    # Venues
    path('venues/', VenueListView.as_view(), name='venue-list'),
    path('venues/<uuid:pk>/', VenueDetailView.as_view(), name='venue-detail'),
    
    # Events
    path('', EventListView.as_view(), name='event-list'),
    path('featured/', FeaturedEventsView.as_view(), name='featured-events'),
    path('my-events/', MyEventsView.as_view(), name='my-events'),
    path('search/', EventSearchView.as_view(), name='event-search'),
    path('<slug:slug>/', EventDetailView.as_view(), name='event-detail'),
    
    # Ticket Tiers
    path('<uuid:event_id>/tiers/', TicketTierListView.as_view(), name='ticket-tier-list'),
    path('tiers/<uuid:pk>/', TicketTierDetailView.as_view(), name='ticket-tier-detail'),
]

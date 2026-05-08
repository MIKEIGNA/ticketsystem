from rest_framework import generics, permissions, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import Q, Min

from .models import Category, Venue, Event, TicketTier
from .serializers import (
    CategorySerializer, CategoryListSerializer,
    VenueSerializer, VenueListSerializer,
    EventSerializer, EventListSerializer, EventCreateSerializer,
    TicketTierSerializer, TicketTierCreateSerializer
)


# ==================== CATEGORY VIEWS ====================

class CategoryListView(generics.ListAPIView):
    """ListAPIView: List all active categories"""
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategoryListSerializer
    permission_classes = [permissions.AllowAny]


class CategoryDetailView(generics.RetrieveAPIView):
    """RetrieveAPIView: Get category details with events"""
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'


# ==================== VENUE VIEWS ====================

class VenueListView(generics.ListCreateAPIView):
    """ListCreateAPIView: List all venues or create new"""
    queryset = Venue.objects.filter(is_active=True)
    serializer_class = VenueSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name', 'city', 'address']
    filterset_fields = ['city']

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return VenueListSerializer
        return VenueSerializer


class VenueDetailView(generics.RetrieveUpdateDestroyAPIView):
    """RetrieveUpdateDestroyAPIView: Venue CRUD operations"""
    queryset = Venue.objects.all()
    serializer_class = VenueSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


# ==================== EVENT VIEWS ====================

class EventListView(generics.ListCreateAPIView):
    """ListCreateAPIView: List events or create new"""
    serializer_class = EventListSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['title', 'subtitle', 'description', 'tags']
    filterset_fields = ['category', 'status', 'featured', 'venue__city']
    ordering_fields = ['start_datetime', 'created_at', 'view_count']
    ordering = ['-start_datetime']

    def get_queryset(self):
        queryset = Event.objects.filter(is_public=True, status='published')
        
        # Filter by date range
        date_from = self.request.query_params.get('from')
        date_to = self.request.query_params.get('to')
        
        if date_from:
            queryset = queryset.filter(start_datetime__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(start_datetime__date__lte=date_to)
        
        # Filter by price range
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        
        if min_price or max_price:
            queryset = queryset.filter(
                ticket_tiers__price__gte=min_price or 0,
                ticket_tiers__price__lte=max_price or 999999,
                ticket_tiers__is_active=True
            ).distinct()
        
        # Filter upcoming/finished events
        filter_type = self.request.query_params.get('filter')
        if filter_type == 'upcoming':
            queryset = queryset.filter(start_datetime__gt=timezone.now())
        elif filter_type == 'today':
            today = timezone.now().date()
            queryset = queryset.filter(start_datetime__date=today)
        elif filter_type == 'finished':
            queryset = queryset.filter(start_datetime__lt=timezone.now())
        
        # Annotate with lowest price
        queryset = queryset.annotate(lowest_price=Min('ticket_tiers__price'))
        
        return queryset.select_related('category', 'venue').prefetch_related('ticket_tiers')

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return EventCreateSerializer
        if self.request.user.is_authenticated and (self.request.user.is_staff or getattr(self.request.user, 'is_organizer', False)):
            return EventSerializer
        return EventListSerializer

    def perform_create(self, serializer):
        serializer.save(organizer=self.request.user)


class EventDetailView(generics.RetrieveUpdateDestroyAPIView):
    """RetrieveUpdateDestroyAPIView: Event CRUD operations"""
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'

    def get_queryset(self):
        if self.request.user.is_authenticated and (self.request.user.is_staff or getattr(self.request.user, 'is_organizer', False)):
            return Event.objects.all()
        return Event.objects.filter(is_public=True, status='published')

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Increment view count
        instance.view_count += 1
        instance.save(update_fields=['view_count'])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [permissions.IsAuthenticated(), IsOrganizerOrReadOnly()]
        return [permissions.AllowAny()]


class FeaturedEventsView(generics.ListAPIView):
    """ListAPIView: Get featured upcoming events"""
    serializer_class = EventListSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Event.objects.filter(
            featured=True,
            status='published',
            start_datetime__gt=timezone.now()
        ).select_related('category', 'venue')[:6]


class MyEventsView(generics.ListAPIView):
    """ListAPIView: Get events organized by current user"""
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Event.objects.filter(organizer=self.request.user)


# ==================== TICKET TIER VIEWS ====================

class TicketTierListView(generics.ListCreateAPIView):
    """ListCreateAPIView: List or create ticket tiers for an event"""
    serializer_class = TicketTierSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        event_id = self.kwargs.get('event_id')
        return TicketTier.objects.filter(event_id=event_id)

    def perform_create(self, serializer):
        from .models import Event
        event = Event.objects.get(id=self.kwargs.get('event_id'))
        serializer.save(event=event)


class TicketTierDetailView(generics.RetrieveUpdateDestroyAPIView):
    """RetrieveUpdateDestroyAPIView: Ticket tier operations"""
    queryset = TicketTier.objects.all()
    serializer_class = TicketTierSerializer
    permission_classes = [permissions.IsAuthenticated]


# ==================== CUSTOM PERMISSION ====================

class IsOrganizerOrReadOnly(permissions.BasePermission):
    """Custom permission to only allow organizers of an event to edit it"""
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.organizer == request.user or request.user.is_staff


# ==================== SEARCH VIEW ====================

class EventSearchView(APIView):
    """APIView for advanced event search"""
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        query = request.query_params.get('q', '')
        
        events = Event.objects.filter(
            Q(title__icontains=query) |
            Q(subtitle__icontains=query) |
            Q(description__icontains=query) |
            Q(tags__icontains=query) |
            Q(venue__name__icontains=query) |
            Q(venue__city__icontains=query),
            status='published',
            is_public=True
        ).select_related('category', 'venue').distinct()[:20]
        
        serializer = EventListSerializer(events, many=True)
        return Response(serializer.data)


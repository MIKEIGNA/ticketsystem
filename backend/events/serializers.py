from rest_framework import serializers
from .models import Category, Venue, Event, TicketTier
from .kpl_team_logos import enrich_match_data_logos


class MatchDataLogoMixin:
    """Attach KPL badge URLs to match_data when DB omitted them."""

    def to_representation(self, instance):
        data = super().to_representation(instance)
        md = data.get("match_data")
        if md is not None:
            data["match_data"] = enrich_match_data_logos(md)
        return data


class CategorySerializer(serializers.ModelSerializer):
    event_count = serializers.IntegerField(source='events.count', read_only=True)
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'icon', 'color', 
                  'image', 'is_active', 'event_count']


class CategoryListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing categories"""
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'icon', 'color']


class VenueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Venue
        fields = ['id', 'name', 'address', 'city', 'country', 
                  'latitude', 'longitude', 'capacity', 'description',
                  'image', 'parking_info', 'accessibility_info',
                  'contact_phone', 'contact_email']


class VenueListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing venues"""
    class Meta:
        model = Venue
        fields = ['id', 'name', 'city', 'image']


class TicketTierSerializer(serializers.ModelSerializer):
    is_on_sale = serializers.BooleanField(read_only=True)
    sold_percentage = serializers.FloatField(read_only=True)
    
    class Meta:
        model = TicketTier
        fields = ['id', 'name', 'description', 'price', 'currency',
                  'available_quantity', 'min_per_order', 'max_per_order',
                  'sales_start', 'sales_end', 'is_active', 'is_on_sale',
                  'includes_seat', 'seat_section', 'benefits',
                  'sold_percentage', 'order']


class TicketTierCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating ticket tiers"""
    class Meta:
        model = TicketTier
        fields = ['name', 'description', 'price', 'total_quantity',
                  'min_per_order', 'max_per_order', 'sales_start', 
                  'sales_end', 'is_active', 'includes_seat', 
                  'seat_section', 'benefits', 'order']
    
    def create(self, validated_data):
        # Set available_quantity = total_quantity on creation
        validated_data['available_quantity'] = validated_data.get('total_quantity', 0)
        return super().create(validated_data)


class EventSerializer(MatchDataLogoMixin, serializers.ModelSerializer):
    category = CategoryListSerializer(read_only=True)
    venue = VenueSerializer(read_only=True)
    ticket_tiers = TicketTierSerializer(many=True, read_only=True)
    is_upcoming = serializers.BooleanField(read_only=True)
    days_until_event = serializers.IntegerField(read_only=True)
    lowest_price = serializers.SerializerMethodField()
    
    class Meta:
        model = Event
        fields = ['id', 'title', 'slug', 'subtitle', 'description',
                  'category', 'venue', 'start_datetime', 'end_datetime',
                  'doors_open', 'poster_image', 'banner_image',
                  'gallery_images', 'video_url', 'age_restriction',
                  'dress_code', 'featured', 'tags', 'status', 'is_public',
                  'view_count', 'is_upcoming', 'days_until_event',
                  'ticket_tiers', 'lowest_price', 'match_data', 'created_at']
    
    def get_lowest_price(self, obj):
        tiers = obj.ticket_tiers.filter(is_active=True, available_quantity__gt=0)
        if tiers.exists():
            return min(tier.price for tier in tiers)
        return None


class EventListSerializer(MatchDataLogoMixin, serializers.ModelSerializer):
    """Lightweight serializer for event listings"""
    category = CategoryListSerializer(read_only=True)
    venue_name = serializers.CharField(source='venue.name', read_only=True)
    venue_city = serializers.CharField(source='venue.city', read_only=True)
    lowest_price = serializers.SerializerMethodField()
    
    class Meta:
        model = Event
        fields = ['id', 'title', 'slug', 'subtitle', 'category',
                  'venue_name', 'venue_city', 'start_datetime',
                  'poster_image', 'featured', 'status', 'lowest_price',
                  'days_until_event', 'match_data']
    
    def get_lowest_price(self, obj):
        tiers = obj.ticket_tiers.filter(is_active=True, available_quantity__gt=0)
        if tiers.exists():
            return min(tier.price for tier in tiers)
        return None


class EventCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating events"""
    category_id = serializers.UUIDField(write_only=True)
    venue_id = serializers.UUIDField(write_only=True)
    ticket_tiers = TicketTierCreateSerializer(many=True, write_only=True, required=False)
    
    class Meta:
        model = Event
        fields = ['title', 'subtitle', 'description', 'category_id', 'venue_id',
                  'start_datetime', 'end_datetime', 'doors_open',
                  'poster_image', 'banner_image', 'gallery_images', 'video_url',
                  'age_restriction', 'dress_code', 'featured', 'tags',
                  'meta_title', 'meta_description', 'ticket_tiers']
    
    def create(self, validated_data):
        ticket_tiers_data = validated_data.pop('ticket_tiers', [])
        category_id = validated_data.pop('category_id')
        venue_id = validated_data.pop('venue_id')
        
        # Get related objects
        from .models import Category, Venue
        category = Category.objects.get(id=category_id)
        venue = Venue.objects.get(id=venue_id)
        
        # Create event
        event = Event.objects.create(
            category=category,
            venue=venue,
            organizer=self.context['request'].user,
            **validated_data
        )
        
        # Create ticket tiers
        for tier_data in ticket_tiers_data:
            TicketTier.objects.create(event=event, **tier_data)
        
        return event

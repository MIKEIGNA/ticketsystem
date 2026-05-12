from rest_framework import serializers
from .models import Booking, Ticket
from events.serializers import TicketTierSerializer, EventListSerializer


class TicketSerializer(serializers.ModelSerializer):
    ticket_tier_name = serializers.CharField(source='ticket_tier.name', read_only=True)
    event_title = serializers.CharField(source='booking.event.title', read_only=True)
    event_date = serializers.DateTimeField(source='booking.event.start_datetime', read_only=True)
    venue_name = serializers.CharField(source='booking.event.venue.name', read_only=True)
    qr_code_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Ticket
        fields = ['id', 'ticket_number', 'ticket_tier', 'ticket_tier_name',
                  'price_paid', 'status', 'attendee_name', 'attendee_email',
                  'attendee_phone', 'seat_number', 'qr_code_url', 'qr_code_data',
                  'security_code',
                  'checked_in', 'checked_in_at', 'event_title', 'event_date',
                  'venue_name', 'created_at']
        read_only_fields = ['ticket_number', 'qr_code', 'qr_code_data', 'security_code', 'checked_in_at']
    
    def get_qr_code_url(self, obj):
        if obj.qr_code:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.qr_code.url)
        return None


class TicketCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating tickets within a booking"""
    ticket_tier_id = serializers.UUIDField()
    
    class Meta:
        model = Ticket
        fields = ['ticket_tier_id', 'attendee_name', 'attendee_email', 
                  'attendee_phone', 'seat_number']


class BookingSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=True)
    event = EventListSerializer(read_only=True)
    
    class Meta:
        model = Booking
        fields = ['id', 'booking_number', 'event', 'status', 'total_amount',
                  'ticket_count', 'contact_name', 'contact_email', 'contact_phone',
                  'special_requests', 'tickets', 'created_at', 'expires_at']
        read_only_fields = ['booking_number', 'created_at']


class BookingCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating bookings"""
    tickets = TicketCreateSerializer(many=True)
    event_id = serializers.UUIDField()
    
    class Meta:
        model = Booking
        fields = ['event_id', 'contact_name', 'contact_email', 'contact_phone',
                  'special_requests', 'tickets']
    
    def validate_tickets(self, value):
        if not value:
            raise serializers.ValidationError("At least one ticket is required")
        return value

    def validate_contact_phone(self, value):
        from accounts.models import normalize_phone
        return normalize_phone(value) if value else value
    
    def create(self, validated_data):
        from events.models import Event, TicketTier
        
        tickets_data = validated_data.pop('tickets')
        event_id = validated_data.pop('event_id')
        
        # Get user from context (passed by view via serializer.save(user=user))
        user = validated_data.pop('user', None)
        
        event = Event.objects.get(id=event_id)
        
        # Calculate total
        total_amount = 0
        ticket_count = len(tickets_data)
        
        # Validate ticket tiers and calculate price
        for ticket_data in tickets_data:
            tier_id = ticket_data['ticket_tier_id']
            tier = TicketTier.objects.get(id=tier_id, event=event)
            
            if tier.available_quantity < 1:
                raise serializers.ValidationError(
                    f"Ticket tier '{tier.name}' is sold out"
                )
            total_amount += tier.price
        
        # Create booking - user may be None for guest checkout
        # AUTO-CONFIRM FOR TESTING: Skip payment verification
        booking = Booking.objects.create(
            user=user,  # Set user here, can be None for guests
            event=event,
            total_amount=total_amount,
            ticket_count=ticket_count,
            status='confirmed',  # Auto-confirm for testing (bypass payment)
            **validated_data
        )
        
        # Create tickets
        created_tickets = []
        for ticket_data in tickets_data:
            tier_id = ticket_data.pop('ticket_tier_id')
            tier = TicketTier.objects.get(id=tier_id)

            # Normalize attendee phone
            from accounts.models import normalize_phone
            phone = ticket_data.get('attendee_phone') or ''
            if phone:
                ticket_data['attendee_phone'] = normalize_phone(phone)

            # Update available quantity
            tier.available_quantity -= 1
            tier.save()
            
            ticket = Ticket.objects.create(
                booking=booking,
                ticket_tier=tier,
                price_paid=tier.price,
                **ticket_data
            )
            created_tickets.append(ticket)
        
        # Return booking with tickets
        # Re-fetch booking to include related tickets
        booking.refresh_from_db()
        return booking


class BookingListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing bookings"""
    event_title = serializers.CharField(source='event.title', read_only=True)
    event_poster = serializers.ImageField(source='event.poster_image', read_only=True)
    event_date = serializers.DateTimeField(source='event.start_datetime', read_only=True)
    
    class Meta:
        model = Booking
        fields = ['id', 'booking_number', 'event_title', 'event_poster',
                  'event_date', 'status', 'total_amount', 'ticket_count', 'created_at']

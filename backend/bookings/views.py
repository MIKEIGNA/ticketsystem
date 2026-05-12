from typing import Optional

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, FileResponse
from django.utils import timezone

from .models import Booking, Ticket
from .serializers import (
    BookingSerializer, 
    BookingListSerializer, 
    BookingCreateSerializer,
    TicketSerializer
)
from .ticket_generator import generate_ticket_pdf
from .security_code import normalize_security_code


def resolve_ticket_for_gate(identifier: str) -> Optional[Ticket]:
    """Resolve a ticket from raw QR text, manual security code, or ticket number."""
    identifier = (identifier or "").strip()
    if not identifier:
        return None
    qs = Ticket.objects.select_related(
        "booking__event",
        "ticket_tier",
        "booking__event__organizer",
    )
    try:
        return qs.get(qr_code_data=identifier)
    except Ticket.DoesNotExist:
        pass
    norm = normalize_security_code(identifier)
    if norm:
        try:
            return qs.get(security_code=norm)
        except Ticket.DoesNotExist:
            pass
    try:
        return qs.get(ticket_number=identifier)
    except Ticket.DoesNotExist:
        return None


class BookingListView(generics.ListCreateAPIView):
    """ListCreateAPIView: List user's bookings or create new (supports guest checkout)"""
    
    def get_permissions(self):
        if self.request.method == 'POST':
            # Allow anyone to create a booking (guest checkout)
            return [permissions.AllowAny()]
        # Require authentication to list bookings
        return [permissions.IsAuthenticated()]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return BookingCreateSerializer
        return BookingListSerializer
    
    def create(self, request, *args, **kwargs):
        """Override create to return full booking with tickets after creation"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Set user if authenticated, otherwise None (guest checkout)
        user = request.user if request.user.is_authenticated else None
        
        try:
            booking = serializer.save(user=user)
        except Exception as exc:
            import traceback
            import logging
            logger = logging.getLogger(__name__)
            logger.error("Booking creation failed: %s\n%s", exc, traceback.format_exc())
            return Response(
                {'detail': str(exc), 'type': type(exc).__name__},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Return full booking with tickets using BookingSerializer
        output_serializer = BookingSerializer(booking)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Booking.objects.filter(user=self.request.user).select_related('event')
        return Booking.objects.none()

    def perform_create(self, serializer):
        # Set user if authenticated, otherwise None (guest checkout)
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(user=user)


class BookingDetailView(generics.RetrieveAPIView):
    """RetrieveAPIView: Get booking details with tickets"""
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'booking_number'
    lookup_url_kwarg = 'booking_number'

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)


class MyTicketsView(generics.ListAPIView):
    """ListAPIView: Get all tickets for current user"""
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Ticket.objects.filter(
            booking__user=self.request.user
        ).select_related('booking', 'ticket_tier', 'booking__event')


class TicketDetailView(generics.RetrieveAPIView):
    """RetrieveAPIView: Get ticket details with QR code"""
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'ticket_number'

    def get_queryset(self):
        return Ticket.objects.filter(booking__user=self.request.user)


class CheckInTicketView(APIView):
    """Check in by ticket number, manual security code (XXXX-…), or raw QR string."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, ticket_number):
        ticket = resolve_ticket_for_gate(ticket_number)
        if not ticket:
            return Response(
                {"error": "Ticket not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Only organizers and staff can check in tickets
        if not (request.user.is_staff or 
                request.user == ticket.booking.event.organizer):
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        success = ticket.check_in(checked_by=request.user)
        
        if success:
            return Response({
                'message': 'Ticket checked in successfully',
                'ticket_number': ticket.ticket_number,
                'checked_in_at': ticket.checked_in_at,
                'attendee': ticket.attendee_name or ticket.booking.contact_name
            })
        
        return Response(
            {'error': 'Ticket already checked in or invalid'},
            status=status.HTTP_400_BAD_REQUEST
        )


class ValidateTicketView(APIView):
    """Validate ticket by scanned QR payload (qr_data) or typed security_code."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        raw = request.data.get("qr_data") or request.data.get("security_code")
        if not raw:
            return Response(
                {"error": "qr_data or security_code required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        ticket = resolve_ticket_for_gate(raw)
        if not ticket:
            return Response(
                {"error": "Ticket not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        
        # Check permissions
        if not (request.user.is_staff or 
                request.user == ticket.booking.event.organizer):
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        return Response({
            'valid': ticket.status == 'valid',
            'ticket_number': ticket.ticket_number,
            'event': ticket.booking.event.title,
            'ticket_tier': ticket.ticket_tier.name,
            'attendee': ticket.attendee_name or ticket.booking.contact_name,
            'checked_in': ticket.checked_in,
            'checked_in_at': ticket.checked_in_at
        })


class TicketDownloadView(APIView):
    """APIView for downloading ticket as PDF"""
    
    def get(self, request, ticket_number):
        """Download ticket PDF - accessible by ticket owner or anyone with the link (guest tickets)"""
        ticket = get_object_or_404(
            Ticket.objects.select_related(
                'booking',
                'ticket_tier',
                'booking__event',
                'booking__event__category',
                'booking__event__venue',
                'booking__event__organizer',
            ),
            ticket_number=ticket_number,
        )

        # Allow download if:
        # 1. User is authenticated and owns the booking
        # 2. Guest checkout (no user) - anyone with the ticket number can download
        if (request.user.is_authenticated and 
            ticket.booking.user and 
            request.user != ticket.booking.user and
            not request.user.is_staff):
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Generate PDF
        try:
            pdf = generate_ticket_pdf(ticket)
            
            # Create response with PDF
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="ticket_{ticket_number}.pdf"'
            return response
            
        except Exception as e:
            return Response(
                {'error': f'Failed to generate ticket PDF: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


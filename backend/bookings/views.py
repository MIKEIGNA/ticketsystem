from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from .models import Booking, Ticket
from .serializers import (
    BookingSerializer, 
    BookingListSerializer, 
    BookingCreateSerializer,
    TicketSerializer
)


class BookingListView(generics.ListCreateAPIView):
    """ListCreateAPIView: List user's bookings or create new"""
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return BookingCreateSerializer
        return BookingListSerializer

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user).select_related('event')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


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
    """APIView for ticket check-in at venue"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, ticket_number):
        ticket = get_object_or_404(Ticket, ticket_number=ticket_number)
        
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
    """APIView for validating ticket by QR code data"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        qr_data = request.data.get('qr_data')
        
        if not qr_data:
            return Response(
                {'error': 'QR code data required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        ticket = get_object_or_404(Ticket, qr_code_data=qr_data)
        
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


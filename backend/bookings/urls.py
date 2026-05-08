from django.urls import path

from .views import (
    BookingListView,
    BookingDetailView,
    MyTicketsView,
    TicketDetailView,
    CheckInTicketView,
    ValidateTicketView,
    TicketDownloadView
)

urlpatterns = [
    # Bookings
    path('', BookingListView.as_view(), name='booking-list'),
    path('<str:booking_number>/', BookingDetailView.as_view(), name='booking-detail'),
    
    # Tickets
    path('tickets/my-tickets/', MyTicketsView.as_view(), name='my-tickets'),
    path('tickets/<str:ticket_number>/', TicketDetailView.as_view(), name='ticket-detail'),
    path('tickets/<str:ticket_number>/download/', TicketDownloadView.as_view(), name='ticket-download'),
    
    # Check-in
    path('checkin/<str:ticket_number>/', CheckInTicketView.as_view(), name='check-in'),
    path('validate/', ValidateTicketView.as_view(), name='validate-ticket'),
]

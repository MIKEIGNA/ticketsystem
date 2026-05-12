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
    # Tickets — must come BEFORE <str:booking_number> to avoid being swallowed
    path('tickets/my-tickets/', MyTicketsView.as_view(), name='my-tickets'),
    path('tickets/<str:ticket_number>/download/', TicketDownloadView.as_view(), name='ticket-download'),
    path('tickets/<str:ticket_number>/', TicketDetailView.as_view(), name='ticket-detail'),

    # Check-in / validate
    path('checkin/<str:ticket_number>/', CheckInTicketView.as_view(), name='check-in'),
    path('validate/', ValidateTicketView.as_view(), name='validate-ticket'),

    # Bookings — generic slug last so it doesn't eat the routes above
    path('', BookingListView.as_view(), name='booking-list'),
    path('<str:booking_number>/', BookingDetailView.as_view(), name='booking-detail'),
]

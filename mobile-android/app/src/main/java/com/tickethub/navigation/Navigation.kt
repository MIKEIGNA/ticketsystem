package com.brightpassticket.navigation

sealed class Screen(val route: String) {
    // Auth
    object Splash : Screen("splash")
    object Login : Screen("login")
    object Register : Screen("register")

    // Main
    object Home : Screen("home")
    object Events : Screen("events")
    object EventDetail : Screen("event/{eventId}") {
        fun createRoute(eventId: String) = "event/$eventId"
    }
    object Search : Screen("search")

    // Booking
    object Booking : Screen("booking/{eventId}/{tierId}/{quantity}") {
        fun createRoute(eventId: String, tierId: String, quantity: Int) =
            "booking/$eventId/$tierId/$quantity"
    }
    object Payment : Screen("payment/{bookingId}/{amount}") {
        fun createRoute(bookingId: String, amount: Double) =
            "payment/$bookingId/$amount"
    }
    object BookingSuccess : Screen("booking_success/{bookingId}") {
        fun createRoute(bookingId: String) = "booking_success/$bookingId"
    }

    // Tickets
    object MyTickets : Screen("my_tickets")
    object TicketDetail : Screen("ticket/{ticketNumber}") {
        fun createRoute(ticketNumber: String) = "ticket/$ticketNumber"
    }

    // Organizer
    object OrganizerDashboard : Screen("organizer/dashboard")
    object CreateEvent : Screen("organizer/create_event")
    object EventStats : Screen("organizer/stats/{eventId}") {
        fun createRoute(eventId: String) = "organizer/stats/$eventId"
    }
    object CheckIn : Screen("organizer/checkin/{eventId}") {
        fun createRoute(eventId: String) = "organizer/checkin/$eventId"
    }

    // Profile
    object Profile : Screen("profile")
    object EditProfile : Screen("profile/edit")
}

package com.tickethub.data.model

import android.os.Parcelable
import kotlinx.parcelize.Parcelize
import java.time.LocalDateTime

// User Types
enum class UserRole {
    REGULAR, ORGANIZER, ADMIN, GUEST
}

@Parcelize
data class User(
    val id: String,
    val email: String,
    val firstName: String,
    val lastName: String,
    val phoneNumber: String?,
    val role: UserRole,
    val isOrganizer: Boolean,
    val avatar: String? = null
) : Parcelable

// Category
@Parcelize
data class Category(
    val id: String,
    val name: String,
    val slug: String,
    val description: String?,
    val icon: String?,
    val color: String,
    val image: String?,
    val isActive: Boolean
) : Parcelable

// Venue
@Parcelize
data class Venue(
    val id: String,
    val name: String,
    val address: String,
    val city: String,
    val country: String,
    val capacity: Int?,
    val image: String?,
    val latitude: Double?,
    val longitude: Double?
) : Parcelable

// Ticket Tier
@Parcelize
data class TicketTier(
    val id: String,
    val name: String,
    val description: String?,
    val price: Double,
    val currency: String,
    val availableQuantity: Int,
    val minPerOrder: Int,
    val maxPerOrder: Int,
    val isActive: Boolean,
    val benefits: List<String> = emptyList(),
    val isOnSale: Boolean = true
) : Parcelable

// Match Data for Sports Events
@Parcelize
data class MatchData(
    val matchId: String,
    val homeTeam: String,
    val awayTeam: String,
    val homeTeamLogo: String?,
    val awayTeamLogo: String?,
    val category: String,
    val stadium: String
) : Parcelable

// Event
@Parcelize
data class Event(
    val id: String,
    val title: String,
    val slug: String,
    val subtitle: String?,
    val description: String,
    val category: Category,
    val venue: Venue,
    val startDateTime: String,
    val endDateTime: String?,
    val posterImage: String?,
    val bannerImage: String?,
    val ageRestriction: String?,
    val featured: Boolean,
    val tags: List<String>,
    val status: String,
    val lowestPrice: Double?,
    val ticketTiers: List<TicketTier>,
    val matchData: MatchData?,
    val isUpcoming: Boolean,
    val daysUntilEvent: Int
) : Parcelable

// Booking
@Parcelize
data class Booking(
    val id: String,
    val bookingNumber: String,
    val event: Event,
    val status: String,
    val totalAmount: Double,
    val ticketCount: Int,
    val contactName: String,
    val contactEmail: String,
    val contactPhone: String?,
    val specialRequests: String?,
    val tickets: List<Ticket>,
    val createdAt: String,
    val expiresAt: String?
) : Parcelable

// Ticket
@Parcelize
data class Ticket(
    val id: String,
    val ticketNumber: String,
    val ticketTier: TicketTier,
    val pricePaid: Double,
    val status: String,
    val attendeeName: String?,
    val attendeeEmail: String?,
    val attendeePhone: String?,
    val seatNumber: String?,
    val qrCodeUrl: String?,
    val checkedIn: Boolean,
    val checkedInAt: String?,
    val eventTitle: String?,
    val eventDate: String?,
    val venueName: String?
) : Parcelable

// Payment
@Parcelize
data class Payment(
    val id: String,
    val transactionId: String,
    val bookingId: String,
    val amount: Double,
    val currency: String,
    val paymentMethod: String,
    val status: String,
    val phoneNumber: String?,
    val createdAt: String,
    val completedAt: String?
) : Parcelable

// Auth
@Parcelize
data class AuthResponse(
    val access: String,
    val refresh: String,
    val user: User
) : Parcelable

@Parcelize
data class LoginRequest(
    val email: String,
    val password: String
) : Parcelable

@Parcelize
data class RegisterRequest(
    val email: String,
    val password: String,
    val firstName: String,
    val lastName: String,
    val phoneNumber: String?,
    val isOrganizer: Boolean = false
) : Parcelable

// Booking Request
@Parcelize
data class TicketDetail(
    val attendeeName: String,
    val attendeeEmail: String,
    val attendeePhone: String?,
    val ticketTierId: String
) : Parcelable

@Parcelize
data class CreateBookingRequest(
    val eventId: String,
    val contactName: String,
    val contactEmail: String,
    val contactPhone: String?,
    val specialRequests: String?,
    val tickets: List<TicketDetail>
) : Parcelable

// Payment Request
@Parcelize
data class PaymentRequest(
    val bookingId: String,
    val phoneNumber: String
) : Parcelable

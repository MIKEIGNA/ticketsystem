package com.tickethub.api

import com.tickethub.data.model.*
import okhttp3.ResponseBody
import retrofit2.Response
import retrofit2.http.*

interface ApiService {

    // Authentication
    @POST("auth/token/")
    suspend fun login(@Body request: LoginRequest): Response<AuthResponse>

    @POST("auth/register/")
    suspend fun register(@Body request: RegisterRequest): Response<User>

    @POST("auth/token/refresh/")
    suspend fun refreshToken(@Body refresh: Map<String, String>): Response<AuthResponse>

    @GET("auth/user/")
    suspend fun getCurrentUser(): Response<User>

    @POST("auth/logout/")
    suspend fun logout(): Response<Unit>

    // Events
    @GET("events/")
    suspend fun getEvents(
        @Query("category") category: String? = null,
        @Query("search") search: String? = null,
        @Query("featured") featured: Boolean? = null,
        @Query("upcoming") upcoming: Boolean? = null,
        @Query("page") page: Int = 1
    ): Response<PaginatedResponse<Event>>

    @GET("events/categories/")
    suspend fun getCategories(): Response<List<Category>>

    @GET("events/{id}/")
    suspend fun getEventDetail(@Path("id") eventId: String): Response<Event>

    @GET("events/slug/{slug}/")
    suspend fun getEventBySlug(@Path("slug") slug: String): Response<Event>

    // Bookings
    @POST("bookings/")
    suspend fun createBooking(@Body request: CreateBookingRequest): Response<Booking>

    @GET("bookings/")
    suspend fun getMyBookings(): Response<List<Booking>>

    @GET("bookings/{id}/")
    suspend fun getBookingDetail(@Path("id") bookingId: String): Response<Booking>

    @GET("bookings/{id}/tickets/")
    suspend fun getBookingTickets(@Path("id") bookingId: String): Response<List<Ticket>>

    // Tickets
    @GET("bookings/tickets/{ticketNumber}/download/")
    suspend fun downloadTicket(
        @Path("ticketNumber") ticketNumber: String
    ): Response<ResponseBody>

    @POST("bookings/tickets/{ticketNumber}/validate/")
    suspend fun validateTicket(@Path("ticketNumber") ticketNumber: String): Response<Ticket>

    @POST("bookings/tickets/{ticketNumber}/checkin/")
    suspend fun checkInTicket(@Path("ticketNumber") ticketNumber: String): Response<Ticket>

    // Payments
    @POST("payments/mpesa/stk-push/")
    suspend fun initiateMpesaPayment(@Body request: PaymentRequest): Response<Payment>

    @POST("payments/mpesa/callback/")
    suspend fun handleMpesaCallback(@Body callback: Map<String, Any>): Response<Unit>

    @GET("payments/{bookingId}/status/")
    suspend fun getPaymentStatus(@Path("bookingId") bookingId: String): Response<Payment>

    // Organizer Endpoints
    @GET("organizer/events/")
    suspend fun getOrganizerEvents(): Response<List<Event>>

    @POST("organizer/events/")
    suspend fun createEvent(@Body event: Map<String, Any>): Response<Event>

    @GET("organizer/events/{id}/stats/")
    suspend fun getEventStats(@Path("id") eventId: String): Response<EventStats>

    @GET("organizer/events/{id}/tickets/")
    suspend fun getEventTickets(@Path("id") eventId: String): Response<List<Ticket>>

    @POST("organizer/events/{id}/checkin/")
    suspend fun checkInByQR(
        @Path("id") eventId: String,
        @Body qrData: Map<String, String>
    ): Response<Ticket>
}

// Generic paginated response
data class PaginatedResponse<T>(
    val count: Int,
    val next: String?,
    val previous: String?,
    val results: List<T>
)

// Event Stats for Organizers
data class EventStats(
    val totalTickets: Int,
    val soldTickets: Int,
    val availableTickets: Int,
    val revenue: Double,
    val checkedIn: Int,
    val tiers: List<TierStat>
)

data class TierStat(
    val tierId: String,
    val tierName: String,
    val total: Int,
    val sold: Int,
    val available: Int,
    val revenue: Double
)

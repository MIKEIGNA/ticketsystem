package com.brightpassticket.data.repository

import com.brightpassticket.api.ApiService
import com.brightpassticket.data.model.*
import okhttp3.ResponseBody
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class BookingRepository @Inject constructor(
    private val apiService: ApiService
) {
    suspend fun createBooking(request: CreateBookingRequest): Result<Booking> {
        return try {
            val response = apiService.createBooking(request)
            if (response.isSuccessful) {
                response.body()?.let {
                    Result.success(it)
                } ?: Result.failure(Exception("Empty response"))
            } else {
                Result.failure(Exception(response.errorBody()?.string() ?: "Failed to create booking"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun getMyBookings(): Result<List<Booking>> {
        return try {
            val response = apiService.getMyBookings()
            if (response.isSuccessful) {
                Result.success(response.body() ?: emptyList())
            } else {
                Result.failure(Exception(response.errorBody()?.string() ?: "Failed to load bookings"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun getBookingDetail(bookingId: String): Result<Booking> {
        return try {
            val response = apiService.getBookingDetail(bookingId)
            if (response.isSuccessful) {
                response.body()?.let {
                    Result.success(it)
                } ?: Result.failure(Exception("Empty response"))
            } else {
                Result.failure(Exception(response.errorBody()?.string() ?: "Failed to load booking"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun getBookingTickets(bookingId: String): Result<List<Ticket>> {
        return try {
            val response = apiService.getBookingTickets(bookingId)
            if (response.isSuccessful) {
                Result.success(response.body() ?: emptyList())
            } else {
                Result.failure(Exception(response.errorBody()?.string() ?: "Failed to load tickets"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun downloadTicket(ticketNumber: String): Result<ResponseBody> {
        return try {
            val response = apiService.downloadTicket(ticketNumber)
            if (response.isSuccessful) {
                response.body()?.let {
                    Result.success(it)
                } ?: Result.failure(Exception("Empty response"))
            } else {
                Result.failure(Exception(response.errorBody()?.string() ?: "Failed to download ticket"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun validateTicket(ticketNumber: String): Result<Ticket> {
        return try {
            val response = apiService.validateTicket(ticketNumber)
            if (response.isSuccessful) {
                response.body()?.let {
                    Result.success(it)
                } ?: Result.failure(Exception("Empty response"))
            } else {
                Result.failure(Exception(response.errorBody()?.string() ?: "Failed to validate ticket"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun checkInTicket(ticketNumber: String): Result<Ticket> {
        return try {
            val response = apiService.checkInTicket(ticketNumber)
            if (response.isSuccessful) {
                response.body()?.let {
                    Result.success(it)
                } ?: Result.failure(Exception("Empty response"))
            } else {
                Result.failure(Exception(response.errorBody()?.string() ?: "Failed to check in"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}

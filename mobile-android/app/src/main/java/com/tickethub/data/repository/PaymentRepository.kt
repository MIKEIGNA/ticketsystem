package com.brightpassticket.data.repository

import com.brightpassticket.api.ApiService
import com.brightpassticket.data.model.Payment
import com.brightpassticket.data.model.PaymentRequest
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class PaymentRepository @Inject constructor(
    private val apiService: ApiService
) {
    suspend fun initiateMpesaPayment(bookingId: String, phoneNumber: String): Result<Payment> {
        return try {
            val response = apiService.initiateMpesaPayment(
                PaymentRequest(bookingId, phoneNumber)
            )
            if (response.isSuccessful) {
                response.body()?.let {
                    Result.success(it)
                } ?: Result.failure(Exception("Empty response"))
            } else {
                Result.failure(Exception(response.errorBody()?.string() ?: "Payment initiation failed"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun getPaymentStatus(bookingId: String): Result<Payment> {
        return try {
            val response = apiService.getPaymentStatus(bookingId)
            if (response.isSuccessful) {
                response.body()?.let {
                    Result.success(it)
                } ?: Result.failure(Exception("Empty response"))
            } else {
                Result.failure(Exception(response.errorBody()?.string() ?: "Failed to get payment status"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}

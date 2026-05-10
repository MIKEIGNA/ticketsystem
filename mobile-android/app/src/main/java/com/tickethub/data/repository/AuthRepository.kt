package com.brightpassticket.data.repository

import com.brightpassticket.api.ApiService
import com.brightpassticket.api.TokenManager
import com.brightpassticket.data.model.*
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.first
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class AuthRepository @Inject constructor(
    private val apiService: ApiService,
    private val tokenManager: TokenManager
) {
    val isLoggedIn: Flow<Boolean> = tokenManager.isLoggedIn
    val currentUser: Flow<User?> = tokenManager.user

    suspend fun login(email: String, password: String): Result<User> {
        return try {
            val response = apiService.login(LoginRequest(email, password))
            if (response.isSuccessful) {
                response.body()?.let { authResponse ->
                    tokenManager.saveTokens(authResponse.access, authResponse.refresh)
                    tokenManager.saveUser(authResponse.user)
                    Result.success(authResponse.user)
                } ?: Result.failure(Exception("Empty response"))
            } else {
                Result.failure(Exception(response.errorBody()?.string() ?: "Login failed"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun register(
        email: String,
        password: String,
        firstName: String,
        lastName: String,
        phoneNumber: String?,
        isOrganizer: Boolean = false
    ): Result<User> {
        return try {
            val response = apiService.register(
                RegisterRequest(
                    email = email,
                    password = password,
                    firstName = firstName,
                    lastName = lastName,
                    phoneNumber = phoneNumber,
                    isOrganizer = isOrganizer
                )
            )
            if (response.isSuccessful) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception(response.errorBody()?.string() ?: "Registration failed"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun logout() {
        try {
            apiService.logout()
        } catch (e: Exception) {
            // Ignore network errors during logout
        } finally {
            tokenManager.clearTokens()
        }
    }

    suspend fun refreshToken(): Result<Unit> {
        return try {
            val refresh = tokenManager.refreshToken.first()
            if (refresh.isNullOrEmpty()) {
                return Result.failure(Exception("No refresh token"))
            }

            val response = apiService.refreshToken(mapOf("refresh" to refresh))
            if (response.isSuccessful) {
                response.body()?.let { authResponse ->
                    tokenManager.saveTokens(authResponse.access, authResponse.refresh)
                    Result.success(Unit)
                } ?: Result.failure(Exception("Empty response"))
            } else {
                Result.failure(Exception("Token refresh failed"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun getCurrentUser(): Result<User> {
        return try {
            val response = apiService.getCurrentUser()
            if (response.isSuccessful) {
                response.body()?.let { user ->
                    tokenManager.saveUser(user)
                    Result.success(user)
                } ?: Result.failure(Exception("Empty response"))
            } else {
                Result.failure(Exception("Failed to get user"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}

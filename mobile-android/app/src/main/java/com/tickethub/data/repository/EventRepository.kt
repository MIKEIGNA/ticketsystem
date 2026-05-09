package com.tickethub.data.repository

import com.tickethub.api.ApiService
import com.tickethub.data.model.Category
import com.tickethub.data.model.Event
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class EventRepository @Inject constructor(
    private val apiService: ApiService
) {
    suspend fun getEvents(
        category: String? = null,
        search: String? = null,
        featured: Boolean? = null,
        upcoming: Boolean? = null,
        page: Int = 1
    ): Result<List<Event>> {
        return try {
            val response = apiService.getEvents(category, search, featured, upcoming, page)
            if (response.isSuccessful) {
                Result.success(response.body()?.results ?: emptyList())
            } else {
                Result.failure(Exception(response.errorBody()?.string() ?: "Failed to load events"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun getCategories(): Result<List<Category>> {
        return try {
            val response = apiService.getCategories()
            if (response.isSuccessful) {
                Result.success(response.body() ?: emptyList())
            } else {
                Result.failure(Exception(response.errorBody()?.string() ?: "Failed to load categories"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun getEventDetail(eventId: String): Result<Event> {
        return try {
            val response = apiService.getEventDetail(eventId)
            if (response.isSuccessful) {
                response.body()?.let {
                    Result.success(it)
                } ?: Result.failure(Exception("Empty response"))
            } else {
                Result.failure(Exception(response.errorBody()?.string() ?: "Failed to load event"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun getEventBySlug(slug: String): Result<Event> {
        return try {
            val response = apiService.getEventBySlug(slug)
            if (response.isSuccessful) {
                response.body()?.let {
                    Result.success(it)
                } ?: Result.failure(Exception("Empty response"))
            } else {
                Result.failure(Exception(response.errorBody()?.string() ?: "Failed to load event"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}

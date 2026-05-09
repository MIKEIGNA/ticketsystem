package com.tickethub.di

import android.content.Context
import com.tickethub.api.RetrofitClient
import com.tickethub.api.TokenManager
import com.tickethub.api.ApiService
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.android.qualifiers.ApplicationContext
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object AppModule {

    @Provides
    @Singleton
    fun provideTokenManager(@ApplicationContext context: Context): TokenManager {
        return TokenManager(context)
    }

    @Provides
    @Singleton
    fun provideRetrofitClient(tokenManager: TokenManager): RetrofitClient {
        return RetrofitClient(tokenManager)
    }

    @Provides
    @Singleton
    fun provideApiService(retrofitClient: RetrofitClient): ApiService {
        return retrofitClient.apiService
    }
}

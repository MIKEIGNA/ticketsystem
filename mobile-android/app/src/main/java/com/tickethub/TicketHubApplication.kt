package com.tickethub

import android.app.Application
import dagger.hilt.android.HiltAndroidApp

@HiltAndroidApp
class TicketHubApplication : Application() {
    override fun onCreate() {
        super.onCreate()
    }
}

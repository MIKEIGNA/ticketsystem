package com.brightpassticket

import android.app.Application
import dagger.hilt.android.HiltAndroidApp

@HiltAndroidApp
class brightpassticketApplication : Application() {
    override fun onCreate() {
        super.onCreate()
    }
}

package com.tickethub.ui.screens.auth

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.hilt.navigation.compose.hiltViewModel
import com.tickethub.ui.theme.PrimaryColor
import com.tickethub.ui.theme.PrimaryDarkColor
import com.tickethub.ui.theme.SecondaryColor
import com.tickethub.ui.viewmodel.AuthViewModel
import kotlinx.coroutines.delay

@Composable
fun SplashScreen(
    viewModel: AuthViewModel = hiltViewModel(),
    onNavigateToHome: () -> Unit,
    onNavigateToLogin: () -> Unit
) {
    var isLoading by remember { mutableStateOf(true) }

    LaunchedEffect(key1 = true) {
        delay(2000) // Show splash for 2 seconds
        
        // Check auth status
        viewModel.checkAuthStatus { isLoggedIn ->
            isLoading = false
            if (isLoggedIn) {
                onNavigateToHome()
            } else {
                onNavigateToLogin()
            }
        }
    }

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(
                brush = Brush.verticalGradient(
                    colors = listOf(PrimaryColor, PrimaryDarkColor)
                )
            ),
        contentAlignment = Alignment.Center
    ) {
        Column(
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            // Logo
            Text(
                text = "Ticket",
                fontSize = 48.sp,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.onPrimary
            )
            Text(
                text = "HUB",
                fontSize = 48.sp,
                fontWeight = FontWeight.ExtraBold,
                color = SecondaryColor
            )
            
            Spacer(modifier = Modifier.height(16.dp))
            
            Text(
                text = "Get Tickets Instantly",
                fontSize = 16.sp,
                color = MaterialTheme.colorScheme.onPrimary.copy(alpha = 0.8f)
            )
            
            Spacer(modifier = Modifier.height(32.dp))
            
            if (isLoading) {
                CircularProgressIndicator(
                    color = MaterialTheme.colorScheme.onPrimary,
                    modifier = Modifier.size(32.dp)
                )
            }
        }
    }
}

package com.brightpassticket

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.viewModels
import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.tooling.preview.Preview
import androidx.navigation.NavDestination.Companion.hierarchy
import androidx.navigation.NavGraph.Companion.findStartDestination
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import androidx.navigation.navArgument
import com.brightpassticket.navigation.Screen
import com.brightpassticket.ui.screens.auth.LoginScreen
import com.brightpassticket.ui.screens.auth.RegisterScreen
import com.brightpassticket.ui.screens.auth.SplashScreen
import com.brightpassticket.ui.screens.booking.BookingScreen
import com.brightpassticket.ui.screens.booking.PaymentScreen
import com.brightpassticket.ui.screens.booking.BookingSuccessScreen
import com.brightpassticket.ui.screens.events.EventDetailScreen
import com.brightpassticket.ui.screens.events.EventsScreen
import com.brightpassticket.ui.screens.events.SearchScreen
import com.brightpassticket.ui.screens.home.HomeScreen
import com.brightpassticket.ui.screens.organizer.OrganizerDashboardScreen
import com.brightpassticket.ui.screens.organizer.CheckInScreen
import com.brightpassticket.ui.screens.profile.ProfileScreen
import com.brightpassticket.ui.screens.tickets.MyTicketsScreen
import com.brightpassticket.ui.screens.tickets.TicketDetailScreen
import com.brightpassticket.ui.theme.brightpassticketTheme
import com.brightpassticket.ui.viewmodel.AuthViewModel
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class MainActivity : ComponentActivity() {

    private val authViewModel: AuthViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            brightpassticketTheme {
                MainApp(authViewModel)
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MainApp(authViewModel: AuthViewModel) {
    val navController = rememberNavController()
    val navBackStackEntry by navController.currentBackStackEntryAsState()
    val currentDestination = navBackStackEntry?.destination

    // Check if current screen should show bottom nav
    val showBottomNav = when (currentDestination?.route) {
        Screen.Home.route,
        Screen.Events.route,
        Screen.Search.route,
        Screen.MyTickets.route,
        Screen.Profile.route -> true
        else -> false
    }

    Scaffold(
        bottomBar = {
            if (showBottomNav) {
                NavigationBar {
                    val items = listOf(
                        Triple(Screen.Home, "Home", Icons.Default.Home),
                        Triple(Screen.Events, "Events", Icons.Default.Event),
                        Triple(Screen.Search, "Search", Icons.Default.Search),
                        Triple(Screen.MyTickets, "Tickets", Icons.Default.ConfirmationNumber),
                        Triple(Screen.Profile, "Profile", Icons.Default.Person)
                    )
                    items.forEach { (screen, label, icon) ->
                        NavigationBarItem(
                            icon = { Icon(icon, contentDescription = label) },
                            label = { Text(label) },
                            selected = currentDestination?.hierarchy?.any { it.route == screen.route } == true,
                            onClick = {
                                navController.navigate(screen.route) {
                                    popUpTo(navController.graph.findStartDestination().id) {
                                        saveState = true
                                    }
                                    launchSingleTop = true
                                    restoreState = true
                                }
                            }
                        )
                    }
                }
            }
        }
    ) { innerPadding ->
        NavHost(
            navController = navController,
            startDestination = Screen.Splash.route,
            modifier = Modifier.padding(innerPadding)
        ) {
            // Auth
            composable(Screen.Splash.route) {
                SplashScreen(
                    viewModel = authViewModel,
                    onNavigateToHome = {
                        navController.navigate(Screen.Home.route) {
                            popUpTo(Screen.Splash.route) { inclusive = true }
                        }
                    },
                    onNavigateToLogin = {
                        navController.navigate(Screen.Login.route) {
                            popUpTo(Screen.Splash.route) { inclusive = true }
                        }
                    }
                )
            }
            composable(Screen.Login.route) {
                LoginScreen(
                    viewModel = authViewModel,
                    onNavigateToHome = {
                        navController.navigate(Screen.Home.route) {
                            popUpTo(Screen.Login.route) { inclusive = true }
                        }
                    },
                    onNavigateToRegister = {
                        navController.navigate(Screen.Register.route)
                    }
                )
            }
            composable(Screen.Register.route) {
                RegisterScreen(
                    viewModel = authViewModel,
                    onNavigateToHome = {
                        navController.navigate(Screen.Home.route) {
                            popUpTo(Screen.Register.route) { inclusive = true }
                        }
                    },
                    onNavigateToLogin = {
                        navController.navigateUp()
                    }
                )
            }

            // Main
            composable(Screen.Home.route) {
                HomeScreen(
                    onEventClick = { eventId ->
                        navController.navigate(Screen.EventDetail.createRoute(eventId))
                    },
                    onViewAllEvents = {
                        navController.navigate(Screen.Events.route)
                    },
                    onViewAllCategories = {
                        navController.navigate(Screen.Events.route)
                    }
                )
            }
            composable(Screen.Events.route) {
                EventsScreen(
                    onEventClick = { eventId ->
                        navController.navigate(Screen.EventDetail.createRoute(eventId))
                    },
                    onBack = { navController.navigateUp() }
                )
            }
            composable(
                route = Screen.EventDetail.route,
                arguments = listOf(navArgument("eventId") { type = NavType.StringType })
            ) { backStackEntry ->
                val eventId = backStackEntry.arguments?.getString("eventId") ?: ""
                EventDetailScreen(
                    eventId = eventId,
                    onBack = { navController.navigateUp() },
                    onBookTicket = { eventId, tierId, quantity ->
                        navController.navigate(Screen.Booking.createRoute(eventId, tierId, quantity))
                    }
                )
            }
            composable(Screen.Search.route) {
                SearchScreen(
                    onEventClick = { eventId ->
                        navController.navigate(Screen.EventDetail.createRoute(eventId))
                    }
                )
            }

            // Booking
            composable(
                route = Screen.Booking.route,
                arguments = listOf(
                    navArgument("eventId") { type = NavType.StringType },
                    navArgument("tierId") { type = NavType.StringType },
                    navArgument("quantity") { type = NavType.IntType }
                )
            ) { backStackEntry ->
                val eventId = backStackEntry.arguments?.getString("eventId") ?: ""
                val tierId = backStackEntry.arguments?.getString("tierId") ?: ""
                val quantity = backStackEntry.arguments?.getInt("quantity") ?: 1
                BookingScreen(
                    eventId = eventId,
                    tierId = tierId,
                    quantity = quantity,
                    onBack = { navController.navigateUp() },
                    onBookingCreated = { bookingId, amount ->
                        navController.navigate(Screen.Payment.createRoute(bookingId, amount))
                    }
                )
            }
            composable(
                route = Screen.Payment.route,
                arguments = listOf(
                    navArgument("bookingId") { type = NavType.StringType },
                    navArgument("amount") { type = NavType.StringType }
                )
            ) { backStackEntry ->
                val bookingId = backStackEntry.arguments?.getString("bookingId") ?: ""
                val amount = backStackEntry.arguments?.getString("amount")?.toDoubleOrNull() ?: 0.0
                PaymentScreen(
                    bookingId = bookingId,
                    amount = amount,
                    onBack = { navController.navigateUp() },
                    onPaymentSuccess = {
                        navController.navigate(Screen.BookingSuccess.createRoute(bookingId)) {
                            popUpTo(Screen.Home.route) { inclusive = false }
                        }
                    }
                )
            }
            composable(
                route = Screen.BookingSuccess.route,
                arguments = listOf(navArgument("bookingId") { type = NavType.StringType })
            ) { backStackEntry ->
                val bookingId = backStackEntry.arguments?.getString("bookingId") ?: ""
                BookingSuccessScreen(
                    bookingId = bookingId,
                    onViewTickets = {
                        navController.navigate(Screen.MyTickets.route) {
                            popUpTo(Screen.Home.route)
                        }
                    },
                    onBackToHome = {
                        navController.navigate(Screen.Home.route) {
                            popUpTo(Screen.Home.route) { inclusive = true }
                        }
                    }
                )
            }

            // Tickets
            composable(Screen.MyTickets.route) {
                MyTicketsScreen(
                    onTicketClick = { ticketNumber ->
                        navController.navigate(Screen.TicketDetail.createRoute(ticketNumber))
                    }
                )
            }
            composable(
                route = Screen.TicketDetail.route,
                arguments = listOf(navArgument("ticketNumber") { type = NavType.StringType })
            ) { backStackEntry ->
                val ticketNumber = backStackEntry.arguments?.getString("ticketNumber") ?: ""
                TicketDetailScreen(
                    ticketNumber = ticketNumber,
                    onBack = { navController.navigateUp() }
                )
            }

            // Organizer
            composable(Screen.OrganizerDashboard.route) {
                OrganizerDashboardScreen(
                    onCreateEvent = {
                        // Navigate to create event
                    },
                    onViewEventStats = { eventId ->
                        navController.navigate(Screen.EventStats.createRoute(eventId))
                    },
                    onCheckIn = { eventId ->
                        navController.navigate(Screen.CheckIn.createRoute(eventId))
                    }
                )
            }
            composable(
                route = Screen.CheckIn.route,
                arguments = listOf(navArgument("eventId") { type = NavType.StringType })
            ) { backStackEntry ->
                val eventId = backStackEntry.arguments?.getString("eventId") ?: ""
                CheckInScreen(
                    eventId = eventId,
                    onBack = { navController.navigateUp() }
                )
            }

            // Profile
            composable(Screen.Profile.route) {
                ProfileScreen(
                    viewModel = authViewModel,
                    onLogout = {
                        navController.navigate(Screen.Login.route) {
                            popUpTo(0) { inclusive = true }
                        }
                    },
                    onEditProfile = {
                        navController.navigate(Screen.EditProfile.route)
                    },
                    onOrganizerDashboard = {
                        navController.navigate(Screen.OrganizerDashboard.route)
                    }
                )
            }
        }
    }
}

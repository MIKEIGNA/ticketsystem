package com.brightpassticket.ui.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.brightpassticket.data.model.User
import com.brightpassticket.data.repository.AuthRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class AuthViewModel @Inject constructor(
    private val authRepository: AuthRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow<AuthUiState>(AuthUiState.Initial)
    val uiState: StateFlow<AuthUiState> = _uiState.asStateFlow()

    private val _currentUser = MutableStateFlow<User?>(null)
    val currentUser: StateFlow<User?> = _currentUser.asStateFlow()

    fun checkAuthStatus(onResult: (Boolean) -> Unit) {
        viewModelScope.launch {
            authRepository.isLoggedIn.collect { isLoggedIn ->
                if (isLoggedIn) {
                    // Refresh user data
                    authRepository.getCurrentUser()
                    authRepository.currentUser.collect { user ->
                        _currentUser.value = user
                        onResult(true)
                    }
                } else {
                    onResult(false)
                }
            }
        }
    }

    fun login(email: String, password: String) {
        viewModelScope.launch {
            _uiState.value = AuthUiState.Loading
            
            authRepository.login(email, password)
                .onSuccess { user ->
                    _currentUser.value = user
                    _uiState.value = AuthUiState.Success(user)
                }
                .onFailure { error ->
                    _uiState.value = AuthUiState.Error(error.message ?: "Login failed")
                }
        }
    }

    fun register(
        email: String,
        password: String,
        firstName: String,
        lastName: String,
        phoneNumber: String?,
        isOrganizer: Boolean = false
    ) {
        viewModelScope.launch {
            _uiState.value = AuthUiState.Loading
            
            authRepository.register(email, password, firstName, lastName, phoneNumber, isOrganizer)
                .onSuccess { user ->
                    _uiState.value = AuthUiState.RegisterSuccess(user)
                }
                .onFailure { error ->
                    _uiState.value = AuthUiState.Error(error.message ?: "Registration failed")
                }
        }
    }

    fun logout() {
        viewModelScope.launch {
            authRepository.logout()
            _currentUser.value = null
            _uiState.value = AuthUiState.Initial
        }
    }

    fun resetState() {
        _uiState.value = AuthUiState.Initial
    }
}

sealed class AuthUiState {
    object Initial : AuthUiState()
    object Loading : AuthUiState()
    data class Success(val user: User) : AuthUiState()
    data class RegisterSuccess(val user: User) : AuthUiState()
    data class Error(val message: String) : AuthUiState()
}

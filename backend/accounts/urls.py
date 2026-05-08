from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    UserRegisterView,
    UserProfileView,
    UserDetailView,
    OrganizerListView,
    CustomTokenObtainPairView
)

urlpatterns = [
    # Authentication
    path('register/', UserRegisterView.as_view(), name='user-register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='user-login'),
    path('refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    
    # User Management
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('users/<uuid:id>/', UserDetailView.as_view(), name='user-detail'),
    path('organizers/', OrganizerListView.as_view(), name='organizer-list'),
]

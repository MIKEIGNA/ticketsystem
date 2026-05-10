from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.permissions import AllowAny

from .views import (
    UserRegisterView,
    UserProfileView,
    UserDetailView,
    OrganizerListView,
    CustomTokenObtainPairView
)

# Create a TokenRefreshView with AllowAny permission
class TokenRefreshViewPublic(TokenRefreshView):
    permission_classes = [AllowAny]

urlpatterns = [
    # Authentication
    path('register/', UserRegisterView.as_view(), name='user-register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshViewPublic.as_view(), name='token_refresh'),
    
    # User Management
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('users/<uuid:id>/', UserDetailView.as_view(), name='user-detail'),
    path('organizers/', OrganizerListView.as_view(), name='organizer-list'),
]

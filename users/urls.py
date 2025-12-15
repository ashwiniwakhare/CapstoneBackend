# urls.py
from django.urls import path
from .views import RegisterView, CustomTokenObtainPairView, MeView

# User authentication and profile endpoints
urlpatterns = [
    # Endpoint to register a new user
    path('register/', RegisterView.as_view(), name='auth_register'),

    # JWT token endpoint: obtain access and refresh tokens
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),

    # Endpoint to get details of the currently logged-in user
    path('me/', MeView.as_view(), name='auth_me'),
]

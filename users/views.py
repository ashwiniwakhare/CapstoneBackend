# views.py
from rest_framework import generics, permissions
from .serializers import RegisterSerializer, UserSerializer
from .models import User
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


# ---------------------------------------------------------
# CUSTOM JWT TOKEN SERIALIZER
# ---------------------------------------------------------
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT serializer that adds user-specific info to the token payload.
    Adds 'role' and 'username' to the JWT token.
    """
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role
        token['username'] = user.username
        return token


# ---------------------------------------------------------
# CUSTOM JWT TOKEN VIEW
# ---------------------------------------------------------
class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Overrides the default token view to use the custom serializer.
    """
    serializer_class = CustomTokenObtainPairSerializer


# ---------------------------------------------------------
# USER REGISTRATION VIEW
# ---------------------------------------------------------
class RegisterView(generics.CreateAPIView):
    """
    API endpoint for registering new users.
    Open to anyone (AllowAny permission).
    """
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer


# ---------------------------------------------------------
# CURRENT USER PROFILE VIEW
# ---------------------------------------------------------
class MeView(generics.RetrieveAPIView):
    """
    API endpoint to retrieve details of the currently logged-in user.
    """
    serializer_class = UserSerializer

    def get_object(self):
        # Returns the authenticated user
        return self.request.user

# serializers.py
from rest_framework import serializers
from .models import User

# Serializer for general User data retrieval
class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for displaying User data.
    Returns id, username, email, first_name, last_name, and role.
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role']


# Serializer for user registration
class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new user.
    Handles password write-only and role assignment.
    """
    password = serializers.CharField(write_only=True)  # Ensures password is never sent in API responses

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'role']

    def create(self, validated_data):
        """
        Overrides create method to use `create_user` for proper password hashing.
        Assigns role with default as 'user' if not provided.
        """
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email'),
            password=validated_data['password'],
            role=validated_data.get('role', 'user')
        )
        return user

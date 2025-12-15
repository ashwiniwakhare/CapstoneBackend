# models.py
from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """
    Custom user model extending Django's AbstractUser.
    Adds a 'role' field to differentiate user types in the system.
    """
    ROLE_CHOICES = (
        ('admin', 'Admin'),   # Full access
        ('agent', 'Agent'),   # Support agent role
        ('user', 'User')      # Regular end user
    )
    
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='user'  # Default role assigned to new users
    )

    def __str__(self):
        # Display username along with role for easy identification
        return f"{self.username} ({self.role})"

# apps.py
from django.apps import AppConfig

class UsersConfig(AppConfig):
    """
    Configuration for the 'users' app.
    - 'default_auto_field' sets the type of primary key for models in this app.
    - 'name' specifies the full Python path to the app.
    """
    default_auto_field = 'django.db.models.BigAutoField'  # Use BigAutoField for primary keys
    name = 'users'  # App name used by Django to reference this app

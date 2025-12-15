# Import AppConfig from Django to configure the app settings
from django.apps import AppConfig

class TicketsConfig(AppConfig):
    """
    App configuration class for the 'tickets' application.
    Django uses this class during startup to register the app.
    """

    # Defines the default primary key field type for models in this app
    default_auto_field = 'django.db.models.BigAutoField'

    # Name of the app (must match the app folder name)
    name = 'tickets'

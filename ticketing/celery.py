import os
from celery import Celery

# Set default Django settings for Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ticketing.settings')

# Create Celery application instance
app = Celery('ticketing')

# Load Celery configuration from Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Automatically discover tasks from all Django apps
app.autodiscover_tasks()

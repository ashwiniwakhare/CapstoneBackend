# DRF router to automatically generate CRUD endpoints for ViewSets
from rest_framework.routers import DefaultRouter

# Django URL utilities to define paths and include other URL patterns
from django.urls import path, include

# Importing views:
# - TicketViewSet & CategoryViewSet: CRUD operations for tickets and categories
# - TicketListView: Custom filtered ticket list view
# - TicketAnalyticsView: Analytics endpoint for dashboard
# - trigger_tfidf_ranking: Custom function to run TF-IDF ranking
from .views import (
    TicketViewSet,
    CategoryViewSet,
    TicketListView,
    TicketAnalyticsView,
    trigger_tfidf_ranking
)

# Initialize DRF router
router = DefaultRouter()
router.register(r'tickets', TicketViewSet, basename='tickets')
router.register(r'categories', CategoryViewSet, basename='categories')

# Define URL patterns
urlpatterns = [
    # Custom analytics endpoint (placed first to avoid router override)
    path('tickets/analytics/', TicketAnalyticsView.as_view(), name='tickets-analytics'),

    # Custom ticket list view with optional filters (e.g., ?mine=true)
    path('tickets/list/', TicketListView.as_view(), name='tickets-list'),

    # Custom endpoint to trigger TF-IDF ranking for tickets
    path('tickets/run-tfidf/', trigger_tfidf_ranking, name='run-tfidf'),

    # Include router-generated CRUD endpoints for tickets and categories
    path('', include(router.urls)),
]

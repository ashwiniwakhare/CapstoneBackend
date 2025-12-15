from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Main URL configuration of the project
urlpatterns = [
    # Django admin panel
    path('admin/', admin.site.urls),

    # Authentication APIs (login, register, JWT, etc.)
    path('api/auth/', include('users.urls')),

    # Ticketing system APIs (CRUD, analytics, background tasks)
    path('api/tickets/', include('tickets.urls')),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )

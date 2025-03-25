"""
URL Configuration for Financial Mediator project.

This module contains the root URL configurations for the project.
It includes:
- Admin interface URLs
- API endpoints
- API documentation
- Health check endpoints
- Monitoring endpoints
"""

from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)
from django.conf import settings

# Define URL patterns for the entire project
urlpatterns = [
    # Django Admin Interface
    path("admin/", admin.site.urls),

    # API Endpoints
    path("api/v1/", include("api.urls")),  # Core API endpoints
    path("api/v1/providers/", include("providers.urls")),  # Provider-related endpoints
    path("api/v1/banking/", include("banking.urls")),  # Banking-related endpoints

    # API Documentation - OpenAPI Schema
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    # Swagger UI
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    # ReDoc UI (alternative to Swagger)
    path(
        "api/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
]

# Add debug toolbar URLs in development
if settings.DEBUG:
    try:
        import debug_toolbar
        urlpatterns.append(
            path("__debug__/", include(debug_toolbar.urls))
        )
    except ImportError:
        pass

# Add Prometheus monitoring endpoints
urlpatterns.append(
    path("", include("django_prometheus.urls"))
)

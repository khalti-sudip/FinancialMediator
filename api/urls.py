"""URL Configuration for the API app."""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

# Import views
from .views import health, auth

# Create a router and register our viewsets
router = DefaultRouter()

urlpatterns = [
    # API Documentation
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
    
    # Health Checks
    path("health/", health.HealthCheckView.as_view(), name="health_check"),
    path("health/db/", health.DatabaseHealthView.as_view(), name="db_health"),
    path("health/redis/", health.RedisHealthView.as_view(), name="redis_health"),
    
    # Authentication
    path("auth/token/", auth.TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", auth.TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/token/verify/", auth.TokenVerifyView.as_view(), name="token_verify"),
    
    # Include router URLs
    path("", include(router.urls)),
    
    # Include providers URLs
    path("providers/", include("providers.urls")),
    
    # Include banking URLs
    path("banking/", include("banking.urls")),
]

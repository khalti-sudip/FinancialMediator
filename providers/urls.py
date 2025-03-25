"""URL patterns for the providers app."""

from django.urls import path, include
from rest_framework_nested import routers
from .views import ProviderViewSet, ProviderEndpointViewSet, ProviderCredentialViewSet

# Create a router for providers
router = routers.DefaultRouter()
router.register(r"", ProviderViewSet, basename="provider")

# Create nested routers for endpoints and credentials
provider_router = routers.NestedDefaultRouter(router, r"", lookup="provider")
provider_router.register(
    r"endpoints", ProviderEndpointViewSet, basename="provider-endpoint"
)
provider_router.register(
    r"credentials", ProviderCredentialViewSet, basename="provider-credential"
)

urlpatterns = [
    path("", include(router.urls)),
    path("", include(provider_router.urls)),
]

"""URL patterns for the providers app."""

from django.urls import path, include
from rest_framework_nested import routers
from .views import ProviderViewSet, ProviderKeyViewSet, ProviderWebhookViewSet

# Create a router for providers
router = routers.DefaultRouter()
router.register(r"", ProviderViewSet, basename="provider")

# Create nested routers for keys and webhooks
provider_router = routers.NestedDefaultRouter(router, r"", lookup="provider")
provider_router.register(
    r"keys", ProviderKeyViewSet, basename="provider-key"
)
provider_router.register(
    r"webhooks", ProviderWebhookViewSet, basename="provider-webhook"
)

urlpatterns = [
    path("", include(router.urls)),
    path("", include(provider_router.urls)),
]

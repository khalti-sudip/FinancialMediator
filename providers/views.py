"""Views for the providers app."""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django_filters import rest_framework as filters
from drf_spectacular.utils import extend_schema, OpenApiParameter

from .models import Provider, ProviderEndpoint, ProviderCredential
from .serializers import (
    ProviderSerializer,
    ProviderEndpointSerializer,
    ProviderCredentialSerializer,
)
from api.middleware.request_tracking import track_request
from api.middleware.rate_limiter import rate_limit


class ProviderFilter(filters.FilterSet):
    """Filter set for Provider model."""

    status = filters.ChoiceFilter(choices=Provider._meta.get_field("status").choices)
    created_after = filters.DateTimeFilter(field_name="created_at", lookup_expr="gte")
    created_before = filters.DateTimeFilter(field_name="created_at", lookup_expr="lte")

    class Meta:
        """Meta options for ProviderFilter."""

        model = Provider
        fields = ["status", "created_after", "created_before"]


class ProviderViewSet(viewsets.ModelViewSet):
    """ViewSet for managing providers."""

    queryset = Provider.objects.all()
    serializer_class = ProviderSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = ProviderFilter

    @track_request
    def list(self, request, *args, **kwargs):
        """List all providers."""
        return super().list(request, *args, **kwargs)

    @track_request
    def create(self, request, *args, **kwargs):
        """Create a new provider."""
        return super().create(request, *args, **kwargs)

    @track_request
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="provider_id",
                type=int,
                location=OpenApiParameter.PATH,
                description="Provider ID",
            )
        ]
    )
    @action(detail=True, methods=["post"])
    @rate_limit(requests=10, duration=60)
    def test_connection(self, request, pk=None):
        """Test the connection to a provider."""
        provider = self.get_object()
        try:
            # Implement provider connection test logic here
            return Response({"status": "success", "message": "Connection successful"})
        except Exception as e:
            return Response(
                {"status": "error", "message": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ProviderEndpointViewSet(viewsets.ModelViewSet):
    """ViewSet for managing provider endpoints."""

    serializer_class = ProviderEndpointSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Get the queryset for provider endpoints."""
        provider_id = self.kwargs.get("provider_pk")
        if provider_id is None:
            return ProviderEndpoint.objects.none()
        return ProviderEndpoint.objects.filter(provider_id=provider_id)

    def perform_create(self, serializer):
        """Create a new provider endpoint."""
        provider = get_object_or_404(Provider, pk=self.kwargs.get("provider_pk"))
        serializer.save(provider=provider)


class ProviderCredentialViewSet(viewsets.ModelViewSet):
    """ViewSet for managing provider credentials."""

    serializer_class = ProviderCredentialSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Get the queryset for provider credentials."""
        provider_id = self.kwargs.get("provider_pk")
        if provider_id is None:
            return ProviderCredential.objects.none()
        return ProviderCredential.objects.filter(provider_id=provider_id)

    def perform_create(self, serializer):
        """Create a new provider credential."""
        provider = get_object_or_404(Provider, pk=self.kwargs.get("provider_pk"))
        serializer.save(provider=provider)

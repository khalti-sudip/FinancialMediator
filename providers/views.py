"""Views for the providers app."""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django_filters import rest_framework as filters
from drf_spectacular.utils import extend_schema, OpenApiParameter

from .models import Provider, ProviderKey, ProviderWebhook
from .serializers import (
    ProviderSerializer,
    ProviderKeySerializer,
    ProviderWebhookSerializer,
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
    @rate_limit()
    def list(self, request, *args, **kwargs):
        """List all providers."""
        return super().list(request, *args, **kwargs)

    @track_request
    @rate_limit()
    def create(self, request, *args, **kwargs):
        """Create a new provider."""
        return super().create(request, *args, **kwargs)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="pk",
                type={"type": "integer"},
                location=OpenApiParameter.PATH,
                description="Provider ID",
            ),
        ],
        responses={200: {"type": "object", "properties": {"status": {"type": "string"}}}},
    )
    @action(detail=True, methods=["post"])
    @track_request
    @rate_limit()
    def test_connection(self, request, pk=None):
        """Test the connection to a provider."""
        provider = self.get_object()
        
        try:
            # Implementation for testing connection
            # This would typically call a service method
            connected = True
            message = "Connection successful"
        except Exception as e:
            connected = False
            message = str(e)
        
        return Response(
            {"status": "success" if connected else "error", "message": message},
            status=status.HTTP_200_OK if connected else status.HTTP_400_BAD_REQUEST,
        )


class ProviderKeyViewSet(viewsets.ModelViewSet):
    """ViewSet for managing provider keys."""

    serializer_class = ProviderKeySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Get the queryset for provider keys."""
        provider_pk = self.kwargs.get("provider_pk")
        return ProviderKey.objects.filter(provider_id=provider_pk)

    def perform_create(self, serializer):
        """Create a new provider key."""
        provider_pk = self.kwargs.get("provider_pk")
        provider = get_object_or_404(Provider, pk=provider_pk)
        serializer.save(provider=provider, user=self.request.user)


class ProviderWebhookViewSet(viewsets.ModelViewSet):
    """ViewSet for managing provider webhooks."""

    serializer_class = ProviderWebhookSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Get the queryset for provider webhooks."""
        provider_pk = self.kwargs.get("provider_pk")
        return ProviderWebhook.objects.filter(provider_id=provider_pk)

    def perform_create(self, serializer):
        """Create a new provider webhook."""
        provider_pk = self.kwargs.get("provider_pk")
        provider = get_object_or_404(Provider, pk=provider_pk)
        serializer.save(provider=provider)

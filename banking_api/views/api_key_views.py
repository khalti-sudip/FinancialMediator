from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
import uuid
import secrets

from banking_api.models.api_key import ApiKey
from banking_api.models.audit_log import AuditLog
from banking_api.serializers.api_key_serializer import ApiKeySerializer


class ApiKeyViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing API keys.
    """

    queryset = ApiKey.objects.all()
    serializer_class = ApiKeySerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["provider_type", "is_active"]
    search_fields = ["name", "provider_type"]
    ordering_fields = ["id", "name", "created_at", "expires_at"]
    ordering = ["-created_at"]

    def perform_create(self, serializer):
        """Create a new API key with auto-generated values if not provided"""
        # Generate key_value if not provided
        if "key_value" not in serializer.validated_data:
            serializer.validated_data["key_value"] = f"api_{uuid.uuid4().hex}"

        api_key = serializer.save()

        # Log API key creation
        AuditLog.log_action(
            action="create",
            resource_type="api_key",
            resource_id=str(api_key.id),
            user=self.request.user,
            ip_address=self._get_client_ip(self.request),
        )

    def perform_update(self, serializer):
        """Update an API key and log the action"""
        api_key = serializer.save()

        # Log API key update
        AuditLog.log_action(
            action="update",
            resource_type="api_key",
            resource_id=str(api_key.id),
            user=self.request.user,
            ip_address=self._get_client_ip(self.request),
        )

    def perform_destroy(self, instance):
        """Delete an API key and log the action"""
        api_key_id = instance.id

        # Log API key deletion
        AuditLog.log_action(
            action="delete",
            resource_type="api_key",
            resource_id=str(api_key_id),
            user=self.request.user,
            ip_address=self._get_client_ip(self.request),
        )

        instance.delete()

    @action(detail=True, methods=["post"])
    def regenerate(self, request, pk=None):
        """
        Regenerate the API key value
        """
        api_key = self.get_object()

        # Generate new key value
        api_key.key_value = f"api_{uuid.uuid4().hex}"

        # Generate new secret if it was previously set
        if api_key.secret_value:
            api_key.secret_value = secrets.token_urlsafe(32)

        api_key.save()

        # Log API key regeneration
        AuditLog.log_action(
            action="update",
            resource_type="api_key",
            resource_id=str(api_key.id),
            user=request.user,
            details="API key regenerated",
            ip_address=self._get_client_ip(request),
        )

        serializer = self.get_serializer(api_key)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def toggle_active(self, request, pk=None):
        """
        Toggle the active status of an API key
        """
        api_key = self.get_object()

        # Toggle is_active
        api_key.is_active = not api_key.is_active
        api_key.save()

        action_details = (
            f"API key {'activated' if api_key.is_active else 'deactivated'}"
        )

        # Log status change
        AuditLog.log_action(
            action="update",
            resource_type="api_key",
            resource_id=str(api_key.id),
            user=request.user,
            details=action_details,
            ip_address=self._get_client_ip(request),
        )

        serializer = self.get_serializer(api_key)
        return Response(serializer.data)

    def _get_client_ip(self, request):
        """Get the client IP address from request"""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip

from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
import requests

from banking_api.models.system_config import SystemConfig
from banking_api.models.audit_log import AuditLog
from banking_api.serializers.system_config_serializer import SystemConfigSerializer


class SystemConfigViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing system configurations.
    """

    queryset = SystemConfig.objects.all()
    serializer_class = SystemConfigSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["system_type", "is_active", "auth_type"]
    search_fields = ["system_name", "base_url"]
    ordering_fields = ["id", "system_name", "created_at", "updated_at"]
    ordering = ["-created_at"]

    def perform_create(self, serializer):
        """Create a new system configuration and log the action"""
        system_config = serializer.save()

        # Log system config creation
        AuditLog.log_action(
            action="create",
            resource_type="system_config",
            resource_id=str(system_config.id),
            user=self.request.user,
            ip_address=self._get_client_ip(self.request),
        )

    def perform_update(self, serializer):
        """Update a system configuration and log the action"""
        system_config = serializer.save()

        # Log system config update
        AuditLog.log_action(
            action="update",
            resource_type="system_config",
            resource_id=str(system_config.id),
            user=self.request.user,
            ip_address=self._get_client_ip(self.request),
        )

    def perform_destroy(self, instance):
        """Delete a system configuration and log the action"""
        system_config_id = instance.id

        # Log system config deletion
        AuditLog.log_action(
            action="delete",
            resource_type="system_config",
            resource_id=str(system_config_id),
            user=self.request.user,
            ip_address=self._get_client_ip(self.request),
        )

        instance.delete()

    @action(detail=True, methods=["post"])
    def test_connection(self, request, pk=None):
        """
        Test the connection to the configured system
        """
        system_config = self.get_object()

        # Get the test endpoint from request data or use default
        test_endpoint = request.data.get("test_endpoint", "/status")
        timeout = system_config.timeout

        try:
            # Prepare URL and headers
            url = f"{system_config.base_url.rstrip('/')}{test_endpoint}"
            headers = system_config.get_auth_headers()

            # Make a request to the system
            response = requests.get(url, headers=headers, timeout=timeout)

            # Log the test action
            AuditLog.log_action(
                action="api_request",
                resource_type="system_config",
                resource_id=str(system_config.id),
                user=request.user,
                details=f"Test connection: {response.status_code}",
                ip_address=self._get_client_ip(request),
            )

            # Return the result
            if response.status_code < 400:
                return Response(
                    {
                        "success": True,
                        "status_code": response.status_code,
                        "message": "Connection successful",
                        "data": response.json() if self._is_json(response) else None,
                    }
                )
            else:
                return Response(
                    {
                        "success": False,
                        "status_code": response.status_code,
                        "message": "Connection failed with HTTP error",
                        "data": response.json() if self._is_json(response) else None,
                    },
                    status=status.HTTP_200_OK,
                )  # Return 200 even for failed connections

        except requests.exceptions.Timeout:
            return Response(
                {
                    "success": False,
                    "message": f"Connection timed out after {timeout} seconds",
                },
                status=status.HTTP_200_OK,
            )

        except requests.exceptions.RequestException as e:
            return Response(
                {"success": False, "message": f"Connection error: {str(e)}"},
                status=status.HTTP_200_OK,
            )

    @action(detail=True, methods=["post"])
    def toggle_active(self, request, pk=None):
        """
        Toggle the active status of a system configuration
        """
        system_config = self.get_object()

        # Toggle is_active
        system_config.is_active = not system_config.is_active
        system_config.save()

        action_details = (
            f"System config {'activated' if system_config.is_active else 'deactivated'}"
        )

        # Log status change
        AuditLog.log_action(
            action="update",
            resource_type="system_config",
            resource_id=str(system_config.id),
            user=request.user,
            details=action_details,
            ip_address=self._get_client_ip(request),
        )

        serializer = self.get_serializer(system_config)
        return Response(serializer.data)

    def _get_client_ip(self, request):
        """Get the client IP address from request"""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip

    def _is_json(self, response):
        """Check if the response is JSON"""
        try:
            response.json()
            return True
        except ValueError:
            return False

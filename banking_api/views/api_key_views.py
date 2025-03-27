from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from banking_api.models.api_key import ApiKey
from banking_api.models.audit_log import AuditLog
from banking_api.serializers.api_key_serializer import ApiKeySerializer
from banking_api.services.api_key_service import APIKeyService
from banking_api.services.audit_log_service import AuditLogService
from banking_api.exceptions import APIKeyError
import uuid
import secrets

class ApiKeyViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing API keys.
    
    This viewset handles all API key operations using the APIKeyService.
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
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api_key_service = APIKeyService()
        self.audit_log_service = AuditLogService()
    
    def perform_create(self, serializer):
        """
        Create a new API key with auto-generated values if not provided
        
        Uses the APIKeyService to handle API key generation and validation.
        """
        try:
            # Generate key_value if not provided
            if "key_value" not in serializer.validated_data:
                serializer.validated_data["key_value"] = f"api_{uuid.uuid4().hex}"
            
            api_key = self.api_key_service.generate_api_key(
                user_id=self.request.user.id,
                name=serializer.validated_data["name"],
                provider_type=serializer.validated_data.get("provider_type", "")
            )
            
            # Log API key creation
            self.audit_log_service.create_audit_log(
                user_id=self.request.user.id,
                action="API_KEY_CREATE",
                details={
                    "api_key_id": str(api_key.id),
                    "name": api_key.name,
                    "provider_type": api_key.provider_type
                },
                ip_address=self._get_client_ip(self.request),
                user_agent=self.request.META.get('HTTP_USER_AGENT')
            )
            
            return api_key
        except APIKeyError as e:
            raise serializers.ValidationError(str(e))
    
    def perform_update(self, serializer):
        """
        Update an API key and log the action
        
        Uses the APIKeyService to handle API key updates.
        """
        try:
            api_key = serializer.save()
            
            # Update using service
            self.api_key_service.update_api_key(
                api_key.id,
                **serializer.validated_data
            )
            
            # Log API key update
            self.audit_log_service.create_audit_log(
                user_id=self.request.user.id,
                action="API_KEY_UPDATE",
                details={
                    "api_key_id": str(api_key.id),
                    "name": api_key.name,
                    "provider_type": api_key.provider_type
                },
                ip_address=self._get_client_ip(self.request),
                user_agent=self.request.META.get('HTTP_USER_AGENT')
            )
            
            return api_key
        except APIKeyError as e:
            raise serializers.ValidationError(str(e))
    
    def perform_destroy(self, instance):
        """
        Delete an API key and log the action
        
        Uses the APIKeyService to handle API key deletion.
        """
        try:
            # Delete using service
            self.api_key_service.delete_api_key(instance.id)
            
            # Log API key deletion
            self.audit_log_service.create_audit_log(
                user_id=self.request.user.id,
                action="API_KEY_DELETE",
                details={
                    "api_key_id": str(instance.id),
                    "name": instance.name,
                    "provider_type": instance.provider_type
                },
                ip_address=self._get_client_ip(self.request),
                user_agent=self.request.META.get('HTTP_USER_AGENT')
            )
        except APIKeyError as e:
            raise serializers.ValidationError(str(e))
    
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
        self.audit_log_service.create_audit_log(
            user_id=self.request.user.id,
            action="API_KEY_UPDATE",
            details={
                "api_key_id": str(api_key.id),
                "name": api_key.name,
                "provider_type": api_key.provider_type
            },
            ip_address=self._get_client_ip(self.request),
            user_agent=self.request.META.get('HTTP_USER_AGENT')
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
        self.audit_log_service.create_audit_log(
            user_id=self.request.user.id,
            action="API_KEY_UPDATE",
            details={
                "api_key_id": str(api_key.id),
                "name": api_key.name,
                "provider_type": api_key.provider_type
            },
            ip_address=self._get_client_ip(self.request),
            user_agent=self.request.META.get('HTTP_USER_AGENT')
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

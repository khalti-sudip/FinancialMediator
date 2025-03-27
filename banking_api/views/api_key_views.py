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
from banking_api.utils.common import get_client_ip, get_user_agent, format_timestamp
import uuid

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
        
        Args:
            serializer: The serializer containing validated data
            
        Returns:
            The created APIKey instance
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
            self._log_api_key_action(
                api_key,
                "API_KEY_CREATE",
                "API key created"
            )
            
            return api_key
        except APIKeyError as e:
            raise serializers.ValidationError(str(e))
    
    def perform_update(self, serializer):
        """
        Update an API key and log the action
        
        Args:
            serializer: The serializer containing validated data
            
        Returns:
            The updated APIKey instance
        """
        try:
            api_key = serializer.save()
            
            # Update using service
            self.api_key_service.update_api_key(
                api_key.id,
                **serializer.validated_data
            )
            
            # Log API key update
            self._log_api_key_action(
                api_key,
                "API_KEY_UPDATE",
                "API key updated"
            )
            
            return api_key
        except APIKeyError as e:
            raise serializers.ValidationError(str(e))
    
    def perform_destroy(self, instance):
        """
        Delete an API key and log the action
        
        Args:
            instance: The APIKey instance to delete
        """
        try:
            # Delete using service
            self.api_key_service.delete_api_key(instance.id)
            
            # Log API key deletion
            self._log_api_key_action(
                instance,
                "API_KEY_DELETE",
                "API key deleted"
            )
        except APIKeyError as e:
            raise serializers.ValidationError(str(e))
    
    @action(detail=False, methods=["get"])
    def validate(self, request):
        """
        Validate an API key
        
        Args:
            request: The HTTP request object
            
        Returns:
            Response containing validation result
        """
        api_key = request.query_params.get("api_key")
        if not api_key:
            return Response(
                {"error": "API key is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            is_valid = self.api_key_service.validate_api_key(api_key)
            return Response({"valid": is_valid})
        except APIKeyError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def _log_api_key_action(self, api_key, action, message):
        """
        Log an API key action
        
        Args:
            api_key: The APIKey instance
            action: The action type
            message: The log message
        """
        self.audit_log_service.create_audit_log(
            user_id=self.request.user.id,
            action=action,
            details={
                "api_key_id": str(api_key.id),
                "name": api_key.name,
                "provider_type": api_key.provider_type,
                "message": message
            },
            ip_address=get_client_ip(self.request),
            user_agent=get_user_agent(self.request)
        )

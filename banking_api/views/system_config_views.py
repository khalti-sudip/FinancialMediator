from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from banking_api.models.system_config import SystemConfig
from banking_api.models.audit_log import AuditLog
from banking_api.serializers.system_config_serializer import SystemConfigSerializer
from banking_api.services.system_config_service import SystemConfigService
from banking_api.services.audit_log_service import AuditLogService
from banking_api.exceptions import SystemConfigError

class SystemConfigViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing system configurations.
    
    This viewset handles all system configuration operations using the SystemConfigService.
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
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.system_config_service = SystemConfigService()
        self.audit_log_service = AuditLogService()
    
    def perform_create(self, serializer):
        """
        Create a new system configuration and log the action
        
        Uses the SystemConfigService to handle configuration creation.
        """
        try:
            system_config = self.system_config_service.set_config(
                key=serializer.validated_data["key"],
                value=serializer.validated_data["value"],
                description=serializer.validated_data.get("description", "")
            )
            
            # Log system config creation
            self.audit_log_service.create_audit_log(
                user_id=self.request.user.id,
                action="SYSTEM_CONFIG_CREATE",
                details={
                    "config_id": str(system_config.id),
                    "key": system_config.key,
                    "value": system_config.value,
                    "description": system_config.description
                },
                ip_address=self._get_client_ip(self.request),
                user_agent=self.request.META.get('HTTP_USER_AGENT')
            )
            
            return system_config
        except SystemConfigError as e:
            raise serializers.ValidationError(str(e))
    
    def perform_update(self, serializer):
        """
        Update a system configuration and log the action
        
        Uses the SystemConfigService to handle configuration updates.
        """
        try:
            system_config = serializer.save()
            
            # Update using service
            self.system_config_service.set_config(
                key=system_config.key,
                value=serializer.validated_data["value"],
                description=serializer.validated_data.get("description", "")
            )
            
            # Log system config update
            self.audit_log_service.create_audit_log(
                user_id=self.request.user.id,
                action="SYSTEM_CONFIG_UPDATE",
                details={
                    "config_id": str(system_config.id),
                    "key": system_config.key,
                    "value": system_config.value,
                    "description": system_config.description
                },
                ip_address=self._get_client_ip(self.request),
                user_agent=self.request.META.get('HTTP_USER_AGENT')
            )
            
            return system_config
        except SystemConfigError as e:
            raise serializers.ValidationError(str(e))
    
    def perform_destroy(self, instance):
        """
        Delete a system configuration and log the action
        
        Uses the SystemConfigService to handle configuration deletion.
        """
        try:
            # Delete using service
            self.system_config_service.delete_config(instance.key)
            
            # Log system config deletion
            self.audit_log_service.create_audit_log(
                user_id=self.request.user.id,
                action="SYSTEM_CONFIG_DELETE",
                details={
                    "config_id": str(instance.id),
                    "key": instance.key,
                    "value": instance.value,
                    "description": instance.description
                },
                ip_address=self._get_client_ip(self.request),
                user_agent=self.request.META.get('HTTP_USER_AGENT')
            )
        except SystemConfigError as e:
            raise serializers.ValidationError(str(e))
    
    @action(detail=False, methods=['get'])
    def get_config(self, request):
        """
        Get a specific system configuration by key
        
        Returns the configuration value if found.
        """
        key = request.query_params.get('key')
        if not key:
            return Response(
                {"error": "Key is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            config = self.system_config_service.get_config(key)
            if not config:
                return Response(
                    {"error": f"Configuration {key} not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            return Response(config)
        except SystemConfigError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def get_all_configs(self, request):
        """
        Get all system configurations
        
        Returns a dictionary of all configurations.
        """
        try:
            configs = self.system_config_service.get_all_configs()
            return Response(configs)
        except SystemConfigError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def _get_client_ip(self, request):
        """Get the client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

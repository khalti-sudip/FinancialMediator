from rest_framework import viewsets, filters, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from banking_api.models.audit_log import AuditLog
from banking_api.serializers.audit_log_serializer import AuditLogSerializer
from banking_api.services.audit_log_service import AuditLogService
from banking_api.exceptions import AuditLogError
from banking_api.utils.common import get_client_ip, format_timestamp
from rest_framework.response import Response

class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing audit logs. Read-only as logs should not be modified.
    
    This viewset handles all audit log operations using the AuditLogService.
    """
    
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["action", "resource_type", "user"]
    search_fields = ["resource_id", "details", "ip_address"]
    ordering_fields = ["id", "created_at", "action"]
    ordering = ["-created_at"]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.audit_log_service = AuditLogService()
    
    def list(self, request, *args, **kwargs):
        """
        List audit logs with optional filters.
        
        Args:
            request: The HTTP request object
            
        Returns:
            Response containing the list of audit logs
        """
        try:
            filters = self._get_request_filters(request)
            logs = self.audit_log_service.get_audit_logs(
                user_id=filters.get("user_id"),
                action=filters.get("action"),
                start_date=filters.get("start_date"),
                end_date=filters.get("end_date"),
                limit=100
            )
            
            serializer = self.get_serializer(logs, many=True)
            return Response(serializer.data)
        except AuditLogError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a specific audit log by ID.
        
        Args:
            request: The HTTP request object
            
        Returns:
            Response containing the audit log details
        """
        try:
            log = self.audit_log_service.get_audit_log_by_id(kwargs["pk"])
            serializer = self.get_serializer(log)
            return Response(serializer.data)
        except AuditLogError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=["get"])
    def user_logs(self, request):
        """
        Get audit logs for a specific user.
        
        Args:
            request: The HTTP request object
            
        Returns:
            Response containing the user's audit logs
        """
        try:
            user_id = request.query_params.get("user_id")
            if not user_id:
                return Response(
                    {"error": "user_id is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            logs = self.audit_log_service.get_user_audit_logs(
                user_id=user_id,
                limit=100
            )
            
            serializer = self.get_serializer(logs, many=True)
            return Response(serializer.data)
        except AuditLogError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=["get"])
    def action_logs(self, request):
        """
        Get audit logs for a specific action.
        
        Args:
            request: The HTTP request object
            
        Returns:
            Response containing the action's audit logs
        """
        try:
            action = request.query_params.get("action")
            if not action:
                return Response(
                    {"error": "action is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            logs = self.audit_log_service.get_action_audit_logs(
                action=action,
                limit=100
            )
            
            serializer = self.get_serializer(logs, many=True)
            return Response(serializer.data)
        except AuditLogError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=["get"])
    def recent_logs(self, request):
        """
        Get most recent audit logs.
        
        Args:
            request: The HTTP request object
            
        Returns:
            Response containing the most recent audit logs
        """
        try:
            limit = int(request.query_params.get("limit", 100))
            logs = self.audit_log_service.get_recent_audit_logs(limit=limit)
            
            serializer = self.get_serializer(logs, many=True)
            return Response(serializer.data)
        except (ValueError, AuditLogError) as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def _get_request_filters(self, request):
        """
        Extract and validate request filters.
        
        Args:
            request: The HTTP request object
            
        Returns:
            Dictionary of validated filter parameters
        """
        return {
            "user_id": request.query_params.get("user_id"),
            "action": request.query_params.get("action"),
            "start_date": request.query_params.get("start_date"),
            "end_date": request.query_params.get("end_date")
        }

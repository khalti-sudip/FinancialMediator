"""
Provider Key Views Module.

This module provides views for:
- API key management
- Usage monitoring
- Access control
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
import logging

from ..models import ProviderKey
from ..serializers import ProviderKeySerializer
from ..tasks import cleanup_expired_keys

logger = logging.getLogger(__name__)

class ProviderKeyViewSet(viewsets.ModelViewSet):
    """ViewSet for managing provider API keys."""
    
    serializer_class = ProviderKeySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Get filtered queryset of API keys.
        
        Filters:
        - provider
        - environment
        - is_active
        - user
        
        Returns:
            QuerySet: Filtered API keys
        """
        queryset = ProviderKey.objects.all()
        
        # Filter by provider
        provider_id = self.request.query_params.get("provider")
        if provider_id:
            queryset = queryset.filter(provider_id=provider_id)
        
        # Filter by environment
        environment = self.request.query_params.get("environment")
        if environment:
            queryset = queryset.filter(environment=environment)
        
        # Filter by active state
        is_active = self.request.query_params.get("active")
        if is_active is not None:
            queryset = queryset.filter(
                is_active=is_active.lower() == "true"
            )
        
        # Filter by user
        user = self.request.query_params.get("user")
        if user:
            queryset = queryset.filter(user_id=user)
        
        return queryset
    
    def perform_create(self, serializer):
        """
        Create new API key.
        
        This method:
        1. Generates key data
        2. Sets expiration
        3. Creates key record
        
        Args:
            serializer: Key serializer
        """
        # Generate key data
        key_data = generate_api_key()
        
        # Set expiration
        expires_at = timezone.now() + timezone.timedelta(days=365)
        
        # Save key
        serializer.save(
            key_data=key_data,
            expires_at=expires_at,
        )
    
    @action(detail=True, methods=["post"])
    def deactivate(self, request, pk=None):
        """
        Deactivate API key.
        
        This endpoint:
        1. Validates key status
        2. Deactivates key
        3. Updates usage data
        
        Args:
            request: HTTP request
            pk: Key ID
            
        Returns:
            Response: Deactivation result
        """
        try:
            # Get key
            key = self.get_object()
            
            # Check if already inactive
            if not key.is_active:
                return Response({
                    "message": "Key is already inactive"
                })
            
            # Deactivate key
            key.is_active = False
            key.save(update_fields=["is_active"])
            
            return Response({
                "message": "Key deactivated successfully"
            })
            
        except Exception as e:
            logger.error(
                f"Failed to deactivate key {pk}",
                exc_info=True
            )
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=["post"])
    def reset_limits(self, request, pk=None):
        """
        Reset API key usage limits.
        
        This endpoint:
        1. Validates key status
        2. Resets usage counters
        3. Updates limits
        
        Args:
            request: HTTP request
            pk: Key ID
            
        Returns:
            Response: Reset result
        """
        try:
            # Get key
            key = self.get_object()
            
            # Reset counters
            key.daily_usage = 0
            key.monthly_usage = 0
            key.save(update_fields=["daily_usage", "monthly_usage"])
            
            return Response({
                "message": "Usage limits reset successfully"
            })
            
        except Exception as e:
            logger.error(
                f"Failed to reset limits for key {pk}",
                exc_info=True
            )
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=["get"])
    def usage(self, request, pk=None):
        """
        Get API key usage statistics.
        
        This endpoint:
        1. Retrieves usage data
        2. Calculates remaining limits
        3. Returns usage metrics
        
        Args:
            request: HTTP request
            pk: Key ID
            
        Returns:
            Response: Usage statistics
        """
        try:
            # Get key
            key = self.get_object()
            
            # Calculate remaining limits
            daily_remaining = (
                key.daily_limit - key.daily_usage
                if key.daily_limit
                else None
            )
            monthly_remaining = (
                key.monthly_limit - key.monthly_usage
                if key.monthly_limit
                else None
            )
            
            return Response({
                "daily_usage": key.daily_usage,
                "monthly_usage": key.monthly_usage,
                "daily_remaining": daily_remaining,
                "monthly_remaining": monthly_remaining,
                "last_used": key.last_used_at,
            })
            
        except Exception as e:
            logger.error(
                f"Failed to get usage for key {pk}",
                exc_info=True
            )
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=["post"])
    def cleanup(self, request):
        """
        Clean up expired API keys.
        
        This endpoint:
        1. Triggers cleanup task
        2. Deactivates expired keys
        3. Returns cleanup summary
        
        Args:
            request: HTTP request
            
        Returns:
            Response: Cleanup summary
        """
        try:
            # Start cleanup task
            task = cleanup_expired_keys.delay()
            
            return Response({
                "message": "Key cleanup initiated",
                "task_id": task.id,
            })
            
        except Exception as e:
            logger.error("Failed to cleanup expired keys", exc_info=True)
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

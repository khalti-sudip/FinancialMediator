"""
Provider Views Module.

This module provides views for:
- Provider management
- Status monitoring
- Configuration updates
- Statistics reporting
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.cache import cache
from django.utils import timezone
import logging

from ..models import Provider
from ..serializers import (
    ProviderSerializer,
    ProviderStatusSerializer,
    ProviderStatsSerializer,
)
from ..tasks import check_provider_status, collect_provider_stats

logger = logging.getLogger(__name__)

class ProviderViewSet(viewsets.ModelViewSet):
    """ViewSet for managing providers."""
    
    serializer_class = ProviderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Get filtered queryset of providers.
        
        Filters:
        - provider_type
        - status
        - is_active
        
        Returns:
            QuerySet: Filtered providers
        """
        queryset = Provider.objects.all()
        
        # Filter by type
        provider_type = self.request.query_params.get("type")
        if provider_type:
            queryset = queryset.filter(provider_type=provider_type)
        
        # Filter by status
        status = self.request.query_params.get("status")
        if status:
            queryset = queryset.filter(status=status)
        
        # Filter by active state
        is_active = self.request.query_params.get("active")
        if is_active is not None:
            queryset = queryset.filter(
                is_active=is_active.lower() == "true"
            )
        
        return queryset
    
    @action(detail=True, methods=["post"])
    def check_status(self, request, pk=None):
        """
        Check provider status.
        
        This endpoint:
        1. Initiates status check
        2. Updates provider status
        3. Returns check results
        
        Args:
            request: HTTP request
            pk: Provider ID
            
        Returns:
            Response: Status check result
        """
        try:
            # Get provider
            provider = self.get_object()
            
            # Check status
            is_healthy = provider.check_status()
            
            # Return result
            return Response({
                "status": provider.status,
                "is_healthy": is_healthy,
                "last_check": provider.last_check_at,
            })
            
        except Exception as e:
            logger.error(
                f"Status check failed for provider {pk}",
                exc_info=True
            )
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=["post"])
    def update_status(self, request, pk=None):
        """
        Update provider status.
        
        This endpoint:
        1. Validates status update
        2. Updates provider status
        3. Triggers notifications
        
        Args:
            request: HTTP request
            pk: Provider ID
            
        Returns:
            Response: Update result
        """
        try:
            # Get provider
            provider = self.get_object()
            
            # Validate data
            serializer = ProviderStatusSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            # Update status
            old_status = provider.status
            provider.status = serializer.validated_data["status"]
            
            if "message" in serializer.validated_data:
                provider.status_message = serializer.validated_data["message"]
            
            provider.save()
            
            # Trigger notification if status changed
            if old_status != provider.status:
                from ..tasks import notify_provider_status
                notify_provider_status.delay(
                    provider.id,
                    provider.status
                )
            
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(
                f"Status update failed for provider {pk}",
                exc_info=True
            )
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=["get"])
    def statistics(self, request, pk=None):
        """
        Get provider statistics.
        
        This endpoint:
        1. Retrieves cached stats
        2. Calculates new metrics
        3. Returns provider performance data
        
        Args:
            request: HTTP request
            pk: Provider ID
            
        Returns:
            Response: Provider statistics
        """
        try:
            # Get provider
            provider = self.get_object()
            
            # Get cached stats
            stats = cache.get(f"provider_stats:{provider.code}")
            
            if not stats:
                # Calculate new stats
                stats = {
                    "total_requests": 0,
                    "success_rate": 0.0,
                    "average_response_time": 0.0,
                    "error_rate": 0.0,
                    "active_keys": 0,
                    "webhook_success_rate": 0.0,
                    "last_update": timezone.now(),
                }
                
                # Queue stats collection
                collect_provider_stats.delay()
            
            # Serialize and return
            serializer = ProviderStatsSerializer(stats)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(
                f"Failed to get statistics for provider {pk}",
                exc_info=True
            )
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=["post"])
    def rotate_credentials(self, request, pk=None):
        """
        Rotate provider API credentials.
        
        This endpoint:
        1. Validates current access
        2. Generates new credentials
        3. Updates provider configuration
        
        Args:
            request: HTTP request
            pk: Provider ID
            
        Returns:
            Response: New credentials
        """
        try:
            # Get provider
            provider = self.get_object()
            
            # Generate new credentials
            new_credentials = generate_provider_credentials(
                provider.provider_type
            )
            
            # Update provider
            provider.credentials = new_credentials
            provider.save(update_fields=["credentials"])
            
            return Response({
                "message": "Credentials rotated successfully",
                "credentials": new_credentials,
            })
            
        except Exception as e:
            logger.error(
                f"Credential rotation failed for provider {pk}",
                exc_info=True
            )
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=["post"])
    def check_all(self, request):
        """
        Check status of all providers.
        
        This endpoint:
        1. Triggers status checks
        2. Updates provider statuses
        3. Returns summary results
        
        Args:
            request: HTTP request
            
        Returns:
            Response: Status check summary
        """
        try:
            # Start status check task
            task = check_provider_status.delay()
            
            return Response({
                "message": "Status check initiated",
                "task_id": task.id,
            })
            
        except Exception as e:
            logger.error("Failed to check all providers", exc_info=True)
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

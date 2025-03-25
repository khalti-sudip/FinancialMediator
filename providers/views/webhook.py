"""
Provider Webhook Views Module.

This module provides views for:
- Webhook processing
- Event handling
- Retry management
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
import logging

from ..models import ProviderWebhook
from ..serializers import ProviderWebhookSerializer
from ..tasks import process_webhook

logger = logging.getLogger(__name__)

class ProviderWebhookViewSet(viewsets.ModelViewSet):
    """ViewSet for managing provider webhooks."""
    
    serializer_class = ProviderWebhookSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Get filtered queryset of webhooks.
        
        Filters:
        - provider
        - event_type
        - status
        - date range
        
        Returns:
            QuerySet: Filtered webhooks
        """
        queryset = ProviderWebhook.objects.all()
        
        # Filter by provider
        provider_id = self.request.query_params.get("provider")
        if provider_id:
            queryset = queryset.filter(provider_id=provider_id)
        
        # Filter by event type
        event_type = self.request.query_params.get("event_type")
        if event_type:
            queryset = queryset.filter(event_type=event_type)
        
        # Filter by status
        status = self.request.query_params.get("status")
        if status:
            queryset = queryset.filter(status=status)
        
        # Filter by date range
        start_date = self.request.query_params.get("start_date")
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        
        end_date = self.request.query_params.get("end_date")
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)
        
        return queryset
    
    def perform_create(self, serializer):
        """
        Create new webhook event.
        
        This method:
        1. Validates event data
        2. Creates webhook record
        3. Triggers processing
        
        Args:
            serializer: Webhook serializer
        """
        # Save webhook
        webhook = serializer.save(
            status="pending",
            retry_count=0,
        )
        
        # Start processing
        process_webhook.delay(webhook.id)
    
    @action(detail=True, methods=["post"])
    def retry(self, request, pk=None):
        """
        Retry webhook processing.
        
        This endpoint:
        1. Validates retry eligibility
        2. Resets webhook status
        3. Triggers reprocessing
        
        Args:
            request: HTTP request
            pk: Webhook ID
            
        Returns:
            Response: Retry result
        """
        try:
            # Get webhook
            webhook = self.get_object()
            
            # Check if can retry
            if webhook.status not in ["failed", "error"]:
                return Response({
                    "message": "Webhook cannot be retried"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Reset status
            webhook.status = "pending"
            webhook.error_message = None
            webhook.save(update_fields=["status", "error_message"])
            
            # Start processing
            process_webhook.delay(webhook.id)
            
            return Response({
                "message": "Webhook retry initiated"
            })
            
        except Exception as e:
            logger.error(
                f"Failed to retry webhook {pk}",
                exc_info=True
            )
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        """
        Cancel webhook processing.
        
        This endpoint:
        1. Validates cancellation
        2. Updates webhook status
        3. Stops processing
        
        Args:
            request: HTTP request
            pk: Webhook ID
            
        Returns:
            Response: Cancellation result
        """
        try:
            # Get webhook
            webhook = self.get_object()
            
            # Check if can cancel
            if webhook.status not in ["pending", "processing"]:
                return Response({
                    "message": "Webhook cannot be cancelled"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Update status
            webhook.status = "cancelled"
            webhook.save(update_fields=["status"])
            
            return Response({
                "message": "Webhook cancelled successfully"
            })
            
        except Exception as e:
            logger.error(
                f"Failed to cancel webhook {pk}",
                exc_info=True
            )
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=["get"])
    def summary(self, request):
        """
        Get webhook processing summary.
        
        This endpoint:
        1. Retrieves webhook stats
        2. Calculates success rates
        3. Returns processing metrics
        
        Args:
            request: HTTP request
            
        Returns:
            Response: Processing summary
        """
        try:
            # Get time range
            end_time = timezone.now()
            start_time = end_time - timezone.timedelta(hours=24)
            
            # Get webhooks in range
            webhooks = ProviderWebhook.objects.filter(
                created_at__range=[start_time, end_time]
            )
            
            # Calculate metrics
            total = webhooks.count()
            completed = webhooks.filter(status="completed").count()
            failed = webhooks.filter(status="failed").count()
            pending = webhooks.filter(status="pending").count()
            
            return Response({
                "total": total,
                "completed": completed,
                "failed": failed,
                "pending": pending,
                "success_rate": completed / total if total > 0 else 0,
                "time_range": {
                    "start": start_time,
                    "end": end_time,
                },
            })
            
        except Exception as e:
            logger.error("Failed to get webhook summary", exc_info=True)
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

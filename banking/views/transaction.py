"""
Transaction Views Module.

This module provides views for:
- Transaction creation and management
- Transaction status updates
- Transaction history and filtering
- Batch transaction processing
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.utils import timezone
import logging

from ..models import Transaction
from ..serializers import TransactionSerializer
from ..tasks import update_balances

logger = logging.getLogger(__name__)

class TransactionViewSet(viewsets.ModelViewSet):
    """ViewSet for managing transactions."""
    
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Get filtered queryset of transactions.
        
        Filters:
        - status
        - transaction_type
        - date range
        - amount range
        
        Returns:
            QuerySet: Filtered transactions
        """
        queryset = Transaction.objects.all()
        
        # Filter by status
        status = self.request.query_params.get("status")
        if status:
            queryset = queryset.filter(status=status)
        
        # Filter by type
        txn_type = self.request.query_params.get("type")
        if txn_type:
            queryset = queryset.filter(transaction_type=txn_type)
        
        # Filter by date range
        start_date = self.request.query_params.get("start_date")
        end_date = self.request.query_params.get("end_date")
        if start_date and end_date:
            queryset = queryset.filter(
                created_at__range=[start_date, end_date]
            )
        
        # Filter by amount range
        min_amount = self.request.query_params.get("min_amount")
        max_amount = self.request.query_params.get("max_amount")
        if min_amount and max_amount:
            queryset = queryset.filter(
                amount__range=[min_amount, max_amount]
            )
        
        return queryset
    
    def perform_create(self, serializer):
        """
        Create a new transaction.
        
        This method:
        1. Generates transaction ID
        2. Sets initial status
        3. Triggers processing
        
        Args:
            serializer: Transaction serializer
        """
        # Generate transaction ID
        transaction_id = generate_transaction_id()
        
        # Create transaction
        with transaction.atomic():
            txn = serializer.save(
                transaction_id=transaction_id,
                status="pending"
            )
            
            # Start processing
            process_transaction.delay(txn.id)
    
    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        """
        Cancel a pending transaction.
        
        This endpoint:
        1. Validates transaction can be cancelled
        2. Updates status
        3. Reverses any partial processing
        
        Args:
            request: HTTP request
            pk: Transaction ID
            
        Returns:
            Response: Cancellation result
        """
        try:
            # Get transaction
            txn = self.get_object()
            
            # Check if can be cancelled
            if txn.status not in ["pending", "processing"]:
                return Response(
                    {"error": "Transaction cannot be cancelled"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Cancel transaction
            with transaction.atomic():
                txn.status = "cancelled"
                txn.completed_at = timezone.now()
                txn.save()
                
                # Update balances
                update_balances.delay()
            
            return Response({"status": "cancelled"})
            
        except Exception as e:
            logger.error(
                f"Failed to cancel transaction {pk}",
                exc_info=True
            )
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=["post"])
    def retry(self, request, pk=None):
        """
        Retry a failed transaction.
        
        This endpoint:
        1. Validates transaction can be retried
        2. Resets status
        3. Triggers reprocessing
        
        Args:
            request: HTTP request
            pk: Transaction ID
            
        Returns:
            Response: Retry result
        """
        try:
            # Get transaction
            txn = self.get_object()
            
            # Check if can be retried
            if txn.status != "failed":
                return Response(
                    {"error": "Only failed transactions can be retried"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Retry transaction
            with transaction.atomic():
                txn.status = "pending"
                txn.error_code = ""
                txn.error_message = ""
                txn.save()
                
                # Start processing
                process_transaction.delay(txn.id)
            
            return Response({"status": "retrying"})
            
        except Exception as e:
            logger.error(
                f"Failed to retry transaction {pk}",
                exc_info=True
            )
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=["post"])
    def batch_create(self, request):
        """
        Create multiple transactions in batch.
        
        This endpoint:
        1. Validates all transactions
        2. Creates transactions atomically
        3. Triggers batch processing
        
        Args:
            request: HTTP request with transaction list
            
        Returns:
            Response: Batch creation result
        """
        try:
            # Validate data
            serializer = self.get_serializer(
                data=request.data,
                many=True
            )
            serializer.is_valid(raise_exception=True)
            
            # Create transactions
            transactions = []
            with transaction.atomic():
                for item in serializer.validated_data:
                    # Generate transaction ID
                    transaction_id = generate_transaction_id()
                    
                    # Create transaction
                    txn = serializer.create({
                        **item,
                        "transaction_id": transaction_id,
                        "status": "pending"
                    })
                    transactions.append(txn)
            
            # Start processing
            process_transactions.delay([t.id for t in transactions])
            
            # Return results
            return Response({
                "created": len(transactions),
                "transactions": self.get_serializer(
                    transactions,
                    many=True
                ).data
            })
            
        except Exception as e:
            logger.error("Batch creation failed", exc_info=True)
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

def generate_transaction_id():
    """
    Generate unique transaction ID.
    
    Returns:
        str: Unique transaction ID
    """
    import uuid
    import time
    
    # Combine timestamp and UUID
    timestamp = int(time.time())
    unique_id = str(uuid.uuid4()).replace("-", "")[:12]
    
    return f"TXN{timestamp}{unique_id}"

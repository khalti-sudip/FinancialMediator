"""
Banking Payment Views Module.

This module provides views for:
- Payment processing
- Payment methods
- Payment history
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db import transaction
import logging

from ..models import PaymentMethod, Transaction, BankAccount
from ..serializers import (
    PaymentMethodSerializer,
    TransactionSerializer,
    PaymentRequestSerializer,
    PaymentResponseSerializer,
)
from ..services import PaymentService, TransactionService
from ..permissions import IsPaymentMethodOwner

logger = logging.getLogger(__name__)

class PaymentMethodViewSet(viewsets.ModelViewSet):
    """ViewSet for managing payment methods."""
    
    queryset = PaymentMethod.objects.all()
    serializer_class = PaymentMethodSerializer
    permission_classes = [IsAuthenticated, IsPaymentMethodOwner]
    
    def get_queryset(self):
        """Filter queryset by user."""
        return self.queryset.filter(user_id=self.request.user.id)
    
    def perform_create(self, serializer):
        """Create payment method."""
        try:
            # Add user
            serializer.save(user_id=self.request.user.id)
            
        except Exception as e:
            logger.error(
                f"Failed to create payment method: {str(e)}",
                exc_info=True
            )
            raise
    
    @action(detail=True, methods=["post"])
    def verify(self, request, pk=None):
        """Verify payment method."""
        try:
            # Get payment method
            payment_method = self.get_object()
            
            # Get provider
            provider = payment_method.provider
            if not provider.is_active:
                raise ValueError("Payment provider is not active")
            
            # Verify with provider
            response = provider.verify_payment_method(
                payment_method.external_id
            )
            
            # Update status
            payment_method.is_verified = response["is_verified"]
            payment_method.verification_data = response
            payment_method.verified_at = timezone.now()
            payment_method.save()
            
            # Return response
            return Response({
                "is_verified": payment_method.is_verified,
                "verification_data": payment_method.verification_data,
            })
            
        except Exception as e:
            logger.error(
                f"Failed to verify payment method: {str(e)}",
                exc_info=True
            )
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=["post"])
    def deactivate(self, request, pk=None):
        """Deactivate payment method."""
        try:
            # Get payment method
            payment_method = self.get_object()
            
            # Deactivate
            payment_method.is_active = False
            payment_method.save()
            
            return Response({"message": "Payment method deactivated"})
            
        except Exception as e:
            logger.error(
                f"Failed to deactivate payment method: {str(e)}",
                exc_info=True
            )
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class PaymentViewSet(viewsets.ViewSet):
    """ViewSet for processing payments."""
    
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=["post"])
    def process(self, request):
        """Process a payment."""
        try:
            # Validate request
            serializer = PaymentRequestSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            # Get data
            data = serializer.validated_data
            account = BankAccount.objects.get(id=data["account_id"])
            payment_method = PaymentMethod.objects.get(
                id=data["payment_method_id"]
            )
            
            # Check ownership
            if account.user_id != request.user.id:
                raise ValueError("Invalid account")
            if payment_method.user_id != request.user.id:
                raise ValueError("Invalid payment method")
            
            # Get service
            service = PaymentService()
            
            # Process payment
            transaction = service.process_payment(
                account=account,
                amount=data["amount"],
                currency=data["currency"],
                payment_method=payment_method,
                metadata=data.get("metadata"),
            )
            
            # Return response
            return Response(
                PaymentResponseSerializer(transaction).data,
                status=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            logger.error(
                f"Failed to process payment: {str(e)}",
                exc_info=True
            )
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=["post"])
    def cancel(self, request):
        """Cancel a payment."""
        try:
            # Get transaction
            transaction = Transaction.objects.get(
                reference=request.data.get("reference")
            )
            
            # Check ownership
            if transaction.account.user_id != request.user.id:
                raise ValueError("Invalid transaction")
            
            # Get service
            service = TransactionService()
            
            # Cancel transaction
            success = service.cancel_transaction(
                transaction=transaction,
                reason=request.data.get("reason", "User cancelled"),
                metadata=request.data.get("metadata"),
            )
            
            if not success:
                raise ValueError("Failed to cancel payment")
            
            # Return response
            return Response({
                "message": "Payment cancelled",
                "transaction": TransactionSerializer(transaction).data,
            })
            
        except Exception as e:
            logger.error(
                f"Failed to cancel payment: {str(e)}",
                exc_info=True
            )
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=["post"])
    def refund(self, request):
        """Refund a payment."""
        try:
            # Get transaction
            transaction = Transaction.objects.get(
                reference=request.data.get("reference")
            )
            
            # Check ownership
            if transaction.account.user_id != request.user.id:
                raise ValueError("Invalid transaction")
            
            # Get provider
            provider = transaction.provider
            if not provider.is_active:
                raise ValueError("Payment provider is not active")
            
            # Process refund
            refund_data = {
                "transaction_id": transaction.reference,
                "amount": request.data.get("amount", transaction.amount),
                "reason": request.data.get("reason", "User requested"),
                "metadata": request.data.get("metadata", {}),
            }
            
            # Call provider API
            response = provider.process_refund(refund_data)
            
            # Create refund transaction
            service = TransactionService()
            refund = service.create_transaction(
                account=transaction.account,
                amount=response["amount"],
                transaction_type="refund",
                currency=transaction.currency,
                reference=response["refund_id"],
                provider=provider,
                parent_reference=transaction.reference,
                metadata={
                    "reason": refund_data["reason"],
                    "provider_response": response,
                },
            )
            
            # Return response
            return Response({
                "message": "Payment refunded",
                "refund": TransactionSerializer(refund).data,
            })
            
        except Exception as e:
            logger.error(
                f"Failed to refund payment: {str(e)}",
                exc_info=True
            )
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

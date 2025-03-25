from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
import uuid

from banking_api.models.transaction import Transaction
from banking_api.models.audit_log import AuditLog
from banking_api.serializers.transaction_serializer import TransactionSerializer


class TransactionViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing transactions.
    """

    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = [
        "status",
        "source_system",
        "target_system",
        "transaction_type",
        "user_id",
    ]
    search_fields = ["transaction_id", "user_id"]
    ordering_fields = ["id", "created_at", "updated_at", "amount"]
    ordering = ["-created_at"]

    def perform_create(self, serializer):
        """Create a new transaction with auto-generated ID if not provided"""
        # Generate transaction_id if not provided
        if "transaction_id" not in serializer.validated_data:
            serializer.validated_data["transaction_id"] = str(uuid.uuid4())

        transaction = serializer.save()

        # Log transaction creation
        AuditLog.log_action(
            action="create",
            resource_type="transaction",
            resource_id=transaction.transaction_id,
            user=self.request.user,
            ip_address=self._get_client_ip(self.request),
        )

    def perform_update(self, serializer):
        """Update a transaction and log the action"""
        transaction = serializer.save()

        # Log transaction update
        AuditLog.log_action(
            action="update",
            resource_type="transaction",
            resource_id=transaction.transaction_id,
            user=self.request.user,
            ip_address=self._get_client_ip(self.request),
        )

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        """
        Mark a transaction as completed
        """
        transaction = self.get_object()

        if transaction.status == "completed":
            return Response(
                {"error": "Transaction is already completed"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        response_data = request.data.get("response_data")

        transaction.mark_completed(response_data)

        # Log transaction completion
        AuditLog.log_action(
            action="update",
            resource_type="transaction",
            resource_id=transaction.transaction_id,
            user=request.user,
            details="Transaction marked as completed",
            ip_address=self._get_client_ip(request),
        )

        serializer = self.get_serializer(transaction)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def fail(self, request, pk=None):
        """
        Mark a transaction as failed
        """
        transaction = self.get_object()

        if transaction.status == "failed":
            return Response(
                {"error": "Transaction is already marked as failed"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        error_message = request.data.get("error_message", "Transaction failed")

        transaction.mark_failed(error_message)

        # Log transaction failure
        AuditLog.log_action(
            action="update",
            resource_type="transaction",
            resource_id=transaction.transaction_id,
            user=request.user,
            details="Transaction marked as failed",
            ip_address=self._get_client_ip(request),
        )

        serializer = self.get_serializer(transaction)
        return Response(serializer.data)

    def _get_client_ip(self, request):
        """Get the client IP address from request"""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip

from django.db import models
from django.utils import timezone
import uuid

class Transaction(models.Model):
    """Transaction model for tracking middleware operations"""

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transaction_id = models.CharField(max_length=100, unique=True, null=False)
    source_system = models.CharField(max_length=50, null=False)
    target_system = models.CharField(max_length=50, null=False)
    transaction_type = models.CharField(max_length=50, null=False)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="pending")
    amount = models.DecimalField(max_digits=20, decimal_places=6, null=True, blank=True)
    currency = models.CharField(max_length=10, null=True, blank=True)
    user_id = models.CharField(max_length=100, null=True, blank=True)
    request_data = models.JSONField(null=True, blank=True)
    response_data = models.JSONField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "transactions"
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["transaction_id"]),
            models.Index(fields=["status"]),
            models.Index(fields=["source_system"]),
            models.Index(fields=["target_system"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["user_id"]),
            models.Index(fields=["transaction_type"]),
            models.Index(fields=["status", "created_at"]),  # Common query pattern
            models.Index(fields=["source_system", "target_system"]),  # Common query pattern
        ]

    def mark_completed(self, response_data):
        """
        Mark transaction as completed with response data

        Args:
            response_data: Response data from the target system
        """
        self.status = "completed"
        self.response_data = response_data
        self.updated_at = timezone.now()
        self.save(update_fields=["status", "response_data", "updated_at"])

    def mark_failed(self, error_message):
        """
        Mark transaction as failed with error message

        Args:
            error_message: Error message from the target system
        """
        self.status = "failed"
        self.error_message = error_message
        self.updated_at = timezone.now()
        self.save(update_fields=["status", "error_message", "updated_at"])

    @classmethod
    def get_recent_transactions(cls, limit=100):
        """
        Get recent transactions with optimized query

        Args:
            limit: Number of transactions to return

        Returns:
            QuerySet: Recent transactions
        """
        return cls.objects.select_related('user').order_by('-created_at')[:limit]

    @classmethod
    def get_transactions_by_status(cls, status, limit=100):
        """
        Get transactions by status with optimized query

        Args:
            status: Transaction status
            limit: Number of transactions to return

        Returns:
            QuerySet: Transactions with specified status
        """
        return cls.objects.filter(status=status).order_by('-created_at')[:limit]

    def __str__(self):
        return f"{self.transaction_id} - {self.status}"

from django.db import models
from django.utils import timezone


class Transaction(models.Model):
    """Transaction model for tracking middleware operations"""

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    transaction_id = models.CharField(max_length=100, unique=True, null=False)
    source_system = models.CharField(max_length=50, null=False)
    target_system = models.CharField(max_length=50, null=False)
    transaction_type = models.CharField(max_length=50, null=False)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="pending")
    amount = models.FloatField(null=True, blank=True)
    currency = models.CharField(max_length=10, null=True, blank=True)
    user_id = models.CharField(max_length=100, null=True, blank=True)
    request_data = models.TextField(null=True, blank=True)
    response_data = models.TextField(null=True, blank=True)
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
        ]

    def __str__(self):
        return f"{self.transaction_id} - {self.status}"

    def mark_completed(self, response_data):
        """Mark transaction as completed with response data"""
        self.status = "completed"
        self.response_data = response_data
        self.updated_at = timezone.now()
        self.save()

    def mark_failed(self, error_message):
        """Mark transaction as failed with error message"""
        self.status = "failed"
        self.error_message = error_message
        self.updated_at = timezone.now()
        self.save()

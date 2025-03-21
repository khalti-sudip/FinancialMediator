from django.db import models
from django.utils import timezone
from banking_api.models.user import User

class AuditLog(models.Model):
    """Audit log for tracking operations and changes"""
    ACTION_CHOICES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('api_request', 'API Request'),
    ]
    
    action = models.CharField(max_length=100, choices=ACTION_CHOICES, null=False)
    resource_type = models.CharField(max_length=50, null=False)
    resource_id = models.CharField(max_length=100, null=False)
    user = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='audit_logs'
    )
    details = models.TextField(null=True, blank=True)
    ip_address = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'audit_logs'
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['action']),
            models.Index(fields=['resource_type']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f'{self.action} - {self.resource_type} - {self.resource_id}'
    
    @classmethod
    def log_action(cls, action, resource_type, resource_id, user=None, details=None, ip_address=None):
        """Helper method to create audit log entries"""
        return cls.objects.create(
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            user=user,
            details=details,
            ip_address=ip_address
        )
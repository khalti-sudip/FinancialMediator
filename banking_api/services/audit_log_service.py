"""
Audit Log service module for banking_api.

This service handles all audit logging business logic.
"""

from typing import Optional, List
from datetime import datetime
from django.db import transaction
from banking_api.models import AuditLog
from banking_api.exceptions import AuditLogError

class AuditLogService:
    """Service class for audit log operations."""
    
    def create_audit_log(self, 
                         user_id: int, 
                         action: str, 
                         details: dict,
                         ip_address: str = None,
                         user_agent: str = None) -> AuditLog:
        """
        Create a new audit log entry.
        
        Args:
            user_id: The ID of the user performing the action
            action: The action being performed
            details: Additional details about the action
            ip_address: The IP address of the request (optional)
            user_agent: The user agent string (optional)
            
        Returns:
            The created AuditLog instance
            
        Raises:
            AuditLogError: If audit log creation fails
        """
        try:
            with transaction.atomic():
                audit_log = AuditLog.objects.create(
                    user_id=user_id,
                    action=action,
                    details=details,
                    ip_address=ip_address,
                    user_agent=user_agent
                )
                return audit_log
        except Exception as e:
            raise AuditLogError(f"Failed to create audit log: {str(e)}")
    
    def get_audit_logs(self, 
                       user_id: int = None,
                       action: str = None,
                       start_date: datetime = None,
                       end_date: datetime = None,
                       limit: int = 100) -> List[AuditLog]:
        """
        Get audit logs based on filters.
        
        Args:
            user_id: Filter by user ID (optional)
            action: Filter by action (optional)
            start_date: Filter logs after this date (optional)
            end_date: Filter logs before this date (optional)
            limit: Maximum number of logs to return
            
        Returns:
            List of AuditLog instances
            
        Raises:
            AuditLogError: If audit log retrieval fails
        """
        try:
            queryset = AuditLog.objects.all()
            
            if user_id:
                queryset = queryset.filter(user_id=user_id)
            if action:
                queryset = queryset.filter(action=action)
            if start_date:
                queryset = queryset.filter(created_at__gte=start_date)
            if end_date:
                queryset = queryset.filter(created_at__lte=end_date)
            
            return list(queryset.order_by('-created_at')[:limit])
        except Exception as e:
            raise AuditLogError(f"Failed to retrieve audit logs: {str(e)}")
    
    def get_user_audit_logs(self, 
                           user_id: int,
                           start_date: datetime = None,
                           end_date: datetime = None,
                           limit: int = 100) -> List[AuditLog]:
        """
        Get audit logs for a specific user.
        
        Args:
            user_id: The ID of the user
            start_date: Filter logs after this date (optional)
            end_date: Filter logs before this date (optional)
            limit: Maximum number of logs to return
            
        Returns:
            List of AuditLog instances
            
        Raises:
            AuditLogError: If audit log retrieval fails
        """
        return self.get_audit_logs(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            limit=limit
        )
    
    def get_action_audit_logs(self, 
                             action: str,
                             start_date: datetime = None,
                             end_date: datetime = None,
                             limit: int = 100) -> List[AuditLog]:
        """
        Get audit logs for a specific action.
        
        Args:
            action: The action to filter by
            start_date: Filter logs after this date (optional)
            end_date: Filter logs before this date (optional)
            limit: Maximum number of logs to return
            
        Returns:
            List of AuditLog instances
            
        Raises:
            AuditLogError: If audit log retrieval fails
        """
        return self.get_audit_logs(
            action=action,
            start_date=start_date,
            end_date=end_date,
            limit=limit
        )
    
    def get_recent_audit_logs(self, limit: int = 100) -> List[AuditLog]:
        """
        Get most recent audit logs.
        
        Args:
            limit: Maximum number of logs to return
            
        Returns:
            List of AuditLog instances
            
        Raises:
            AuditLogError: If audit log retrieval fails
        """
        return self.get_audit_logs(limit=limit)
    
    def get_audit_log_by_id(self, log_id: int) -> AuditLog:
        """
        Get an audit log by ID.
        
        Args:
            log_id: The ID of the audit log
            
        Returns:
            The AuditLog instance
            
        Raises:
            AuditLogError: If the audit log is not found
        """
        try:
            return AuditLog.objects.get(pk=log_id)
        except AuditLog.DoesNotExist:
            raise AuditLogError(f"Audit log with ID {log_id} not found")

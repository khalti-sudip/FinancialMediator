"""
Tests for the audit log service.
"""

import pytest
from datetime import datetime
from django.contrib.auth import get_user_model
from banking_api.services.audit_log_service import AuditLogService
from banking_api.exceptions import AuditLogError

UserModel = get_user_model()

def test_create_audit_log(db):
    """Test creating a new audit log."""
    audit_log_service = AuditLogService()
    
    # Create a user
    user = UserModel.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="password123"
    )
    
    # Create audit log
    audit_log = audit_log_service.create_audit_log(
        user_id=user.id,
        action="LOGIN",
        details={"ip_address": "127.0.0.1"},
        ip_address="127.0.0.1",
        user_agent="Test Agent"
    )
    
    assert audit_log.user == user
    assert audit_log.action == "LOGIN"
    assert audit_log.details == {"ip_address": "127.0.0.1"}
    assert audit_log.ip_address == "127.0.0.1"
    assert audit_log.user_agent == "Test Agent"

def test_get_audit_logs(db):
    """Test getting audit logs with filters."""
    audit_log_service = AuditLogService()
    
    # Create a user and multiple audit logs
    user = UserModel.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="password123"
    )
    
    audit_log_service.create_audit_log(
        user_id=user.id,
        action="LOGIN",
        details={"ip_address": "127.0.0.1"}
    )
    audit_log_service.create_audit_log(
        user_id=user.id,
        action="LOGOUT",
        details={"ip_address": "127.0.0.1"}
    )
    
    # Get logs by user
    user_logs = audit_log_service.get_user_audit_logs(user.id)
    assert len(user_logs) == 2
    
    # Get logs by action
    login_logs = audit_log_service.get_action_audit_logs("LOGIN")
    assert len(login_logs) == 1
    
    # Get recent logs
    recent_logs = audit_log_service.get_recent_audit_logs(limit=1)
    assert len(recent_logs) == 1

def test_get_nonexistent_audit_log(db):
    """Test getting a non-existent audit log."""
    audit_log_service = AuditLogService()
    
    with pytest.raises(AuditLogError):
        audit_log_service.get_audit_log_by_id(9999)

def test_get_audit_logs_with_date_range(db):
    """Test getting audit logs with date range."""
    audit_log_service = AuditLogService()
    
    # Create a user and audit logs
    user = UserModel.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="password123"
    )
    
    # Create logs at different times
    audit_log_service.create_audit_log(
        user_id=user.id,
        action="LOGIN",
        details={"ip_address": "127.0.0.1"}
    )
    
    # Get logs within a date range
    start_date = datetime.now()
    audit_log_service.create_audit_log(
        user_id=user.id,
        action="LOGOUT",
        details={"ip_address": "127.0.0.1"}
    )
    
    logs = audit_log_service.get_audit_logs(
        start_date=start_date,
        limit=10
    )
    
    assert len(logs) == 1  # Only the logout log should be returned

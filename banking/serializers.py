"""
Banking Serializers Module.

This module provides serializers for:
- Bank account management
- Transaction processing
- Payment method handling
- Bank integration configuration
"""

from rest_framework import serializers
from django.utils import timezone
from .models import BankAccount, Transaction, PaymentMethod, BankIntegration

class BankAccountSerializer(serializers.ModelSerializer):
    """Serializer for bank account data."""
    
    class Meta:
        model = BankAccount
        fields = [
            "id",
            "account_number",
            "bank_name",
            "branch_code",
            "holder_name",
            "holder_type",
            "is_active",
            "is_verified",
            "account_type",
            "currency",
            "current_balance",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "is_verified",
            "current_balance",
            "created_at",
            "updated_at",
        ]
    
    def validate_account_number(self, value):
        """Validate account number format."""
        # Remove any whitespace
        value = "".join(value.split())
        
        # Check length
        if len(value) < 8 or len(value) > 20:
            raise serializers.ValidationError(
                "Account number must be between 8 and 20 characters"
            )
        
        # Check if numeric
        if not value.isdigit():
            raise serializers.ValidationError(
                "Account number must contain only digits"
            )
        
        return value

class TransactionSerializer(serializers.ModelSerializer):
    """Serializer for transaction data."""
    
    class Meta:
        model = Transaction
        fields = [
            "id",
            "transaction_id",
            "reference_id",
            "amount",
            "currency",
            "transaction_type",
            "status",
            "source_account",
            "destination_account",
            "description",
            "metadata",
            "error_code",
            "error_message",
            "created_at",
            "updated_at",
            "completed_at",
        ]
        read_only_fields = [
            "id",
            "transaction_id",
            "status",
            "error_code",
            "error_message",
            "created_at",
            "updated_at",
            "completed_at",
        ]
    
    def validate(self, data):
        """Validate transaction data."""
        # Check amount is positive
        if data.get("amount", 0) <= 0:
            raise serializers.ValidationError({
                "amount": "Amount must be positive"
            })
        
        # Ensure source and destination accounts use same currency
        if data.get("destination_account"):
            if (data["source_account"].currency != 
                data["destination_account"].currency):
                raise serializers.ValidationError(
                    "Source and destination accounts must use same currency"
                )
        
        return data

class PaymentMethodSerializer(serializers.ModelSerializer):
    """Serializer for payment method data."""
    
    class Meta:
        model = PaymentMethod
        fields = [
            "id",
            "name",
            "method_type",
            "provider",
            "provider_method_id",
            "is_active",
            "is_default",
            "user",
            "last_four",
            "expiry_date",
            "created_at",
            "updated_at",
            "last_used_at",
        ]
        read_only_fields = [
            "id",
            "last_four",
            "created_at",
            "updated_at",
            "last_used_at",
        ]
    
    def validate(self, data):
        """Validate payment method data."""
        # Check expiry date is in future
        if data.get("expiry_date"):
            if data["expiry_date"] < timezone.now().date():
                raise serializers.ValidationError({
                    "expiry_date": "Expiry date must be in the future"
                })
        
        return data

class BankIntegrationSerializer(serializers.ModelSerializer):
    """Serializer for bank integration data."""
    
    class Meta:
        model = BankIntegration
        fields = [
            "id",
            "bank_name",
            "bank_code",
            "is_active",
            "integration_type",
            "api_base_url",
            "api_version",
            "settings",
            "rate_limits",
            "created_at",
            "updated_at",
            "last_sync_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "last_sync_at",
        ]
        extra_kwargs = {
            "auth_credentials": {"write_only": True},
        }
    
    def validate_settings(self, value):
        """Validate integration settings."""
        required_fields = ["timeout", "retry_count", "webhook_url"]
        
        for field in required_fields:
            if field not in value:
                raise serializers.ValidationError(
                    f"Missing required setting: {field}"
                )
        
        return value

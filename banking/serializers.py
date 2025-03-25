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

class PaymentRequestSerializer(serializers.Serializer):
    """Serializer for payment request data."""
    
    account_id = serializers.UUIDField(required=True)
    payment_method_id = serializers.UUIDField(required=True)
    amount = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        min_value=0.01,
        required=True
    )
    currency = serializers.CharField(max_length=3, required=True)
    description = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True
    )
    metadata = serializers.DictField(
        required=False,
        allow_null=True
    )
    
    def validate_currency(self, value):
        """Validate currency code."""
        value = value.upper()
        if len(value) != 3:
            raise serializers.ValidationError(
                "Currency code must be 3 characters"
            )
        return value

class PaymentResponseSerializer(serializers.ModelSerializer):
    """Serializer for payment response data."""
    
    payment_method = PaymentMethodSerializer()
    provider_name = serializers.CharField(source='provider.name')
    
    class Meta:
        model = Transaction
        fields = [
            "id",
            "reference",
            "amount",
            "currency",
            "status",
            "payment_method",
            "provider_name",
            "error_message",
            "metadata",
            "created_at",
            "completed_at",
        ]

class PaymentRefundSerializer(serializers.Serializer):
    """Serializer for payment refund data."""
    
    reference = serializers.CharField(required=True)
    amount = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        min_value=0.01,
        required=False
    )
    reason = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True
    )
    metadata = serializers.DictField(
        required=False,
        allow_null=True
    )
    
    def validate(self, data):
        """Validate refund data."""
        try:
            transaction = Transaction.objects.get(
                reference=data["reference"]
            )
            
            # Check if transaction can be refunded
            if transaction.status != "completed":
                raise serializers.ValidationError(
                    "Only completed transactions can be refunded"
                )
            
            # Check refund amount
            refund_amount = data.get("amount", transaction.amount)
            if refund_amount > transaction.amount:
                raise serializers.ValidationError(
                    "Refund amount cannot exceed transaction amount"
                )
            
            # Add transaction to validated data
            data["transaction"] = transaction
            
        except Transaction.DoesNotExist:
            raise serializers.ValidationError("Invalid transaction reference")
        
        return data

class PaymentMethodTokenSerializer(serializers.Serializer):
    """Serializer for payment method tokenization."""
    
    provider_id = serializers.UUIDField(required=True)
    token_data = serializers.DictField(required=True)
    save_for_future = serializers.BooleanField(default=False)
    set_default = serializers.BooleanField(default=False)
    metadata = serializers.DictField(
        required=False,
        allow_null=True
    )
    
    def validate_token_data(self, value):
        """Validate token data."""
        required_fields = ["token", "type"]
        for field in required_fields:
            if field not in value:
                raise serializers.ValidationError(
                    f"Missing required field: {field}"
                )
        return value

class PaymentMethodVerificationSerializer(serializers.Serializer):
    """Serializer for payment method verification."""
    
    verification_data = serializers.DictField(required=True)
    metadata = serializers.DictField(
        required=False,
        allow_null=True
    )
    
    def validate_verification_data(self, value):
        """Validate verification data."""
        required_fields = ["code", "method"]
        for field in required_fields:
            if field not in value:
                raise serializers.ValidationError(
                    f"Missing required field: {field}"
                )
        return value

"""
Transaction serializer for FinancialMediator banking API.

This serializer handles the serialization and validation of transaction data,
including request and response formats for financial transactions.

Key Features:
1. Transaction data validation
2. Status tracking
3. Error handling
4. Response formatting
"""

from rest_framework import serializers
from banking_api.models import Transaction
from django.core.exceptions import ValidationError
import uuid

class TransactionSerializer(serializers.ModelSerializer):
    """
    Serializer for Transaction model.
    
    Handles serialization and validation of transaction data.
    
    Fields:
    - id: Transaction UUID (read-only)
    - transaction_id: Unique transaction identifier
    - source_system: Source system identifier
    - target_system: Target system identifier
    - transaction_type: Type of transaction
    - status: Transaction status
    - amount: Transaction amount
    - currency: Currency code
    - user_id: User identifier
    - request_data: Request payload
    - response_data: Response payload
    - error_message: Error details
    - created_at: Creation timestamp (read-only)
    - updated_at: Last update timestamp (read-only)
    """
    
    class Meta:
        """Serializer metadata."""
        model = Transaction
        fields = [
            "id",
            "transaction_id",
            "source_system",
            "target_system",
            "transaction_type",
            "status",
            "amount",
            "currency",
            "user_id",
            "request_data",
            "response_data",
            "error_message",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
    
    def validate(self, data):
        """
        Additional validation for transactions.
        
        Validates:
        1. Transaction amount
        2. Currency format
        3. Required fields based on transaction type
        
        Args:
            data: Transaction data to validate
            
        Returns:
            dict: Validated data
            
        Raises:
            ValidationError: If validation fails
        """
        # Validate amount
        if data.get('amount', 0) <= 0:
            raise serializers.ValidationError("Transaction amount must be positive")
            
        # Validate currency
        currency = data.get('currency')
        if currency and len(currency) != 3:
            raise serializers.ValidationError("Currency code must be 3 characters")
            
        # Validate transaction type specific fields
        transaction_type = data.get('transaction_type')
        if transaction_type:
            required_fields = {
                'deposit': ['source_system'],
                'withdrawal': ['target_system'],
                'transfer': ['source_system', 'target_system'],
                'payment': ['target_system'],
                'refund': ['source_system']
            }
            
            missing_fields = []
            for field in required_fields.get(transaction_type, []):
                if not data.get(field):
                    missing_fields.append(field)
                    
            if missing_fields:
                raise serializers.ValidationError(
                    f"Missing required fields for {transaction_type}: {missing_fields}"
                )
        
        return data
    
    def create(self, validated_data):
        """
        Create a new transaction.
        
        Args:
            validated_data: Validated transaction data
            
        Returns:
            Transaction: Created transaction instance
        """
        # Generate unique transaction ID
        transaction_id = str(uuid.uuid4())
        validated_data['transaction_id'] = transaction_id
        
        # Set default status
        validated_data.setdefault('status', 'pending')
        
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """
        Update an existing transaction.
        
        Args:
            instance: Existing transaction instance
            validated_data: Validated update data
            
        Returns:
            Transaction: Updated transaction instance
        """
        # Prevent updating transaction type
        if 'transaction_type' in validated_data:
            raise serializers.ValidationError(
                "Transaction type cannot be changed after creation"
            )
            
        return super().update(instance, validated_data)

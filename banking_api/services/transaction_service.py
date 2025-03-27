"""
Transaction service module for banking_api.

This service handles all transaction-related business logic.
"""

from typing import Optional
from django.db import transaction
from banking_api.models import Transaction, User
from banking_api.exceptions import InsufficientBalanceError, TransactionError

class TransactionService:
    """Service class for transaction operations."""
    
    def create_transaction(self, user: User, amount: float, description: str) -> Transaction:
        """
        Create a new transaction.
        
        Args:
            user: The user initiating the transaction
            amount: The transaction amount
            description: Description of the transaction
            
        Returns:
            The created Transaction instance
            
        Raises:
            InsufficientBalanceError: If the user has insufficient balance
            TransactionError: If the transaction fails
        """
        if user.balance < amount:
            raise InsufficientBalanceError("Insufficient balance for transaction")
            
        with transaction.atomic():
            try:
                transaction = Transaction.objects.create(
                    user=user,
                    amount=amount,
                    description=description
                )
                user.balance -= amount
                user.save()
                return transaction
            except Exception as e:
                raise TransactionError(f"Transaction failed: {str(e)}")
    
    def get_transaction(self, transaction_id: int) -> Transaction:
        """
        Get a transaction by ID.
        
        Args:
            transaction_id: The ID of the transaction to retrieve
            
        Returns:
            The Transaction instance
            
        Raises:
            TransactionError: If the transaction is not found
        """
        try:
            return Transaction.objects.get(pk=transaction_id)
        except Transaction.DoesNotExist:
            raise TransactionError(f"Transaction with ID {transaction_id} not found")
    
    def update_transaction_status(self, transaction_id: int, status: str) -> Transaction:
        """
        Update a transaction's status.
        
        Args:
            transaction_id: The ID of the transaction to update
            status: The new status
            
        Returns:
            The updated Transaction instance
            
        Raises:
            TransactionError: If the transaction is not found or status is invalid
        """
        try:
            transaction = Transaction.objects.get(pk=transaction_id)
            transaction.status = status
            transaction.save()
            return transaction
        except Transaction.DoesNotExist:
            raise TransactionError(f"Transaction with ID {transaction_id} not found")
        except ValueError:
            raise TransactionError(f"Invalid status: {status}")

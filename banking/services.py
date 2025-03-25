"""
Banking Services Module.

This module provides services for:
- Transaction processing
- Balance management
- Account operations
- Payment processing
"""

from decimal import Decimal
from typing import Dict, Any, Optional, List
from django.db import transaction
from django.utils import timezone
from django.conf import settings
import logging

from .models import BankAccount, Transaction, PaymentMethod
from providers.models import Provider

logger = logging.getLogger(__name__)

class TransactionService:
    """Service for processing financial transactions."""
    
    def __init__(self):
        """Initialize service."""
        self.logger = logging.getLogger(__name__)
    
    @transaction.atomic
    def create_transaction(
        self,
        account: BankAccount,
        amount: Decimal,
        transaction_type: str,
        currency: str,
        reference: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Transaction:
        """
        Create a new transaction.
        
        Args:
            account: Bank account
            amount: Transaction amount
            transaction_type: Type of transaction
            currency: Currency code
            reference: External reference
            metadata: Additional data
            **kwargs: Additional fields
            
        Returns:
            Transaction: Created transaction
        """
        try:
            # Validate amount
            if amount <= 0:
                raise ValueError("Amount must be positive")
            
            # Validate currency
            if currency != account.currency:
                raise ValueError("Currency mismatch")
            
            # Create transaction
            transaction = Transaction.objects.create(
                account=account,
                amount=amount,
                type=transaction_type,
                currency=currency,
                reference=reference,
                metadata=metadata or {},
                status="pending",
                **kwargs
            )
            
            # Update balance
            if transaction_type in ["deposit", "credit"]:
                account.balance += amount
            elif transaction_type in ["withdrawal", "debit"]:
                if account.balance < amount:
                    raise ValueError("Insufficient funds")
                account.balance -= amount
            
            account.save()
            
            # Update transaction
            transaction.status = "completed"
            transaction.completed_at = timezone.now()
            transaction.save()
            
            return transaction
            
        except Exception as e:
            self.logger.error(
                f"Failed to create transaction: {str(e)}",
                exc_info=True
            )
            raise
    
    def get_transaction(
        self,
        reference: str
    ) -> Optional[Transaction]:
        """
        Get transaction by reference.
        
        Args:
            reference: Transaction reference
            
        Returns:
            Transaction: Found transaction or None
        """
        try:
            return Transaction.objects.get(reference=reference)
        except Transaction.DoesNotExist:
            return None
    
    def cancel_transaction(
        self,
        transaction: Transaction,
        reason: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Cancel a transaction.
        
        Args:
            transaction: Transaction to cancel
            reason: Cancellation reason
            metadata: Additional data
            
        Returns:
            bool: True if cancelled
        """
        try:
            # Check if can cancel
            if transaction.status not in ["pending", "processing"]:
                raise ValueError("Transaction cannot be cancelled")
            
            # Update transaction
            transaction.status = "cancelled"
            transaction.error_message = reason
            transaction.metadata.update(metadata or {})
            transaction.save()
            
            # Reverse balance change
            account = transaction.account
            if transaction.type in ["deposit", "credit"]:
                account.balance -= transaction.amount
            elif transaction.type in ["withdrawal", "debit"]:
                account.balance += transaction.amount
            
            account.save()
            
            return True
            
        except Exception as e:
            self.logger.error(
                f"Failed to cancel transaction: {str(e)}",
                exc_info=True
            )
            return False

class PaymentService:
    """Service for processing payments."""
    
    def __init__(self):
        """Initialize service."""
        self.logger = logging.getLogger(__name__)
    
    def process_payment(
        self,
        account: BankAccount,
        amount: Decimal,
        currency: str,
        payment_method: PaymentMethod,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Transaction:
        """
        Process a payment.
        
        Args:
            account: Bank account
            amount: Payment amount
            currency: Currency code
            payment_method: Payment method
            metadata: Additional data
            
        Returns:
            Transaction: Payment transaction
        """
        try:
            # Get provider
            provider = payment_method.provider
            if not provider.is_active:
                raise ValueError("Payment provider is not active")
            
            # Create payment
            payment_data = {
                "amount": str(amount),
                "currency": currency,
                "payment_method": payment_method.external_id,
                "description": metadata.get("description", "Payment"),
                "metadata": metadata or {},
            }
            
            # Call provider API
            response = provider.create_payment(payment_data)
            
            # Create transaction
            transaction = Transaction.objects.create(
                account=account,
                amount=amount,
                type="payment",
                currency=currency,
                reference=response["payment_id"],
                provider=provider,
                payment_method=payment_method,
                metadata={
                    **metadata or {},
                    "provider_response": response,
                },
                status="pending",
            )
            
            return transaction
            
        except Exception as e:
            self.logger.error(
                f"Failed to process payment: {str(e)}",
                exc_info=True
            )
            raise

class AccountService:
    """Service for managing bank accounts."""
    
    def __init__(self):
        """Initialize service."""
        self.logger = logging.getLogger(__name__)
    
    @transaction.atomic
    def create_account(
        self,
        user_id: str,
        currency: str,
        account_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> BankAccount:
        """
        Create a new bank account.
        
        Args:
            user_id: User ID
            currency: Currency code
            account_type: Type of account
            metadata: Additional data
            
        Returns:
            BankAccount: Created account
        """
        try:
            # Create account
            account = BankAccount.objects.create(
                user_id=user_id,
                currency=currency,
                account_type=account_type,
                balance=Decimal("0"),
                is_active=True,
                metadata=metadata or {},
            )
            
            return account
            
        except Exception as e:
            self.logger.error(
                f"Failed to create account: {str(e)}",
                exc_info=True
            )
            raise
    
    def get_account_balance(
        self,
        account: BankAccount,
        refresh: bool = False
    ) -> Decimal:
        """
        Get account balance.
        
        Args:
            account: Bank account
            refresh: Whether to refresh from provider
            
        Returns:
            Decimal: Account balance
        """
        try:
            if refresh and account.provider:
                # Get balance from provider
                response = account.provider.get_balance(
                    account.external_id
                )
                
                # Update balance
                account.balance = Decimal(response["balance"])
                account.last_synced_at = timezone.now()
                account.save()
            
            return account.balance
            
        except Exception as e:
            self.logger.error(
                f"Failed to get balance: {str(e)}",
                exc_info=True
            )
            return account.balance
    
    def get_transaction_history(
        self,
        account: BankAccount,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        transaction_type: Optional[str] = None,
        limit: int = 100
    ) -> List[Transaction]:
        """
        Get account transaction history.
        
        Args:
            account: Bank account
            start_date: Start date
            end_date: End date
            transaction_type: Type filter
            limit: Max results
            
        Returns:
            list: Transaction list
        """
        try:
            # Build query
            queryset = Transaction.objects.filter(
                account=account
            )
            
            if start_date:
                queryset = queryset.filter(created_at__gte=start_date)
            
            if end_date:
                queryset = queryset.filter(created_at__lte=end_date)
            
            if transaction_type:
                queryset = queryset.filter(type=transaction_type)
            
            # Get transactions
            return queryset.order_by("-created_at")[:limit]
            
        except Exception as e:
            self.logger.error(
                f"Failed to get history: {str(e)}",
                exc_info=True
            )
            return []

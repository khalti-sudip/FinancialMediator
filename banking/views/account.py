"""
Banking Account Views Module.

This module provides views for:
- Account management
- Balance operations
- Transaction history
"""

from decimal import Decimal
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db import transaction
import logging

from ..models import BankAccount, Transaction
from ..serializers import (
    BankAccountSerializer,
    TransactionSerializer,
    AccountBalanceSerializer,
    AccountStatementSerializer,
)
from ..services import AccountService, TransactionService
from ..permissions import IsAccountOwner

logger = logging.getLogger(__name__)

class BankAccountViewSet(viewsets.ModelViewSet):
    """ViewSet for managing bank accounts."""
    
    queryset = BankAccount.objects.all()
    serializer_class = BankAccountSerializer
    permission_classes = [IsAuthenticated, IsAccountOwner]
    
    def get_queryset(self):
        """Filter queryset by user."""
        return self.queryset.filter(user_id=self.request.user.id)
    
    def perform_create(self, serializer):
        """Create bank account."""
        try:
            # Get service
            service = AccountService()
            
            # Create account
            account = service.create_account(
                user_id=self.request.user.id,
                currency=serializer.validated_data["currency"],
                account_type=serializer.validated_data["account_type"],
                metadata=serializer.validated_data.get("metadata"),
            )
            
            # Update serializer
            serializer.instance = account
            
        except Exception as e:
            logger.error(
                f"Failed to create account: {str(e)}",
                exc_info=True
            )
            raise
    
    @action(detail=True, methods=["get"])
    def balance(self, request, pk=None):
        """Get account balance."""
        try:
            # Get account
            account = self.get_object()
            
            # Get service
            service = AccountService()
            
            # Get balance
            balance = service.get_account_balance(
                account,
                refresh=request.query_params.get("refresh") == "true"
            )
            
            # Return response
            return Response({
                "balance": str(balance),
                "currency": account.currency,
                "last_synced": account.last_synced_at,
            })
            
        except Exception as e:
            logger.error(
                f"Failed to get balance: {str(e)}",
                exc_info=True
            )
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=["post"])
    def deposit(self, request, pk=None):
        """Deposit funds to account."""
        try:
            # Get account
            account = self.get_object()
            
            # Validate data
            amount = Decimal(request.data.get("amount"))
            if amount <= 0:
                raise ValueError("Amount must be positive")
            
            # Get service
            service = TransactionService()
            
            # Create transaction
            transaction = service.create_transaction(
                account=account,
                amount=amount,
                transaction_type="deposit",
                currency=account.currency,
                reference=request.data.get("reference"),
                metadata=request.data.get("metadata"),
            )
            
            # Return response
            return Response(
                TransactionSerializer(transaction).data,
                status=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            logger.error(
                f"Failed to deposit: {str(e)}",
                exc_info=True
            )
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=["post"])
    def withdraw(self, request, pk=None):
        """Withdraw funds from account."""
        try:
            # Get account
            account = self.get_object()
            
            # Validate data
            amount = Decimal(request.data.get("amount"))
            if amount <= 0:
                raise ValueError("Amount must be positive")
            
            # Get service
            service = TransactionService()
            
            # Create transaction
            transaction = service.create_transaction(
                account=account,
                amount=amount,
                transaction_type="withdrawal",
                currency=account.currency,
                reference=request.data.get("reference"),
                metadata=request.data.get("metadata"),
            )
            
            # Return response
            return Response(
                TransactionSerializer(transaction).data,
                status=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            logger.error(
                f"Failed to withdraw: {str(e)}",
                exc_info=True
            )
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=["get"])
    def transactions(self, request, pk=None):
        """Get account transactions."""
        try:
            # Get account
            account = self.get_object()
            
            # Get service
            service = AccountService()
            
            # Get transactions
            transactions = service.get_transaction_history(
                account=account,
                start_date=request.query_params.get("start_date"),
                end_date=request.query_params.get("end_date"),
                transaction_type=request.query_params.get("type"),
                limit=int(request.query_params.get("limit", 100)),
            )
            
            # Return response
            return Response(
                TransactionSerializer(transactions, many=True).data
            )
            
        except Exception as e:
            logger.error(
                f"Failed to get transactions: {str(e)}",
                exc_info=True
            )
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=["get"])
    def statement(self, request, pk=None):
        """Get account statement."""
        try:
            # Get account
            account = self.get_object()
            
            # Get date range
            start_date = request.query_params.get(
                "start_date",
                timezone.now().replace(day=1).date().isoformat()
            )
            end_date = request.query_params.get(
                "end_date",
                timezone.now().date().isoformat()
            )
            
            # Get transactions
            transactions = Transaction.objects.filter(
                account=account,
                created_at__date__range=[start_date, end_date]
            ).order_by("created_at")
            
            # Calculate summary
            opening_balance = Decimal("0")
            closing_balance = account.balance
            total_credits = sum(
                t.amount for t in transactions
                if t.type in ["deposit", "credit"]
            )
            total_debits = sum(
                t.amount for t in transactions
                if t.type in ["withdrawal", "debit"]
            )
            
            # Return response
            return Response({
                "account": BankAccountSerializer(account).data,
                "start_date": start_date,
                "end_date": end_date,
                "opening_balance": str(opening_balance),
                "closing_balance": str(closing_balance),
                "total_credits": str(total_credits),
                "total_debits": str(total_debits),
                "transactions": TransactionSerializer(
                    transactions,
                    many=True
                ).data,
            })
            
        except Exception as e:
            logger.error(
                f"Failed to get statement: {str(e)}",
                exc_info=True
            )
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

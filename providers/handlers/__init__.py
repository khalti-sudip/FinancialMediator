"""
Provider Handlers Package.

This package provides webhook handlers for:
- Payment events
- Wallet transactions
- Bank operations
- KYC verifications
"""

from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

# Payment handlers
def handle_payment_success(data: Dict[str, Any]) -> bool:
    """Handle successful payment."""
    try:
        from banking.models import Transaction
        
        # Update transaction
        transaction = Transaction.objects.get(
            reference=data["transaction_id"]
        )
        transaction.status = "completed"
        transaction.metadata.update(data)
        transaction.save()
        
        return True
        
    except Exception as e:
        logger.error("Payment success handler failed", exc_info=True)
        return False

def handle_payment_failure(data: Dict[str, Any]) -> bool:
    """Handle failed payment."""
    try:
        from banking.models import Transaction
        
        # Update transaction
        transaction = Transaction.objects.get(
            reference=data["transaction_id"]
        )
        transaction.status = "failed"
        transaction.error_message = data.get("error")
        transaction.metadata.update(data)
        transaction.save()
        
        return True
        
    except Exception as e:
        logger.error("Payment failure handler failed", exc_info=True)
        return False

def handle_payment_refund(data: Dict[str, Any]) -> bool:
    """Handle payment refund."""
    try:
        from banking.models import Transaction
        
        # Create refund transaction
        Transaction.objects.create(
            type="refund",
            status="completed",
            amount=data["amount"],
            currency=data["currency"],
            reference=data["refund_id"],
            parent_reference=data["transaction_id"],
            metadata=data,
        )
        
        return True
        
    except Exception as e:
        logger.error("Payment refund handler failed", exc_info=True)
        return False

# Wallet handlers
def handle_wallet_deposit(data: Dict[str, Any]) -> bool:
    """Handle wallet deposit."""
    try:
        from banking.models import Transaction, BankAccount
        
        # Create deposit transaction
        Transaction.objects.create(
            type="deposit",
            status="completed",
            amount=data["amount"],
            currency=data["currency"],
            reference=data["deposit_id"],
            metadata=data,
        )
        
        # Update balance
        account = BankAccount.objects.get(
            wallet_id=data["wallet_id"]
        )
        account.balance += data["amount"]
        account.save()
        
        return True
        
    except Exception as e:
        logger.error("Wallet deposit handler failed", exc_info=True)
        return False

def handle_wallet_withdrawal(data: Dict[str, Any]) -> bool:
    """Handle wallet withdrawal."""
    try:
        from banking.models import Transaction, BankAccount
        
        # Create withdrawal transaction
        Transaction.objects.create(
            type="withdrawal",
            status="completed",
            amount=data["amount"],
            currency=data["currency"],
            reference=data["withdrawal_id"],
            metadata=data,
        )
        
        # Update balance
        account = BankAccount.objects.get(
            wallet_id=data["wallet_id"]
        )
        account.balance -= data["amount"]
        account.save()
        
        return True
        
    except Exception as e:
        logger.error("Wallet withdrawal handler failed", exc_info=True)
        return False

# Bank handlers
def handle_bank_transfer(data: Dict[str, Any]) -> bool:
    """Handle bank transfer."""
    try:
        from banking.models import Transaction
        
        # Create transfer transaction
        Transaction.objects.create(
            type="transfer",
            status="completed",
            amount=data["amount"],
            currency=data["currency"],
            reference=data["transfer_id"],
            metadata=data,
        )
        
        return True
        
    except Exception as e:
        logger.error("Bank transfer handler failed", exc_info=True)
        return False

def handle_bank_statement(data: Dict[str, Any]) -> bool:
    """Handle bank statement."""
    try:
        from banking.models import Transaction
        
        # Process statement entries
        for entry in data["entries"]:
            Transaction.objects.create(
                type=entry["type"],
                status="completed",
                amount=entry["amount"],
                currency=entry["currency"],
                reference=entry["reference"],
                metadata=entry,
            )
        
        return True
        
    except Exception as e:
        logger.error("Bank statement handler failed", exc_info=True)
        return False

# KYC handlers
def handle_kyc_verification(data: Dict[str, Any]) -> bool:
    """Handle KYC verification."""
    try:
        from users.models import UserProfile
        
        # Update verification status
        profile = UserProfile.objects.get(
            reference=data["user_reference"]
        )
        profile.kyc_status = data["status"]
        profile.kyc_details.update(data)
        profile.save()
        
        return True
        
    except Exception as e:
        logger.error("KYC verification handler failed", exc_info=True)
        return False

def handle_kyc_document(data: Dict[str, Any]) -> bool:
    """Handle KYC document."""
    try:
        from users.models import UserDocument
        
        # Create document record
        UserDocument.objects.create(
            user_reference=data["user_reference"],
            type=data["document_type"],
            status=data["status"],
            metadata=data,
        )
        
        return True
        
    except Exception as e:
        logger.error("KYC document handler failed", exc_info=True)
        return False

# Handler mappings
payment_handlers = {
    "payment.success": handle_payment_success,
    "payment.failure": handle_payment_failure,
    "payment.refund": handle_payment_refund,
    "default": handle_payment_success,
}

wallet_handlers = {
    "wallet.deposit": handle_wallet_deposit,
    "wallet.withdrawal": handle_wallet_withdrawal,
    "default": handle_wallet_deposit,
}

bank_handlers = {
    "bank.transfer": handle_bank_transfer,
    "bank.statement": handle_bank_statement,
    "default": handle_bank_transfer,
}

kyc_handlers = {
    "kyc.verification": handle_kyc_verification,
    "kyc.document": handle_kyc_document,
    "default": handle_kyc_verification,
}

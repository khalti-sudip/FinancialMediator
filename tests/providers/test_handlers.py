"""
Provider Handlers Test Module.

This module tests:
- Payment handlers
- Wallet handlers
- Bank handlers
- KYC handlers
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from banking.models import Transaction, BankAccount
from users.models import UserProfile, UserDocument
from providers.handlers import (
    # Payment handlers
    handle_payment_success,
    handle_payment_failure,
    handle_payment_refund,
    # Wallet handlers
    handle_wallet_deposit,
    handle_wallet_withdrawal,
    # Bank handlers
    handle_bank_transfer,
    handle_bank_statement,
    # KYC handlers
    handle_kyc_verification,
    handle_kyc_document,
)

User = get_user_model()

class PaymentHandlersTest(TestCase):
    """Test cases for payment handlers."""
    
    def setUp(self):
        """Set up test data."""
        # Create test transaction
        self.transaction = Transaction.objects.create(
            type="payment",
            status="pending",
            amount=100,
            currency="USD",
            reference="test_tx",
        )
        
        self.payment_data = {
            "transaction_id": "test_tx",
            "amount": 100,
            "currency": "USD",
            "status": "success",
        }
    
    def test_payment_success(self):
        """Test payment success handler."""
        result = handle_payment_success(self.payment_data)
        
        self.assertTrue(result)
        
        # Check transaction status
        self.transaction.refresh_from_db()
        self.assertEqual(self.transaction.status, "completed")
        self.assertEqual(
            self.transaction.metadata["transaction_id"],
            "test_tx"
        )
    
    def test_payment_failure(self):
        """Test payment failure handler."""
        self.payment_data.update({
            "status": "failed",
            "error": "Insufficient funds",
        })
        
        result = handle_payment_failure(self.payment_data)
        
        self.assertTrue(result)
        
        # Check transaction status
        self.transaction.refresh_from_db()
        self.assertEqual(self.transaction.status, "failed")
        self.assertEqual(
            self.transaction.error_message,
            "Insufficient funds"
        )
    
    def test_payment_refund(self):
        """Test payment refund handler."""
        refund_data = {
            "refund_id": "test_refund",
            "transaction_id": "test_tx",
            "amount": 50,
            "currency": "USD",
        }
        
        result = handle_payment_refund(refund_data)
        
        self.assertTrue(result)
        
        # Check refund transaction
        refund = Transaction.objects.get(reference="test_refund")
        self.assertEqual(refund.type, "refund")
        self.assertEqual(refund.status, "completed")
        self.assertEqual(refund.amount, 50)
        self.assertEqual(refund.parent_reference, "test_tx")

class WalletHandlersTest(TestCase):
    """Test cases for wallet handlers."""
    
    def setUp(self):
        """Set up test data."""
        # Create test account
        self.account = BankAccount.objects.create(
            wallet_id="test_wallet",
            balance=1000,
            currency="USD",
        )
        
        self.wallet_data = {
            "wallet_id": "test_wallet",
            "amount": 100,
            "currency": "USD",
        }
    
    def test_wallet_deposit(self):
        """Test wallet deposit handler."""
        self.wallet_data.update({
            "deposit_id": "test_deposit",
        })
        
        result = handle_wallet_deposit(self.wallet_data)
        
        self.assertTrue(result)
        
        # Check account balance
        self.account.refresh_from_db()
        self.assertEqual(self.account.balance, 1100)
        
        # Check deposit transaction
        deposit = Transaction.objects.get(reference="test_deposit")
        self.assertEqual(deposit.type, "deposit")
        self.assertEqual(deposit.status, "completed")
        self.assertEqual(deposit.amount, 100)
    
    def test_wallet_withdrawal(self):
        """Test wallet withdrawal handler."""
        self.wallet_data.update({
            "withdrawal_id": "test_withdrawal",
        })
        
        result = handle_wallet_withdrawal(self.wallet_data)
        
        self.assertTrue(result)
        
        # Check account balance
        self.account.refresh_from_db()
        self.assertEqual(self.account.balance, 900)
        
        # Check withdrawal transaction
        withdrawal = Transaction.objects.get(reference="test_withdrawal")
        self.assertEqual(withdrawal.type, "withdrawal")
        self.assertEqual(withdrawal.status, "completed")
        self.assertEqual(withdrawal.amount, 100)

class BankHandlersTest(TestCase):
    """Test cases for bank handlers."""
    
    def setUp(self):
        """Set up test data."""
        self.bank_data = {
            "transfer_id": "test_transfer",
            "amount": 100,
            "currency": "USD",
            "source": "123456789",
            "destination": "987654321",
        }
    
    def test_bank_transfer(self):
        """Test bank transfer handler."""
        result = handle_bank_transfer(self.bank_data)
        
        self.assertTrue(result)
        
        # Check transfer transaction
        transfer = Transaction.objects.get(reference="test_transfer")
        self.assertEqual(transfer.type, "transfer")
        self.assertEqual(transfer.status, "completed")
        self.assertEqual(transfer.amount, 100)
    
    def test_bank_statement(self):
        """Test bank statement handler."""
        statement_data = {
            "entries": [
                {
                    "type": "credit",
                    "amount": 100,
                    "currency": "USD",
                    "reference": "test_credit",
                },
                {
                    "type": "debit",
                    "amount": 50,
                    "currency": "USD",
                    "reference": "test_debit",
                },
            ],
        }
        
        result = handle_bank_statement(statement_data)
        
        self.assertTrue(result)
        
        # Check statement transactions
        credit = Transaction.objects.get(reference="test_credit")
        self.assertEqual(credit.type, "credit")
        self.assertEqual(credit.amount, 100)
        
        debit = Transaction.objects.get(reference="test_debit")
        self.assertEqual(debit.type, "debit")
        self.assertEqual(debit.amount, 50)

class KYCHandlersTest(TestCase):
    """Test cases for KYC handlers."""
    
    def setUp(self):
        """Set up test data."""
        # Create test user
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass",
        )
        
        # Create user profile
        self.profile = UserProfile.objects.create(
            user=self.user,
            reference="test_user",
            kyc_status="pending",
        )
        
        self.kyc_data = {
            "user_reference": "test_user",
            "status": "verified",
            "verification_date": "2025-03-25",
            "verification_level": "full",
        }
    
    def test_kyc_verification(self):
        """Test KYC verification handler."""
        result = handle_kyc_verification(self.kyc_data)
        
        self.assertTrue(result)
        
        # Check profile status
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.kyc_status, "verified")
        self.assertEqual(
            self.profile.kyc_details["verification_level"],
            "full"
        )
    
    def test_kyc_document(self):
        """Test KYC document handler."""
        document_data = {
            "user_reference": "test_user",
            "document_type": "passport",
            "status": "accepted",
            "document_id": "test_doc",
            "expiry_date": "2030-03-25",
        }
        
        result = handle_kyc_document(document_data)
        
        self.assertTrue(result)
        
        # Check document record
        document = UserDocument.objects.get(
            user_reference="test_user"
        )
        self.assertEqual(document.type, "passport")
        self.assertEqual(document.status, "accepted")
        self.assertEqual(
            document.metadata["document_id"],
            "test_doc"
        )

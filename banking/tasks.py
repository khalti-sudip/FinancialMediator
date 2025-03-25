"""
Banking Tasks Module.

This module provides Celery tasks for:
- Transaction processing
- Account synchronization
- Balance updates
- Integration health checks
"""

from celery import shared_task
from django.utils import timezone
from django.core.cache import cache
from django.db import transaction
from django.conf import settings
import logging

from .models import BankAccount, Transaction, BankIntegration

logger = logging.getLogger(__name__)

@shared_task(
    name="banking.tasks.sync_transactions",
    bind=True,
    max_retries=3,
    default_retry_delay=300,  # 5 minutes
)
def sync_transactions(self):
    """
    Synchronize transactions with integrated banks.
    
    This task:
    1. Fetches new transactions from each bank
    2. Updates local transaction records
    3. Reconciles account balances
    
    Returns:
        dict: Synchronization summary
    """
    try:
        # Get active bank integrations
        integrations = BankIntegration.objects.filter(is_active=True)
        
        summary = {
            "total_synced": 0,
            "total_failed": 0,
            "by_bank": {},
        }
        
        # Process each integration
        for integration in integrations:
            try:
                # Initialize bank client
                client = get_bank_client(integration)
                
                # Fetch new transactions
                new_transactions = client.fetch_transactions(
                    since=integration.last_sync_at
                )
                
                # Process transactions
                processed = process_transactions(
                    integration,
                    new_transactions
                )
                
                # Update summary
                summary["total_synced"] += processed["synced"]
                summary["total_failed"] += processed["failed"]
                summary["by_bank"][integration.bank_code] = processed
                
                # Update last sync time
                integration.last_sync_at = timezone.now()
                integration.save()
                
            except Exception as e:
                logger.error(
                    f"Failed to sync {integration.bank_name}",
                    exc_info=True
                )
                summary["by_bank"][integration.bank_code] = {
                    "error": str(e)
                }
        
        return summary
        
    except Exception as e:
        logger.error("Transaction sync failed", exc_info=True)
        raise self.retry(exc=e)

@shared_task(
    name="banking.tasks.update_balances",
    bind=True,
)
def update_balances(self):
    """
    Update account balances based on completed transactions.
    
    This task:
    1. Processes completed transactions
    2. Updates account balances
    3. Validates balance consistency
    
    Returns:
        dict: Update summary
    """
    try:
        # Get accounts needing update
        accounts = BankAccount.objects.filter(is_active=True)
        
        summary = {
            "total_updated": 0,
            "total_failed": 0,
            "inconsistencies": [],
        }
        
        # Process each account
        for account in accounts:
            try:
                with transaction.atomic():
                    # Calculate new balance
                    new_balance = calculate_account_balance(account)
                    
                    # Check for inconsistencies
                    if new_balance != account.current_balance:
                        summary["inconsistencies"].append({
                            "account": account.account_number,
                            "recorded": str(account.current_balance),
                            "calculated": str(new_balance),
                        })
                    
                    # Update balance
                    account.current_balance = new_balance
                    account.save()
                    
                    summary["total_updated"] += 1
                    
            except Exception as e:
                logger.error(
                    f"Failed to update balance for {account.account_number}",
                    exc_info=True
                )
                summary["total_failed"] += 1
        
        return summary
        
    except Exception as e:
        logger.error("Balance update failed", exc_info=True)
        return None

@shared_task(name="banking.tasks.check_integration_health")
def check_integration_health():
    """
    Check health of bank integrations.
    
    This task:
    1. Tests API connectivity
    2. Validates authentication
    3. Checks rate limits
    4. Updates integration status
    
    Returns:
        dict: Health check results
    """
    try:
        # Get active integrations
        integrations = BankIntegration.objects.filter(is_active=True)
        
        results = {}
        
        # Check each integration
        for integration in integrations:
            try:
                # Initialize client
                client = get_bank_client(integration)
                
                # Perform health check
                health = client.check_health()
                
                # Update status
                results[integration.bank_code] = {
                    "status": "healthy",
                    "latency": health.get("latency"),
                    "rate_limit_remaining": health.get("rate_limit"),
                }
                
            except Exception as e:
                results[integration.bank_code] = {
                    "status": "unhealthy",
                    "error": str(e),
                }
        
        # Cache results
        cache.set(
            "integration_health",
            results,
            timeout=settings.HEALTH_CHECK_CACHE_TTL
        )
        
        return results
        
    except Exception as e:
        logger.error("Integration health check failed", exc_info=True)
        return None

def get_bank_client(integration):
    """
    Get appropriate bank client for integration.
    
    Args:
        integration: BankIntegration instance
        
    Returns:
        BankClient: Initialized bank client
    """
    # Import appropriate client class
    client_class = get_client_class(integration.integration_type)
    
    # Initialize client
    return client_class(
        base_url=integration.api_base_url,
        version=integration.api_version,
        credentials=integration.auth_credentials,
        settings=integration.settings,
    )

def process_transactions(integration, transactions):
    """
    Process new transactions from bank.
    
    Args:
        integration: BankIntegration instance
        transactions: List of transaction data
        
    Returns:
        dict: Processing summary
    """
    summary = {
        "synced": 0,
        "failed": 0,
    }
    
    for txn_data in transactions:
        try:
            with transaction.atomic():
                # Create or update transaction
                txn, created = Transaction.objects.update_or_create(
                    transaction_id=txn_data["id"],
                    defaults={
                        "amount": txn_data["amount"],
                        "currency": txn_data["currency"],
                        "status": txn_data["status"],
                        "source_account": txn_data["source"],
                        "destination_account": txn_data["destination"],
                        "description": txn_data["description"],
                        "metadata": txn_data.get("metadata", {}),
                    }
                )
                
                summary["synced"] += 1
                
        except Exception as e:
            logger.error(
                f"Failed to process transaction {txn_data['id']}",
                exc_info=True
            )
            summary["failed"] += 1
    
    return summary

def calculate_account_balance(account):
    """
    Calculate account balance from transactions.
    
    Args:
        account: BankAccount instance
        
    Returns:
        Decimal: Calculated balance
    """
    from decimal import Decimal
    
    # Get completed transactions
    completed_txns = Transaction.objects.filter(
        status="completed",
        source_account=account,
    )
    
    # Calculate balance
    balance = Decimal("0.00")
    
    for txn in completed_txns:
        if txn.transaction_type in ["deposit", "transfer"]:
            balance += txn.amount
        elif txn.transaction_type == "withdrawal":
            balance -= txn.amount
    
    return balance
